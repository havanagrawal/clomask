"""Synthesize image data along with masks using preconfigured image templates"""

import os
import json
import time
import shutil
from enum import Enum
from collections import namedtuple
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool

import numpy as np
from PIL import Image

from .shelf import Shelf

class ObjectSize(float, Enum):
    """Resize factors for different object sizes"""
    SMALL = 0.6
    MEDIUM = 0.7
    LARGE = 0.8


OBJECT_SIZES = list(ObjectSize)


PasteLocation = namedtuple("PasteLocation", ["x", "y"])


class DataSynthesizer:
    """Synthetic Dataset creator for Mask RCNN

        Arguments
        ---------
        config_path: path-like, str
            The relative/absolute path to the configuration directory
            It is expected to contain three files:
                - backgrounds.json
                - foregrounds.json
                - class_map.json

        template_path: path-like, str
            The relative/absolute path to the template image directory
            It is expected to have the following directories
                - foregrounds
                - backgrounds
            The backgrounds directory itself must have directories named by
            categories.

        seed: int, default=None
            The seed used for the random number generation. This should be
            initialized in case replicable datasets are desired.

            NOTE: If the configuration files are modified, setting the seed will
                  NOT generate the same dataset, i.e. configuration changes
                  invalidate all prior seeds.
    """
    def __init__(self, config_path, template_path, seed=None):
        self.config_path = config_path
        self.template_path = template_path

        with open(config_path + "/backgrounds.json") as bg_conf_file:
            self.bg_conf = json.load(bg_conf_file)

        with open(config_path + "/foregrounds.json") as fg_conf_file:
            self.fg_conf = json.load(fg_conf_file)

        with open(config_path + "/class_map.json") as class_map_file:
            self.class_map = json.load(class_map_file)

        self.bg_labels = list(self.bg_conf.keys())

        self.rng = np.random.RandomState(seed)

    def _get_new_image_size(self, curr_obj_conf, obj_size, shelf_height):
        cur_height, cur_width = curr_obj_conf["height"], curr_obj_conf["width"]
        new_height = int(shelf_height * obj_size)
        new_width = int((new_height / cur_height) * cur_width)

        return (new_width, new_height)

    def _get_fg_and_conf(self, categories):
        fg_category = self.rng.choice(categories)
        fg_category_objs = list(self.fg_conf[fg_category].keys())
        fg_obj = self.rng.choice(fg_category_objs)
        obj_conf = self.fg_conf[fg_category][fg_obj]
        fg_class_id = self.class_map.get(fg_category, None)

        obj_file = self.template_path + "/foregrounds/{cat}/{obj}.png".format(cat=fg_category, obj=fg_obj)

        return obj_file, obj_conf, fg_category, fg_class_id

    def _get_bg_and_conf(self):
        bg_label = self.rng.choice(self.bg_labels)
        bg_conf = self.bg_conf[bg_label]
        bg_file = self.template_path + "/backgrounds/{}.jpg".format(bg_label)
        return bg_file, bg_conf

    def _process_shelf_region(
            self, shelf_region, shelf_no, bg_file, image_path, categories, nomask_categories, rotation_probability,
            obj_sizes_allowed, max_objs_in_pack, max_offset):
        """Target function for processing each individual shelf region"""
        bg_img = Image.open(bg_file)
        empty_fg = Image.new('RGBA', bg_img.size, color=(0, 0, 0, 0))

        # This is the starting template for individual foreground object masks
        empty_alpha_mask = Image.new('L', bg_img.size, color=0)

        # Contains all the masks for this shelf region
        shelf_alpha_mask = empty_alpha_mask.copy()
        num_obj = 0

        def within_bounds(shelf_region, x):
            return x < shelf_region.x_end

        paste_pos = PasteLocation(shelf_region.x_start, 0)

        while within_bounds(shelf_region, paste_pos.x):
            fg_file, fg_conf, fg_category, fg_id = self._get_fg_and_conf(categories + nomask_categories)

            shelf_height = shelf_region.height_at(paste_pos.x)
            obj_size = self.rng.choice(obj_sizes_allowed)
            new_size = self._get_new_image_size(fg_conf, obj_size, shelf_height)

            fg_img = Image.open(fg_file)
            fg_img = fg_img.resize(new_size, Image.LANCZOS)

            objs_in_pack = self.rng.randint(1, max_objs_in_pack + 1)

            for _ in range(objs_in_pack):
                num_obj += 1
                to_paste = fg_img

                is_rotated = self.rng.binomial(1, p=rotation_probability)
                if is_rotated:
                    to_paste = to_paste.rotate(self.rng.randint(-90, 90), expand=1)

                width, height = to_paste.size

                bottom_shelf_pos = int(shelf_region.bottom_line.y_at(paste_pos.x))
                paste_pos = PasteLocation(paste_pos.x, bottom_shelf_pos - height)

                if not within_bounds(shelf_region, paste_pos.x + width):
                    return {"img": bg_img, "mask": shelf_alpha_mask}

                new_fg = empty_fg.copy()
                new_fg.paste(to_paste, paste_pos)

                alpha_mask = to_paste.getchannel(3)
                new_alpha_mask = empty_alpha_mask.copy()

                new_alpha_mask.paste(alpha_mask, paste_pos)
                shelf_alpha_mask.paste(alpha_mask, paste_pos)

                obj_num_str = str(num_obj).rjust(3, "0")
                image_filepath = image_path + "/train_mask/mask_{}_{}${}.png".format(shelf_no, obj_num_str, fg_id)

                if fg_category not in nomask_categories:
                    new_alpha_mask.save(image_filepath)

                bg_img = Image.composite(new_fg, bg_img, new_alpha_mask)
                x_offset = self.rng.randint(1, max_offset)
                paste_pos = PasteLocation(paste_pos.x + width + x_offset, bottom_shelf_pos)

                if not within_bounds(shelf_region, paste_pos.x):
                    break

        return {"img": bg_img, "mask": shelf_alpha_mask}

    def generate_synthetic_dataset(
            self, n, output_dir, categories=None, nomask_categories=None, rotation_probability=0.1, max_x_offset=1,
            obj_sizes_allowed=None, max_objs_in_pack=3, skip_shelf_probability=0, verbose=True):
        """Synthesize an image dataset

            Arguments
            ---------
            n: int
                the number of images to be generated.

            output_dir: path-like, str
                The output directory to which the generated dataset is written.

            categories: list, default: ["bottles"]
                a list of categories from which objects will be selected. Should
                match the keys in the foreground config file.

            nomask_categories: list, default: []
                a list of categories from which objects will be selected,
                but no masks will be generated for them. This allows us to introduce
                controllable noise into the dataset.

            rotation_probability: float, default=0.1:
                The probability of rotating an image,
                in other words, the proportion of rotated objects

            max_x_offset: int, default=1
                The maximum number of pixels present between two images.

            obj_sizes_allowed: list, default=OBJECT_SIZES
                the allowed variation in sizes for the objects.
                Use SMALL, MEDIUM and LARGE from the ObjectSize enum

            max_objs_in_pack: int, default=3
                Maximum number of objects in a pack (appearing consecutively)

            skip_shelf_probability: float, [0, 1], default=0
                The probability of skipping a shelf while placing items

            verbose: bool, default=False
                If true, print a message each time an image is generated.

        Return
        ------
        save_path: path-like, str
            The directory to which all the generated data was written.
        """
        if categories is None:
            categories = ["bottles"]

        if nomask_categories is None:
            nomask_categories = []

        if obj_sizes_allowed is None:
            obj_sizes_allowed = OBJECT_SIZES

        timestamp = time.strftime("%Y_%m_%d_%H_%M_%S", time.gmtime())
        dataset_name = "synth_data_{}".format(timestamp)
        save_path = os.path.join(output_dir, dataset_name)
        os.makedirs(save_path)
        with open(save_path + "/id_map.json", "w") as id_file:
            id_class_map = {v:k for k, v in self.class_map.items()}
            json.dump(id_class_map, id_file, indent=4)

        for i in range(n):
            image_name = "image_{}_{}".format(i, timestamp)
            image_path = save_path + "/{}".format(image_name)
            os.makedirs(image_path + "/train_image")
            os.makedirs(image_path + "/train_mask")

            verbose and print("Generating image {i} of {n}".format(i=i+1, n=n))
            bg_file, bg_conf = self._get_bg_and_conf()
            shelf = Shelf(config=bg_conf)

            args = {
                "bg_file": bg_file,
                "image_path": image_path,
                "categories": categories,
                "nomask_categories": nomask_categories,
                "rotation_probability": rotation_probability,
                "obj_sizes_allowed": obj_sizes_allowed,
                "max_objs_in_pack": max_objs_in_pack,
                "max_offset": max_x_offset
            }

            shelf_masks = []
            for k, shelf_region in enumerate(shelf.regions):
                skip_shelf = self.rng.binomial(1, p=skip_shelf_probability)
                # Never skip the first shelf
                if k != 0 and skip_shelf:
                    continue
                shelf_n_mask = self._process_shelf_region(shelf_region, k, **args)
                shelf_masks.append(shelf_n_mask)


            bg_img = None
            for shelf_n_mask in shelf_masks:
                shelf_img = shelf_n_mask["img"]
                shelf_mask = shelf_n_mask["mask"]
                if bg_img is None:
                    bg_img = shelf_img.copy()
                else:
                    bg_img = Image.composite(shelf_img, bg_img, shelf_mask)

            bg_img.save(image_path + "/train_image/{}.png".format(image_name))

        print("Done.")
        return save_path


