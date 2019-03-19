# Model Server

## Overview

This is the backend that serves the Mask R-CNN model. The basic flow is:
  1. Read messages off an SQS queue
  2. Get the S3 URL of the image
  3. Download the file locally
  4. Generate the mask files
  5. Upload the masked images to an output S3 bucket

## How To Run

From the Clomask (Git root) directory:

```bash
python3 -m model_server.server.model_server
```
