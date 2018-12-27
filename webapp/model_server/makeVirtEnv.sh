#!/bin/bash
virtualenv -p /Users/havan/anaconda3/bin/python3 modelserver
. modelserver/bin/activate
pip3 install -r Mask_RCNN/requirements.txt
pip3 install -r requirements.txt
