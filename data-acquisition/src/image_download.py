"""
Script to download images from google.
Uses python package: https://github.com/hardikvasa/google-images-download
Install the package using: pip install google_images_download

Currently you can download upto 100 images at a time without any extra 
modifications.
For more than 100 images we need to configure selenium and chromedriver.

By default the images will get stored to download folder in the same directory
as the script.
"""


from google_images_download import google_images_download


response = google_images_download.googleimagesdownload()
arguments = {"keywords":"football","limit":10,"print_urls":True}   #creating list of arguments
paths = response.download(arguments)   #passing the arguments to the function
print(paths)
