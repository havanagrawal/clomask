"""Utility methods for manipulating images"""

import numpy as np

def post_process(im):
    """Remove the padding added by the model"""
    for i in range(im.shape[0]):
        for j in range(im.shape[1]):
            replace_pixel_with_white(im, i, j)

    return remove_border(im)


def replace_pixel_with_white(im, i, j, threshold=200):
    r, g, b = im[i, j, :]
    if r >= threshold and g >= threshold and b >= threshold:
        im[i, j, :] = np.array([255, 255, 255])

def remove_border(im):
    """Remove the border (frame) of an image if it is a constant pattern"""
    for trimmer in [trim_top, trim_bottom, trim_left, trim_right]:
        im = trimmer(im)

    return im

def trim_top(im):
    i = 1

    if not np.all(im[0, :, :] == im[i, :, :]):
        return im

    while np.all(im[0, :, :] == im[i, :, :]):
        i += 1

    return im[i:, :, :]

def trim_bottom(im):
    height = im.shape[0] - 1
    i = height - 1

    if not np.all(im[height, :, :] == im[i, :, :]):
        return im

    while np.all(im[height, :, :] == im[i, :, :]):
        i -= 1

    return im[:i, :, :]

def trim_left(im):
    i = 1

    if not np.all(im[:, 0, :] == im[:, i, :]):
        return im

    while np.all(im[:, 0, :] == im[:, i, :]):
        i += 1

    return im[:, i:, :]

def trim_right(im):
    width = im.shape[1] - 1
    i = width - 1

    if not np.all(im[:, width, :] == im[:, i, :]):
        return im

    while np.all(im[:, width, :] == im[:, i, :]):
        i -= 1

    return im[:, :i, :]
