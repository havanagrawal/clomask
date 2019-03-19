"""Mask RCNN model API

    This module exports a base implementation for Mask RCNN based models
"""

import os
from shutil import copyfile

import skimage.io

from . import Model
from ..imutils import post_process

# Import Mask RCNN
import visualize
import model as modellib

class MaskRCNNModel(Model):
    """Base implementation for MaskRCNN based models"""
    def __init__(self, name, config, model_dir, class_names):
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

        self.class_names = class_names

    def load(self, filepath=None):
        self.model.load_weights(filepath, by_name=True)

    def create_mask(self, filepath, output_dir, generate_per_class=False):
        return self.create_masks([filepath], output_dir, generate_per_class)

    def create_masks(self, filepaths, output_dir, generate_per_class=False):
        """Create and persist masks for each image from the filepaths

            Arguments
            ---------
            filepaths: iterable[str]
                An iterable of path-like objects or strings representing filepaths

            output_dir: str, path-like
                The output directory to which the masks will be written

            generate_per_class: bool, default=False
                Whether additional images should be generated for each class.
                Thus if there are k classes, k + 1 images will be generated:
                    1 for each class (k)
                    1 with all classes
        """
        images = [skimage.io.imread(filepath) for filepath in filepaths]

        os.makedirs(output_dir + "/og", exist_ok=True)
        originals = [output_dir + "/og/" + os.path.basename(f) for f in filepaths]
        for src, dest in zip(filepaths, originals):
            copyfile(src, os.path.abspath(dest))

        # Run detection
        results = self.model.detect(images, verbose=1)

        output_paths = originals

        # Visualize results
        for r, image, filepath in zip(results, images, filepaths):
            file_basename = os.path.basename(filepath)

            class_ids = ['all']
            if generate_per_class:
                class_ids.extend(set(r['class_ids']))

            class_ids = set(class_ids)

            for class_id in class_ids:
                res = self._filter_for_class_id(r, class_id)
                output_path = output_dir + "/" + str(class_id) + "/" + file_basename
                self._save_masks(image, res, output_path)
                output_paths.append(output_path)

        return output_paths

    def _save_masks(self, image, res, output_path):
        captions = ["{:.3f}".format(score) for score in res['scores']]
        visualize.display_instances(image, res['rois'], res['masks'], res['class_ids'],
                                    self.class_names, res['scores'],
                                    show_label=True, show_bbox=False,
                                    captions=captions,
                                    figsize=(8, 8), savepath=output_path)
        out = post_process(skimage.io.imread(output_path))
        skimage.io.imsave(output_path, out)

    def _filter_for_class_id(self, result, class_id=None):
        if class_id == 'all':
            return result

        filter = result['class_ids'] == class_id
        return {
            'rois': result['rois'][filter],
            'masks': result['masks'][..., filter],
            'class_ids': result['class_ids'][filter],
            'scores': result['scores'][filter],
        }
