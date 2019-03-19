"""The script that serves the model. Follows a simple flow:
    1. Read an S3 URI from the SQS queue
    2. Download the image
    3. Run the model's predict method to create the mask
    4. Upload the mask.
"""
import os
import sys
import json
from time import sleep
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s [%(process)d] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

abspath = os.path.abspath
sys.path.extend([
    abspath("mrcnn"),
    abspath("mrcnn/scripts")
])

import boto3

from .config import *
from ..models import ClomaskModel

SQS_QUEUE = boto3.resource("sqs").Queue(SQS_URL)
INPUT_S3_BUCKET = boto3.resource("s3").Bucket(INPUT_S3_BUCKET_NAME)
OUTPUT_S3_BUCKET = boto3.resource("s3").Bucket(OUTPUT_S3_BUCKET_NAME)

DOWNLOAD_DIR = "downloads"
OUTPUT_DIR = "output"

# How long should we wait if the queue is empty
SLEEP_TIME_IN_SEC = 2

def s3_image_key_gen():
    while True:
        messages = SQS_QUEUE.receive_messages(MaxNumberOfMessages=10, WaitTimeSeconds=SLEEP_TIME_IN_SEC)
        logging.info("Received %d messages", len(messages))

        for message in messages:
            m_dict = json.loads(message.body)
            logging.debug(m_dict)
            obj_key = m_dict["Records"][0]["s3"]["object"]["key"]
            obj_key = obj_key.replace("+", " ")
            yield obj_key, message.receipt_handle


def make_key(filename):
    just_file = os.path.basename(filename)
    parent_dir = os.path.basename(os.path.dirname(filename))
    return parent_dir + "/" + just_file

def main():
    logging.info("Starting up...")

    if not os.path.exists(DOWNLOAD_DIR):
        os.mkdir(DOWNLOAD_DIR)

    # Create the output dir if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    class_names = [None, 'bottle', 'box', 'bag']
    model = ClomaskModel(class_names=class_names)
    model.load()

    logging.info("Loaded model")

    # Indefinite loop to listen to messages on the queue
    for s3_image_key, receipt_handle in s3_image_key_gen():
        logging.info("Processing image %s with handle %s", s3_image_key, receipt_handle)

        download_path = os.path.join(DOWNLOAD_DIR, s3_image_key)

        # Pick up the image from S3
        INPUT_S3_BUCKET.download_file(Key=s3_image_key, Filename=download_path)
        logging.info("Downloaded %s from S3", s3_image_key)

        # Get the mask predictions and annotations
        output_files = model.create_mask(download_path, OUTPUT_DIR, generate_per_class=True)
        logging.info("Created mask for %s", s3_image_key)

        # Upload to output S3 bucket
        for output_file in output_files:
            key = make_key(output_file)
            OUTPUT_S3_BUCKET.upload_file(Filename=output_file, Key=key)
        logging.info("Uploaded %s to S3", s3_image_key)

        # Cleanup files
        os.remove(download_path)
        for output_file in output_files:
            os.remove(output_file)
        logging.info("Cleaned up local files")

        # Delete from queue, so that we don't reprocess it
        SQS_QUEUE.delete_messages(Entries=[{'Id': 'dummy', 'ReceiptHandle': receipt_handle}])
        logging.info("Successfully processed image %s with handle %s", s3_image_key, receipt_handle)


if __name__ == "__main__":
    main()
