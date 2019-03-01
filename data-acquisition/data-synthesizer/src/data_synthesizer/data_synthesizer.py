"""Synthesize image data along with masks using preconfigured image templates"""

import os
import json
import time
import queue
import random
from enum import Enum
from threading import Thread

import numpy as np
from PIL import Image


class ObjectSize(float, Enum):
    SMALL = 0.6
    MEDIUM = 0.75
    LARGE = 0.9


OBJECT_SIZES = list(ObjectSize)


class DataSynthesizer:

    def __init__(self, config_path, template_path, data_path):
        self.config_path = config_path
        self.data_path = data_path
        self.template_path = template_path

        with open(self.config_path + "/backgrounds.json") as bg_conf_file:
            self.bg_conf = json.load(bg_conf_file)

        with open(self.config_path + "/foregrounds.json") as fg_conf_file:
            self.fg_conf = json.load(fg_conf_file)

        with open(self.config_path + "/class_map.json") as class_map_file:
            self.class_map = json.load(class_map_file)

        self.bg_labels = list(self.bg_conf.keys())

    def _get_new_image_size(self, curr_obj_conf, obj_size, shelf_height):
        cur_height, cur_width = curr_obj_conf["height"], curr_obj_conf["width"]
        new_height = int(shelf_height * obj_size)
        new_width = int((new_height / cur_height) * cur_width)

        return (new_width, new_height)

    def _get_fg_and_conf(self, categories):
        curr_fg_category = random.choice(categories)
        curr_fg_category_objs = list(self.fg_conf[curr_fg_category].keys())
        curr_fg_obj = random.choice(curr_fg_category_objs)
        curr_obj_conf = self.fg_conf[curr_fg_category][curr_fg_obj]
        fg_class_id = self.class_map[curr_fg_category]

        curr_obj_file = (
            self.template_path + "/foregrounds/{cat}/{obj}.png").format(
                cat=curr_fg_category, obj=curr_fg_obj)

        return curr_obj_file, curr_obj_conf, fg_class_id

    def _get_bg_and_conf(self):
        curr_bg_label = random.choice(self.bg_labels)
        curr_bg_conf = self.bg_conf[curr_bg_label]
        curr_bg_file = (
            self.template_path + "/backgrounds/{bg}.jpg").format(
                bg=curr_bg_label)
        return curr_bg_file, curr_bg_conf

    def _process_shelf(
            self, shelf, bg_conf, bg_file, image_path, categories, rot_pc,
            obj_sizes_allowed, max_objs_in_pack, max_offset):
        """
        Target function for parallely processing each individual shelf.
        """
        shelf_region = bg_conf["shelf_region"]
        x_start, x_end = shelf_region[0][0], shelf_region[1][0]
        shelf_positions = bg_conf["shelf_y_positions"]
        shelf_ht = bg_conf["shelf_ht"]

        bg_img = Image.open(bg_file)
        empty_fg = Image.new('RGBA', bg_img.size, color=(0, 0, 0, 0))
        empty_alpha_mask = Image.new('L', bg_img.size, color=0)
        shelf_alpha_mask = empty_alpha_mask.copy()
        num_obj = 0

        paste_pos = (x_start, 0)
        while paste_pos[0] < x_end:
            fg_file, fg_conf, fg_id = self._get_fg_and_conf(categories)
            obj_size = random.choice(obj_sizes_allowed)
            new_size = self._get_new_image_size(fg_conf, obj_size, shelf_ht)
            fg_img = Image.open(fg_file)
            fg_img = fg_img.resize(new_size, Image.LANCZOS)

            for _ in range(max_objs_in_pack):
                num_obj += 1
                is_rotated = np.random.binomial(1, p=rot_pc)
                to_paste = fg_img
                if is_rotated:
                    to_paste = fg_img.rotate(
                        np.random.randint(-90, 90), expand=1)

                img_size = to_paste.size
                alpha_mask = to_paste.getchannel(3)
                paste_pos = (paste_pos[0], shelf_positions[shelf]-img_size[1])

                if paste_pos[0] + img_size[0] > x_end:
                    paste_pos = (paste_pos[0] + img_size[0], shelf_positions[shelf])
                    break

                new_fg = empty_fg.copy()
                new_fg.paste(to_paste, paste_pos)

                new_alpha_mask = empty_alpha_mask.copy()
                new_alpha_mask.paste(alpha_mask, paste_pos)

                shelf_alpha_mask.paste(alpha_mask, paste_pos)

                image_filepath = image_path + "/train_mask/mask_{}{}${}.png".format(shelf, num_obj, fg_id)
                new_alpha_mask.save(image_filepath)

                bg_img = Image.composite(new_fg, bg_img,
                                         new_alpha_mask)
                x_offset = np.random.randint(1, max_offset, 1)[0]
                paste_pos = (paste_pos[0]+img_size[0]+x_offset,
                             shelf_positions[shelf])

                if paste_pos[0] >= x_end:
                    break

        return {"img": bg_img, "mask": shelf_alpha_mask}

    def generate_synthetic_dataset(
            self, n, categories=["bottles"], rot_pc=[0.1], x_offset=1,
            obj_sizes_allowed=OBJECT_SIZES, max_objs_in_pack=3):
        """
            Synthesize an image dataset

            Arguments
            ---------
            n: int
                the number of images to be generated.

            categories: list, default: ["bottles"]
                a list of categories from which objects will be selected. Should
                match the keys in the foreground config file.

            rot_pc: list, default=[0.1]:
                Proportion of rotated images

            x_offset: int, default=1
                number of pixels present between two images.

            obj_sizes_allowed: list, default=OBJECT_SIZES
                the allowed variation in sizes for the objects.
                (s=small, m=medium and l=large)

            max_objs_in_pack: int, default=3
                Maximum number of objects in a pack (appearing consecutively).
        """

        timestamp = time.strftime("%Y_%m_%d_%H_%M_%S", time.gmtime())
        dataset_name = "synth_data_{}".format(timestamp)
        save_path = self.data_path + dataset_name
        os.mkdir(save_path)
        with open(save_path + "/id_map.json", "w") as id_file:
            id_class_map = {v:k for k, v in self.class_map.items()}
            json.dump(id_class_map, id_file, indent=4)

        for i in range(n):
            image_name = "image_{}_{}".format(i, timestamp)
            image_path = save_path + "/{}".format(image_name)
            os.mkdir(image_path)
            os.mkdir(image_path + "/train_image")
            os.mkdir(image_path + "/train_mask")

            print("Generating image {i} of {n}".format(i=i+1, n=n))
            bg_file, bg_conf = self._get_bg_and_conf()
            num_shelves = bg_conf["num_shelves"]
            rot = random.choice(rot_pc)
            que = queue.Queue()
            threads = []
            args = {
                "bg_conf": bg_conf,
                "bg_file": bg_file,
                "image_path": image_path,
                "categories": categories,
                "rot_pc": rot,
                "obj_sizes_allowed": obj_sizes_allowed,
                "max_objs_in_pack": max_objs_in_pack,
                "max_offset": x_offset
            }

            for shelf in range(num_shelves):
                t = Thread(
                    target=lambda q, shelf, args: q.put(
                        self._process_shelf(shelf, **args)),
                    args=(que, shelf, args))
                threads.append(t)

            for t in threads:
                t.start()
            for t in threads:
                t.join()

            bg_img = None
            while not que.empty():
                shelf_n_mask = que.get()
                shelf_img = shelf_n_mask["img"]
                shelf_mask = shelf_n_mask["mask"]
                if bg_img is None:
                    bg_img = shelf_img.copy()
                else:
                    bg_img = Image.composite(shelf_img, bg_img, shelf_mask)
            bg_img.save(
                image_path + "/train_image/{}.png".format(image_name))

        print("Done.")
