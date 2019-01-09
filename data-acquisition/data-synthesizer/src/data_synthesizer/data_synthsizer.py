import os
import random
import numpy as np
from PIL import Image
import json
import time

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
        with open(self.config_path + "/foregrounds.json") as fr_conf_file:
            self.fr_conf = json.load(fr_conf_file)

    def _get_new_image_size(
            self, curr_obj_conf, obj_sizes_allowed, shelf_ht):

        curr_fr_obj_size = np.random.choice(obj_sizes_allowed, 1)[0]
        new_obj_ht = int(shelf_ht * OBJ_SIZE_MAP[curr_fr_obj_size])
        new_obj_width = int(
            (new_obj_ht/curr_obj_conf["height"])*curr_obj_conf["width"])

        new_img_size = (new_obj_width, new_obj_ht)

        return new_img_size

    def _get_fr_and_conf(self, categories):

        curr_fr_category = np.random.choice(categories, 1)[0]
        curr_fr_category_objs = list(self.fr_conf[curr_fr_category].keys())
        curr_fr_obj = np.random.choice(curr_fr_category_objs, 1)[0]
        curr_obj_conf = self.fr_conf[curr_fr_category][curr_fr_obj]

        curr_obj_file = (
            self.template_path + "/foregrounds/{cat}/{obj}.png").format(
                cat=curr_fr_category, obj=curr_fr_obj)

        return curr_obj_file, curr_obj_conf

    def _get_bg_and_conf(self):
        curr_bg_label = np.random.choice(self.bg_labels, 1)[0]
        curr_bg_conf = self.bg_conf[curr_bg_label]
        curr_bg_file = (
            self.template_path + "/backgrounds/{bg}.jpg").format(
                bg=curr_bg_label)
        return curr_bg_file, curr_bg_conf

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
            shelf_region = bg_conf["shelf_region"]
            x_start, x_end = shelf_region[0][0], shelf_region[1][0]
            shelf_positions = bg_conf["shelf_y_positions"]
            shelf_ht = bg_conf["shelf_ht"]

            bg_img = Image.open(bg_file)
            empty_fr = Image.new('RGBA', bg_img.size, color=(0, 0, 0, 0))
            empty_alpha_mask = Image.new('L', bg_img.size, color=0)
            num_obj = 0
            for shelf in range(num_shelves):
                paste_pos = (x_start, 0)
                while paste_pos[0] < x_end:

                    fr_file, fr_conf = self._get_fr_and_conf(categories)
                    new_size = self._get_new_image_size(
                        fr_conf, obj_sizes_allowed, shelf_ht)
                    fr_img = Image.open(fr_file)
                    fr_img = fr_img.resize(new_size, Image.LANCZOS)

                    num_instances = np.random.choice(max_objs_in_pack, 1)[0]

                    for instance in range(num_instances):
                        num_obj += 1
                        is_rotated = np.random.binomial(1, p=rot_pc)
                        if is_rotated:
                            to_paste = fr_img.rotate(
                                np.random.randint(-90, 90), expand=1)
                        else:
                            to_paste = fr_img

                        img_size = to_paste.size
                        alpha_mask = to_paste.getchannel(3)
                        paste_pos = (paste_pos[0],
                                     shelf_positions[shelf]-img_size[1])

                        new_fg = empty_fr.copy()
                        new_fg.paste(to_paste, paste_pos)

                        new_alpha_mask = empty_alpha_mask.copy()
                        new_alpha_mask.paste(alpha_mask, paste_pos)

                        new_alpha_mask.save(
                            image_path + "/train_mask/mask_{}.jpg".format(
                                num_obj))

                        bg_img = Image.composite(new_fg, bg_img,
                                                 new_alpha_mask)
                        paste_pos = (paste_pos[0]+img_size[0]+x_offset,
                                     shelf_positions[shelf])

                        if paste_pos[0] >= x_end:
                            break

            bg_img.save(image_path+ "/train_image/{}.jpg".format(image_name))

        print("Done.")

            

