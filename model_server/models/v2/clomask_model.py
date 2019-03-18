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

from .config import InferenceConfig

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_DIR = os.path.join(ROOT_DIR, "logs")

# Local path to trained weights file
CLOMASK_MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn_clomask_0055.h5")


class ClomaskModel(MaskRCNNModel):
    def __init__(self, items=None):
        """Initialize the Clomask Model

        Arguments
        ---------
        items: list-like
            Only items from this list will be annotated, and the rest will be discarded.
            If not provided, all masks are generated.
        """
        super().__init__(name="Clomask", config=InferenceConfig(), model_dir=MODEL_DIR, items=items)

    def load(self, filepath=CLOMASK_MODEL_PATH):
        self.model.load_weights(filepath, by_name=True)
