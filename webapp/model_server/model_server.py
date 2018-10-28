import os
from time import sleep

import boto3

from config import *
from model import load_model


SQS_QUEUE = boto3.resource("sqs").Queue(SQS_URL)
S3_BUCKET = boto3.resource("s3").Bucket(S3_BUCKET_URL)

# Load the model once, during deployment
MODEL = load_model(MODEL_PATH)

def s3_image_key_gen():
    while True:
        messages = SQS_QUEUE.receive_messages(MaxNumberOfMessages=10)
        if not messages:
            sleep(10)
            continue

        for message in messages:
            obj_key = message["Records"][0]["s3"]["object"]["key"]
            yield obj_key, message.receipt_handle


def cleanup(s3_image_key):
    os.remove(s3_image_key)
    os.remove(OUTPUT_DIR + "/" + s3_image_key)


def create_mask(s3_image_key):
    # Use the model to create the mask files and the visualization
    pass


def main():
    # Indefinite loop to listen to messages on the queue
    for s3_image_key, receipt_handle in s3_image_key_gen():

        # Pick up the image from S3
        S3_BUCKET.download_file(s3_image_key, s3_image_key)

        # Get the mask predictions and annotations
        create_mask(s3_image_key)

        # Upload to output S3 bucket
        S3_BUCKET.upload_file("{}/{}".format(OUTPUT_DIR, s3_image_key), s3_image_key)

        # Cleanup files
        cleanup(s3_image_key)

        # Delete from queue, so that we don't reprocess it
        SQS_QUEUE.delete_messages(Entries=[{'Id': 'dummy', 'ReceiptHandle': receipt_handle}])


if __name__ == "__main__":
    main()
