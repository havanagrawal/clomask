"""
Module to manage the addition, deletion and modification of foreground
and background images inside the img_templates folder. The configurations
will be stored in the files in config folder.
"""

import os
import json


class TemplateManager:
    def __init__(self, config_path):
        self.config_path = config_path

    def add_foreground_category(self, category):
        """
        Adding new foreground category.
        """
        config_path = self.config_path + "foregrounds.json"
        with open(config_path, "r") as conf_file:
            config = json.load(conf_file)
        if category not in config:
            config[category] = {}
        else:
            raise Exception((
                "Category {category} present in foreground configuration."
            ).format(category=category))

        with open(config_path, "w") as conf_file:
            json.dump(config, conf_file, indent=4)
        print("New foreground category {} added.".format(category))

    def del_foreground_category(self, category):
        """
        Removing foreground category.
        """
        config_path = self.config_path + "foregrounds.json"
        with open(config_path, "r") as conf_file:
            config = json.load(conf_file)
        if category in config:
            config.pop(category)
        else:
            raise Exception((
                "Category {} not present in foreground configuration."
            ).format(category))

        with open(config_path, "w") as conf_file:
            json.dump(config, conf_file, indent=4)
        print("Removed category {} and all associated objects.".format(
            category))

    def _add_foreground_template(self, label, config, args):

        category = args["category"]
        if category in config:
            if label not in config[category]:
                config[category][label] = {}
                config[category][label]["height"] = args["height"]
                config[category][label]["width"] = args["width"]
            else:
                raise Exception((
                    "Foreground object already exists in {category}."
                    " If you want to modify an existing configuration use "
                    "the function `modify_template`").format(
                        category=category))
        else:
            raise Exception((
                "Category {category} not found in foreground configuration."
                " If you are adding a new category object please use "
                "the function `add_foreground_category`").format(
                    category=category))
        return config

    def _add_background_template(self, label, config, args):

        if label not in config:
            config[label] = {}
            config[label]["shelf_region"] = args["shelf_region"]
            config[label]["shelf_ht"] = args["shelf_ht"]
            config[label]["num_shelves"] = args["num_shelves"]
            config[label]["shelf_y_positions"] = \
                args["shelf_y_positions"]
        else:
            raise Exception(
                "Background object with same label already exists."
                " If you want to modify an existing configuration use "
                "the function `modify_template`")
        return config

    def add_template(self, label, template_type, **kwargs):
        """
        Adding the template object to the config file.
        """
        if template_type == "background":
            config_path = self.config_path + "backgrounds.json"
            with open(config_path, "r") as conf_file:
                config = json.load(conf_file)
            new_config = self._add_background_template(label, config, kwargs)

        elif template_type == "foreground":
            config_path = self.config_path + "foregrounds.json"
            with open(config_path, "r") as conf_file:
                config = json.load(conf_file)
            new_config = self._add_foreground_template(label, config, kwargs)

        with open(config_path, "w") as conf_file:
            json.dump(new_config, conf_file, indent=4)
        print(
            "New {type} object {label} configured.".format(
                type=template_type, label=label))

    def del_template(self, label, template_type, category=None):
        """
        Removing the template object from the config file.
        """
        if template_type == "background":
            config_path = self.config_path + "backgrounds.json"
            with open(config_path, "r") as conf_file:
                config = json.load(conf_file)
            if label in config:
                config.pop(label)
            else:
                raise Exception(
                    "Label {} not found.".format(label))

        elif template_type == "foreground":
            config_path = self.config_path + "foregrounds.json"
            with open(config_path, "r") as conf_file:
                config = json.load(conf_file)
            if category in config:
                if label in config[category]:
                    config[category].pop(label)
                else:
                    raise Exception(
                        "Label {} not found.".format(label))
            else:
                raise Exception(
                    "Category {} not found.".format(category))
        with open(config_path, "w") as conf_file:
            json.dump(config, conf_file, indent=4)
        print(
            "{type} object {label} removed.".format(
                type=template_type, label=label, ))

    def modify_template(self):
        pass
