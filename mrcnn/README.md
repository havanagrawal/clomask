# Model Training

## Table of Contents

1. [Introduction](#introduction)  
1. [Examples](#examples)  
1. [Usage](#usage)  
 

## Introduction


## Setup

Run data synthesizer module to generate the training  datasets in the following folder structure:

~~~~~~~
        project
          |-- mrcnn
               |-- scipts
                    |-- config.py
                    |-- model.py
                    |-- train.py
                    |-- pre_process.py
                    |-- requirements.txt
                    |-- utils.py
                    |-- visualize.py
                    |-- Inference_notebook.ipynb
                    |-- utils.py
                    
               |--- mask_data
                    |-- id_map.json
                    |-- logs/
                    |-- mask_rcnn_coco.h5
                    |-- test_image
                    |-- train_image
~~~~~~~

## Training


### Pre-processing
Data pre-processing using pre_process.py to generate .h5 file for masks.


### Model and Training

 -- Modified Matterport's implementation of Mask-RCNN deep neural network for object instance segmentation.
    Model - Added two new methods to train just specific masks.
            mrcnn_mask: Just mask layers
            mask_heads: Mask layers or rpn/fpn
    Multiclass- Pre_processed images and mask files accordingly to prepare for multi classification.
 -- Increased maximum number of predicted objects since an image can contain 200 or more bottles/bags/boxes.
 -- Increased POST_NMS_ROIS_TRAINING to get more region proposals during training.
 -- Resized images and masks to 512x512.
 -- Used Default anchor size as we do not expect small objects: RPN_ANCHOR_SCALES = (16, 32, 64, 128, 256)
 -- Relied heavily on deep image augmentation due to small training set:
      Random horizontal or vertical flips
      Random 90 or -90 degrees rotation
      Random rotations in the range of (-20, 20) degrees
      Random scaling of image and mask scaling in the range (0.5, 2.0)
 -- Used Resnet101 architecture as a backbone encoder.
 -- Trained the model with Adam optimizer for 65 epochs:
 -- 5 epochs of heads with learning rate 1e-4 (To speed up the training process)
 -- 30 epochs with learning rate 1e-5
 -- 30 epochs with learning rate 1e-6
 -- changed mAP computation to be (0.5 - 0.8) 
 -- weighted mAP 
 -- weighted loss 
 LOSS_WEIGHTS = {
        "rpn_class_loss": 20.,
        "rpn_bbox_loss": 1.,
        "mrcnn_class_loss": 10.,
        "mrcnn_bbox_loss": 1.,
        "mrcnn_mask_loss": 10.
    }

```
   
### Model Execution and Run-Time
Run `python pre_process.py` to pre-process data 

Run `python train.py` to train the model. Model weights are saved at ../data/logs/kaggle_bowl/mask_rcnn.h5.

Run python inference_notebook.ipynb.py to evaluate model performance on test set 


The following execution times are measured on Nvidia P100 GPUs provided by AWS Deep learning AMI

```
Each training epoch takes about 25 minutes.
It takes about 18 hours to train the model from scratch.

## Example model predictions

[put graphs from notebook]
