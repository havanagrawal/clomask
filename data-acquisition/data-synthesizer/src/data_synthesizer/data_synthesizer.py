import json
import numpy as np
import os
from PIL import Image
import queue
import random
import time
from threading import Thread

OBJ_SIZE_MAP = {
    "s": 0.6,
    "m": 0.75,
    "l": 0.9
}


class DataSynthesizer:

    def __init__(self, config_path, template_path, data_path):
        self.config_path = config_path
        self.data_path = data_path
        self.template_path = template_path
        with open(self.config_path + "/backgrounds.json") as bg_conf_file:
            self.bg_conf = json.load(bg_conf_file)
        self.bg_labels = list(self.bg_conf.keys())
        with open(self.config_path + "/foregrounds.json") as fg_conf_file:
            self.fg_conf = json.load(fg_conf_file)

    def _get_new_image_size(
            self, curr_obj_conf, obj_sizes_allowed, shelf_ht):

        curr_fg_obj_size = np.random.choice(obj_sizes_allowed, 1)[0]
        new_obj_ht = int(shelf_ht * OBJ_SIZE_MAP[curr_fg_obj_size])
        new_obj_width = int(
            (new_obj_ht/curr_obj_conf["height"])*curr_obj_conf["width"])

        new_img_size = (new_obj_width, new_obj_ht)

        return new_img_size

    def _get_fg_and_conf(self, categories):

        curr_fg_category = np.random.choice(categories, 1)[0]
        curr_fg_category_objs = list(self.fg_conf[curr_fg_category].keys())
        curr_fg_obj = np.random.choice(curr_fg_category_objs, 1)[0]
        curr_obj_conf = self.fg_conf[curr_fg_category][curr_fg_obj]

        curr_obj_file = (
            self.template_path + "/foregrounds/{cat}/{obj}.png").format(
                cat=curr_fg_category, obj=curr_fg_obj)

        return curr_obj_file, curr_obj_conf

    def _get_bg_and_conf(self):
        curr_bg_label = np.random.choice(self.bg_labels, 1)[0]
        curr_bg_conf = self.bg_conf[curr_bg_label]
        curr_bg_file = (
            self.template_path + "/backgrounds/{bg}.jpg").format(
                bg=curr_bg_label)
        return curr_bg_file, curr_bg_conf

    def _process_shelf(
            self, shelf, bg_conf, bg_file, image_path, categories, rot_pc,
            obj_sizes_allowed, max_objs_in_pack, x_offset):
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
            fg_file, fg_conf = self._get_fg_and_conf(categories)
            new_size = self._get_new_image_size(
                fg_conf, obj_sizes_allowed, shelf_ht)
            fg_img = Image.open(fg_file)
            fg_img = fg_img.resize(new_size, Image.LANCZOS)

            num_instances = np.random.choice(max_objs_in_pack, 1)[0]

            for _ in range(num_instances):
                num_obj += 1
                is_rotated = np.random.binomial(1, p=rot_pc)
                to_paste = fg_img
                if is_rotated:
                    to_paste = fg_img.rotate(
                        np.random.randint(-90, 90), expand=1)

                img_size = to_paste.size
                alpha_mask = to_paste.getchannel(3)
                paste_pos = (paste_pos[0],
                             shelf_positions[shelf]-img_size[1])

                new_fg = empty_fg.copy()
                new_fg.paste(to_paste, paste_pos)

                new_alpha_mask = empty_alpha_mask.copy()
                new_alpha_mask.paste(alpha_mask, paste_pos)

                shelf_alpha_mask.paste(alpha_mask, paste_pos)

                new_alpha_mask.save(
                    image_path + "/train_mask/mask_{}{}.png".format(
                        shelf, num_obj))
                bg_img = Image.composite(new_fg, bg_img,
                                         new_alpha_mask)
                paste_pos = (paste_pos[0]+img_size[0]+x_offset,
                             shelf_positions[shelf])

                if paste_pos[0] >= x_end:
                    break

        return {"img": bg_img, "mask": shelf_alpha_mask}

    def generate_synthetic_dataset(
            self, n, categories=["bottles"], rot_pc=0.1, x_offset=1,
            obj_sizes_allowed=["s", "m", "l"], max_objs_in_pack=3):
        """
            The synthesizer takes the following parameters:
            n: integer specifying the number of images to be generated.

            categories (default: ["bottles"]): An array specifying the 
                categories from which objects will be selected. Should 
                match the keys in the foreground config file.

            rot_pc (default=0.1): Proportion of rotated images

            x_offset (default=1 px): Integer value specifying the number of
                pixels present between two images.

            obj_sizes_allowed (default=[["s", "m", "l"]]): An array specifying
                the allowed variation in sizes for the objects.
                (s=small, m=medium and l=large)

            max_objs_in_pack (default=3): Max number of objects in a pack 
                (appearing consecutively).
        """

        timestamp = time.strftime("%Y_%m_%d_%H_%M_%S", time.gmtime())
        dataset_name = "synth_data_{}".format(timestamp)
        save_path = self.data_path + dataset_name
        os.mkdir(save_path)

        for i in range(n):
            image_name = "image_{}_{}".format(i, timestamp)
            image_path = save_path + "/{}".format(image_name)
            os.mkdir(image_path)
            os.mkdir(image_path + "/train_image")
            os.mkdir(image_path + "/train_mask")

            print("Generating image {i} of {n}".format(i=i+1, n=n))
            bg_file, bg_conf = self._get_bg_and_conf()
            num_shelves = bg_conf["num_shelves"]

            que = queue.Queue()
            threads = []
            args = {
                "bg_conf": bg_conf,
                "bg_file": bg_file,
                "image_path": image_path,
                "categories": categories,
                "rot_pc": rot_pc,
                "obj_sizes_allowed": obj_sizes_allowed,
                "max_objs_in_pack": max_objs_in_pack,
                "x_offset": x_offset
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
                    bg_img = Image.composite(shelf_img, bg_img,
                                             shelf_mask)
            bg_img.save(
                image_path + "/train_image/{}.png".format(image_name))

        print("Done.")