class ParallelDataSynthesizer(DataSynthesizer):
    """Parallelized Synthetic Dataset creator for Mask RCNN

        Arguments
        ---------
        config_path: path-like, str
            The relative/absolute path to the configuration directory
            It is expected to contain three files:
                - backgrounds.json
                - foregrounds.json
                - class_map.json

        template_path: path-like, str
            The relative/absolute path to the template image directory
            It is expected to have the following directories
                - foregrounds
                - backgrounds
            The backgrounds directory itself must have directories named by
            categories.

        seed: int, default=None
            The seed used for the random number generation. This should be
            initialized in case replicable datasets are desired.

            NOTE: If the configuration files are modified, setting the seed will
                  NOT generate the same dataset, i.e. configuration changes
                  invalidate all prior seeds.

        n_jobs: int, default: # of cpus
            The number of threads to use
    """
    def __init__(self, config_path, template_path, seed=None, n_jobs=None):
        super(ParallelDataSynthesizer, self).__init__(config_path, template_path, seed)
        self.seed = seed
        self.n_jobs = n_jobs or cpu_count()

    def generate_synthetic_dataset(
            self, n, output_dir, categories=None, nomask_categories=None, rotation_probability=0.1, max_x_offset=1,
            obj_sizes_allowed=None, max_objs_in_pack=3, skip_shelf_probability=0, verbose=True):
        """Synthesize an image dataset

            Arguments
            ---------
            n: int
                the number of images to be generated.

            output_dir: path-like, str
                The output directory to which the generated dataset is written.

            categories: list, default: ["bottles"]
                a list of categories from which objects will be selected. Should
                match the keys in the foreground config file.

            nomask_categories: list, default: []
                a list of categories from which objects will be selected,
                but no masks will be generated for them. This allows us to introduce
                controllable noise into the dataset.

            rotation_probability: float, default=0.1:
                The probability of rotating an image,
                in other words, the proportion of rotated objects

            max_x_offset: int, default=1
                The maximum number of pixels present between two images.

            obj_sizes_allowed: list, default=OBJECT_SIZES
                the allowed variation in sizes for the objects.
                Use SMALL, MEDIUM and LARGE from the ObjectSize enum

            max_objs_in_pack: int, default=3
                Maximum number of objects in a pack (appearing consecutively)

            skip_shelf_probability: float, [0, 1], default=0
                The probability of skipping a shelf while placing items

            verbose: bool, default: False
                If true, print a message each time an image is generated.

        Return
        ------
        results: list[pool.AsyncResult]
            A list of AsyncResult, where each result contains the output directory
            to which the data was written.

            Note: Consider using the staticmethod "merge_results" that
            creates a single usable dataset
        """
        rng = np.random.RandomState(self.seed)
        seeds = rng.choice(10*n, size=self.n_jobs, replace=False)
        pool = Pool(self.n_jobs)
        results = []
        n = n // self.n_jobs
        for seed in seeds:
            synth = DataSynthesizer(self.config_path, self.template_path, seed=seed)
            res = pool.apply_async(
                synth.generate_synthetic_dataset,
                args=(
                    n, output_dir, categories, nomask_categories,
                    rotation_probability, max_x_offset, obj_sizes_allowed,
                    max_objs_in_pack, skip_shelf_probability, verbose
                )
            )
            results.append(res)

            # Ugly hack: Prevent the same timestamp being used for the directory name
            time.sleep(1)

        return results

    @staticmethod
    def merge(results, output_dir):
        """Merge AsyncResults from different DataSynthesizer runs.

        Note that the id_map.json file must be identical for all datasets.
        If it is not, the resulting id_map.json in the final dataset MUST be
        inspected for correctness

        Arguments
        ---------
        results: list[AsyncResult]
            A list of AsyncResult, where each result contains the output directory
            to which the data was written.

        output_dir: path-like, str
            The directory to which the final dataset must be written.
        """
        save_paths = [res.get() for res in results]

        timestamp = time.strftime("%Y_%m_%d_%H_%M_%S", time.gmtime())
        dataset_name = "synth_data_{}".format(timestamp)
        save_path = os.path.join(output_dir, dataset_name)

        os.makedirs(save_path)

        for path in save_paths:
            for f in os.listdir(path):
                filepath = path + "/" + f
                try:
                    shutil.move(filepath, save_path)
                except Exception as e:
                    print("Encountered error {}. Continuing.".format(e))
            shutil.rmtree(path)

        return save_path
