# Model Server

## Overview

This is the backend that serves the Mask R-CNN model. The basic flow is:
  1. Read messages off an SQS queue
  2. Get the S3 URL of the image
  3. Download the file locally
  4. Generate the mask
  5. Upload the masked image to an output S3 bucket

## TODO

1. Create a generic "ModelAPI" interface. Create adapters for different models.
