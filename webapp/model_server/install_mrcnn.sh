#!/bin/bash

# Installs the latest version of M-RCNN
# Ensure that you have activated your virtualenv before running this script

git clone https://github.com/matterport/Mask_RCNN.git
cd Mask_RCNN
pip3 install -r requirements.txt
python3 setup.py install
