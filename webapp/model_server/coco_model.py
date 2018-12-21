import os
import sys
import random
import math
from shutil import copyfile

import numpy as np
import skimage.io
import matplotlib
import matplotlib.pyplot as plt

from model_api import Model
from imutils import post_process

# Root directory of the project
ROOT_DIR = os.path.abspath("Mask_RCNN")

# Import Mask RCNN
sys.path.append(ROOT_DIR)  # To find local version of the library
from mrcnn import utils
import mrcnn.model as modellib
from mrcnn import visualize

# Import COCO config
sys.path.append(os.path.join(ROOT_DIR, "samples/coco/"))  # To find local version
import coco

# Directory to save logs and trained model
MODEL_DIR = os.path.join(ROOT_DIR, "logs")

# Local path to trained weights file
COCO_MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco.h5")

# Download COCO trained weights from Releases if needed
if not os.path.exists(COCO_MODEL_PATH):
    utils.download_trained_weights(COCO_MODEL_PATH)


class InferenceConfig(coco.CocoConfig):
    # Set batch size to 1 since we'll be running inference on
    # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1


# COCO Class names
# Index of the class in the list is its ID. For example, to get ID of
# the teddy bear class, use: class_names.index('teddy bear')
class_names = ['BG', 'person', 'bicycle', 'car', 'motorcycle', 'airplane',
               'bus', 'train', 'truck', 'boat', 'traffic light',
               'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird',
               'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear',
               'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie',
               'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
               'kite', 'baseball bat', 'baseball glove', 'skateboard',
               'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
               'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
               'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
               'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed',
               'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
               'keyboard', 'cell phone', 'microwave', 'oven', 'toaster',
               'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors',
               'teddy bear', 'hair drier', 'toothbrush']


def filter_results(r, itemset):
    allowed_indices = [class_names.index(item) for item in itemset]
    filter_mask = np.isin(r['class_ids'], allowed_indices)
    r['rois'] = r['rois'][filter_mask, :]
    r['scores'] = r['scores'][filter_mask]
    r['class_ids'] = r['class_ids'][filter_mask]
    r['masks'] = r['masks'][:, :, filter_mask]

    return r


class CocoModel(Model):
    def __init__(self, items=None):
        """Initialize the Coco Model

        Arguments
        ---------
        items: list-like
            Only items from this list will be annotated, and the rest will be discarded.
            If not provided, all masks are generated.
        """
        super().__init__("Coco")
        config = InferenceConfig()

        # Create model object in inference mode.
        self.model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=config)

        # Default to all classes in case no filter is provided
        if not items:
            items = class_names
        self.items = list(items)

    def load(self, filepath=None):
        self.model.load_weights(COCO_MODEL_PATH, by_name=True)

    def create_mask(self, filepath, output_dir):
        output_path = output_dir + "/" + os.path.basename(filepath)
        image = skimage.io.imread(filepath)
        print(image.shape)

        # Run detection
        results = self.model.detect([image], verbose=1)

        # Visualize results
        r = results[0]
        r = filter_results(r, self.items)

        visualize.display_instances(image, r['rois'], r['masks'], r['class_ids'],
                                    class_names, r['scores'],
                                    show_label=False, show_bbox=False,
                                    figsize=(8, 8), savepath=output_path)

        out = skimage.io.imread(output_path)
        skimage.io.imsave("tmp.jpg", out)
        out = post_process(out)
        skimage.io.imsave(output_path, out)

        return output_path

if __name__ == "__main__":
    model = CocoModel()
    model.load()
    f = model.create_mask("15409674101077949923911974822053.jpg", "output")
    print(f)
