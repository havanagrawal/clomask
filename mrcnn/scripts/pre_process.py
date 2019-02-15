"""
Script to pre process mask files and convert to H5 files creating stiched masks and mask label list
for faster training time and multiclassification.
"""

from config import *
import time
import numpy as np
import os
import cv2
import h5py
import gc


def mask_to_h5(train_path):
    """
        Generating masks and saving to .h5 file for faster training.
    """
    train_ids = list(os.listdir(train_path))
    for i, id_ in enumerate(train_ids):
        path = train_path + id_
        if os.path.exists(path + IMAGE_PATH + id_ + '.h5'):
            os.remove(path + IMAGE_PATH + id_ + '.h5')
        if os.path.exists(path + MASK_PATH + id_ + '.h5'):
            os.remove(path + MASK_PATH + id_ + '.h5')
        mask = []
        label_array = []
        for mask_file in next(os.walk(path + MASK_PATH))[2]:
            if 'png' in mask_file:
                    class_id = int(mask_file.split('__')[1][:-4])
                    label_array.append(class_id)
                    mask_ = cv2.imread(path + MASK_PATH + mask_file, 0)
                    i += 1
                    mask_ = np.where(mask_ > 128, 1, 0)
                    # Add mask only if its area is larger than one pixel
                    if np.sum(mask_) >= 1:
                        mask.append(np.squeeze(mask_))
        mask = np.stack(mask, axis=-1)
        mask = mask.astype(np.uint8)
        fname = path + MASK_PATH + id_ + '.h5'
        with h5py.File(fname, "w") as hf:
            hf.create_dataset("mask_images", data=mask)
            hf.create_dataset("labels", data=label_array)
        # removing mask incase of memory issue
        del mask
        gc.collect()
        print('Done with file-{}'.format(i))


if __name__ == '__main__':
    start = time.time()
    mask_to_h5(train_path)
    print('Elapsed time', round((time.time() - start)/60, 1), 'minutes')
