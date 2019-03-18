"""Mask RCNN model API

    This module exports a base implementation for Mask RCNN based models
"""

import os

import skimage.io

from . import Model
from ..imutils import post_process

# Import Mask RCNN
import visualize
import model as modellib

class MaskRCNNModel(Model):
    """Base implementation for MaskRCNN based models"""
    def __init__(self, name, config, model_dir, items=None):
        """Initialize the Coco Model

        Arguments
        ---------
        items: list-like
            Only items from this list will be annotated, and the rest will be discarded.
            If not provided, all masks are generated.
        """
        super().__init__(name)

        # Create model object in inference mode.
        self.model = modellib.MaskRCNN(
            mode="inference",
            model_dir=model_dir,
            config=config
        )

        self.items = list(items)
        self.class_names = items

    def load(self, filepath=None):
        self.model.load_weights(filepath, by_name=True)

    def create_mask(self, filepath, output_dir):
        output_path = output_dir + "/" + os.path.basename(filepath)
        image = skimage.io.imread(filepath)
        print(image.shape)

        # Run detection
        results = self.model.detect([image], verbose=1)

        # Visualize results
        r = results[0]

        visualize.display_instances(image, r['rois'], r['masks'], r['class_ids'],
                                    self.class_names, r['scores'],
                                    show_label=False, show_bbox=False,
                                    figsize=(8, 8), savepath=output_path)

        out = skimage.io.imread(output_path)
        skimage.io.imsave("tmp.jpg", out)
        out = post_process(out)
        skimage.io.imsave(output_path, out)

        return output_path
