"""
Module to manage the addition, deletion and modification of foreground
and background images inside the img_templates folder. The configurations
will be stored in the files in config folder.
"""
import json


class ConfigIO:
    """Thin wrapper around JSON configuration management"""
    def __init__(self, config_path):
        self.config_path = config_path

    def read(self):
        with open(self.config_path, "r") as conf_file:
            return json.load(conf_file)

    def write(self, config):
        with open(self.config_path, "w") as conf_file:
            json.dump(config, conf_file, indent=2)


class TemplateManager:
    """Simple class to manage the foreground and background configuration files

        While you can always edit the JSON files by hand, this class avoids
        common errors that are prone to such manual editing.

        Arguments
        ---------
        config_path: path-like, str
            The configuration directory that contains the foregrounds.json
            and backgrounds.json files
    """
    def __init__(self, config_path):
        self.config_path = config_path

        fg_config = self.config_path + "foregrounds.json"
        bg_config = self.config_path + "backgrounds.json"

        self.fg_config_io = ConfigIO(fg_config)
        self.bg_config_io = ConfigIO(bg_config)

    def add_foreground_category(self, category):
        """Add a new foreground category"""
        config = self.fg_config_io.read()
        if category in config:
            raise KeyError((
                "Category {category} present in foreground configuration."
            ).format(category=category))

        config[category] = {}

        self.fg_config_io.write(config)
        print("New foreground category {} added.".format(category))

    def delete_foreground_category(self, category):
        """Delete a foreground category from the configuration"""
        config = self.fg_config_io.read()

        if category not in config:
            raise KeyError((
                "Category {} not present in foreground configuration."
            ).format(category))

        config.pop(category)

        self.fg_config_io.write(config)

        print("Removed category {} and all associated objects.".format(category))

    def _add_foreground_template(self, config, category, label, args):
        if category not in config:
            raise KeyError((
                "Category {category} not found in foreground configuration."
                " If you are adding a new category object please use "
                "the function `add_foreground_category`").format(
                    category=category))

        if label in config[category]:
            raise KeyError((
                "Foreground object already exists in {category}.").format(
                    category=category))

        config[category][label] = dict(args)

        return config

    def add_background_template(self, label, args):
        config = self.bg_config_io.read()
        if label in config:
            raise KeyError("Background object with same label already exists.")

        config[label] = dict(args)

        self.bg_config_io.write(config)
        print("New background object {label} configured.".format(label=label))

    def delete_background_template(self, label):
        config = self.bg_config_io.read()
        config.pop(label)
        self.bg_config_io.write(config)
        print("Background object {label} removed.".format(label=label))

    def add_foreground_template(self, category, label, args):
        config = self.fg_config_io.read()
        new_config = self._add_foreground_template(config, category, label, args)
        self.fg_config_io.write(new_config)
        print("New foreground object {label} configured.".format(label=label))

    def delete_foreground_template(self, label, category=None):
        config = self.fg_config_io.read()
        if category not in config:
            raise KeyError("Category {} not found.".format(category))

        if label not in config[category]:
            raise KeyError("Label {} not found.".format(label))

        config[category].pop(label)

        self.fg_config_io.write(config)

        print("Foreground object {label} removed.".format(label=label))
