"""
Training module for maskrcnn on Bottles, Boxes and Candy bags.
"""

from config import *
import h5py
from imgaug import augmenters as iaa
from sklearn.model_selection import train_test_split
from random import randint
import numpy as np


class ClomaskDataset(utils.Dataset):
    """
        Class wrapper for clomask dataset.
    """

    def load_shapes(self, id_list, train_path):
        """
           Initialize the class with dataset info.
        """
        # Add classes
        self.add_class('clomask', 1, "bottles")
        self.add_class('clomask', 2, "boxes")
        self.add_class('clomask', 3, "bags")
        self.train_path = train_path
        # Add images
        for i, id_ in enumerate(id_list):
            self.add_image('clomask', image_id=i, path=None,
                           img_name=id_)

    def _load_img(self, fname):
        """
           Reading image file from a path.
        """
        img = cv2.imread(fname)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
        return img

    def load_image(self, image_id, color):
        """
            Load image from directory
        """
        info = self.image_info[image_id]
        path = self.train_path + info['img_name'] + \
            IMAGE_PATH + info['img_name'] + '.png'
        try:
            img = self._load_img(path)
        except:
            path = self.train_path + info['img_name'] + \
                IMAGE_PATH + info['img_name'] + '.jpg'
            img = self._load_img(path)
        return img

    def image_reference(self, image_id):
        """
            Return the images data of the image.
        """
        info = self.image_info[image_id]
        return info['path']

    def load_mask(self, image_id):
        """
            Generate instance masks for images of the given image ID.
        """

        info = self.image_info[image_id]
        path = self.train_path + info['img_name'] + \
            MASK_PATH + info['img_name'] + '.h5'
        if os.path.exists(path):
            with h5py.File(path, "r") as hf:
                mask = hf["mask_images"][()]
                class_ids = hf["labels"][()]
        else:
            path = self.train_path + info['img_name']
            mask = []
            label_array = []
            for mask_file in next(os.walk(path + MASK_PATH))[2]:
                if 'png' in mask_file:
                        # these lines have been commented out due to invalid test data file name
                        # class_id = int(mask_file.split('$')[1][:-4])
                        # label_array.append(class_id)
                        mask_ = cv2.imread(path + MASK_PATH + mask_file, 0)
                        mask_ = np.where(mask_ > 128, 1, 0)
                        # Add mask only if its area is larger than one pixel
                        if np.sum(mask_) >= 1:
                            mask.append(np.squeeze(mask_))
            mask = np.stack(mask, axis=-1)
            class_ids = np.ones(mask.shape[2])
        return mask.astype(np.uint8), class_ids.astype(np.int8)


class ClomaskTrain(object):
    """
        Training class for clomask dataset.
    """

    def __init__(self):
        self.init_weights = 'coco'
        self.config = ClomaskConfig()
        self.learning_rate_one = 1e-4
        self.learning_rate_two = 1e-5
        self.learning_rate_three = 1e-6
        self.train_data = None
        self.val_data = None

    def prepare_dataset(self):

        train_list, test_list = os.listdir(TRAIN_PATH), os.listdir(TEST_PATH)
    #     train_list, val_list = train_test_split(os.listdir(train_path), test_size=0.1,
    #                                             random_state=2019)

    # Use this for explode the training data for use in augmentation.
    # train_list = np.repeat(train_list,5)

        # initialize training dataset
        train_data = ClomaskDataset()
        train_data.load_shapes(train_list, TRAIN_PATH)
        train_data.prepare()

        # initialize validation dataset
        validation_data = ClomaskDataset()
        validation_data.load_shapes(test_list, TEST_PATH)
        validation_data.prepare()
        # Create model configuration in training mode

        self.config.STEPS_PER_EPOCH = len(train_list)//self.config.BATCH_SIZE
        self.config.VALIDATION_STEPS = len(test_list)//self.config.BATCH_SIZE

        self.train_data = train_data
        self.val_data = validation_data

    def weight_initialize(self):
        """
            Loading Model weights to start training with
        """
        self.model = modellib.MaskRCNN(mode="training", config=self.config, model_dir=MODEL_DIR)
        if self.init_weights == "imagenet":
            weights_path = self.model.get_imagenet_weights()
            self.model.load_weights(weights_path, by_name=True, exclude=["mrcnn_class_logits", "mrcnn_bbox_fc",
                                                                   "mrcnn_bbox", "mrcnn_mask"])
        elif self.init_weights == "coco":
            weights_path = COCO_PATH
            self.model.load_weights(weights_path, by_name=True, exclude=["mrcnn_class_logits", "mrcnn_bbox_fc",
                                                                   "mrcnn_bbox", "mrcnn_mask"])

    def model_train(self):

        augmentation = iaa.Sequential([
                    iaa.Fliplr(0.5),
                    iaa.Flipud(0.5),
                    iaa.OneOf([iaa.Affine(rotate=0),
                        iaa.Affine(rotate=90),
                        iaa.Affine(rotate=180),
                        iaa.Affine(rotate=270)]),
                        iaa.Sometimes(0.5, iaa.Affine(rotate=(-10, 10))),
                    iaa.Sometimes(0.5, iaa.Affine(scale=randint(2, 3)))
                    ])
        # Start Training the model

        self.model.train(self.train_data, self.val_data,
                    learning_rate=self.learning_rate_one,
                    epochs=5,
                    layers='heads')

        self.model.train(self.train_data, self.val_data,
                    learning_rate=self.learning_rate_two,
                    epochs=30,
                    layers='all',
                    augmentation=augmentation)

        self.model.train(self.train_data, self.val_data,
                    learning_rate=self.learning_rate_three,
                    epochs=60,
                    layers='all',
                    augmentation=augmentation)


def main():
    Clomasktrain = ClomaskTrain()
    Clomasktrain.prepare_dataset()
    Clomasktrain.weight_initialize()
    Clomasktrain.model_train()


if __name__ == '__main__':
    start = time.time()
    main()
    print('Elapsed time', round((time.time() - start)/60, 1), 'minutes')