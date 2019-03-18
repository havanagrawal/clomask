import os
import sys
import random
import math
from shutil import copyfile

import numpy as np
import skimage.io
import matplotlib
import matplotlib.pyplot as plt

from ...api import MaskRCNNModel
from ...imutils import post_process

# Import Mask RCNN
import utils
import visualize
import model as modellib

# Import COCO config
from .config import InferenceConfig

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Directory to save logs and trained model
MODEL_DIR = os.path.join(ROOT_DIR, "logs")

# Local path to trained weights file
COCO_MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco.h5")

# Download COCO trained weights from Releases if needed
if not os.path.exists(COCO_MODEL_PATH):
    utils.download_trained_weights(COCO_MODEL_PATH)


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


class CocoModel(MaskRCNNModel):
    def __init__(self, items=None):
        """Initialize the Coco Model

        Arguments
        ---------
        items: list-like
            Only items from this list will be annotated, and the rest will be discarded.
            If not provided, all masks are generated.
        """
        super().__init__(name="Coco", config=InferenceConfig(), model_dir=MODEL_DIR, class_names=class_names)
        self.items = items or class_names

    def load(self, filepath=COCO_MODEL_PATH):
        self.model.load_weights(filepath, by_name=True)

    def create_mask(self, filepath, output_dir):
        output_path = output_dir + "/" + os.path.basename(filepath)
        image = skimage.io.imread(filepath)
        print(image.shape)

        # Run detection
        results = self.model.detect([image], verbose=2)

        # Visualize results
        r = results[0]
        print(r)
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
