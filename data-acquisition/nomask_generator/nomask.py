from PIL import Image
from google_images_download import google_images_download
import Augmentor
import glob
import shutil
import os

class NoMask:

    def __init__(self, search_term, number_of_images):
        self.search_term = search_term
        self.number_of_images = number_of_images
    
    def create_image_dataset(self):
        """
        Download images from Google, and generate the corresponding
        masks for these images. There is a limit of 100, which can 
        be overridden by setting up Selenium and Chromedriver. 
        """
        response = google_images_download.googleimagesdownload()
        arguments = {"keywords":self.search_term, "limit":self.number_of_images, "print_urls":False,
                    "output_directory":"no_mask", "image_directory":"images", "format":"jpg"}
        response.download(arguments)
        path = 'no_mask/images'
        i = 0
        for filename in os.listdir(path):
            os.rename(os.path.join(path,filename), os.path.join(path,'image'+str(i)+'.jpg'))
            i = i + 1
        list_of_files = glob.glob("no_mask/images/*.jpg")
        os.mkdir("no_mask/masks")
        for file in list_of_files:
            self.create_masks(file)

        return
    
    def create_masks(self, path):
        """
        This function generate empty black masks for each of 
        the images downloaded from Google. 
        """
        x = path.rstrip('\n')
        t = x.split('/')[-1].rstrip('.jpg')
        im = Image.open(x)
        img = Image.new('RGB', im.size)
        img.save("no_mask/masks/"+"mask_"+t+".jpg", "JPEG")
        return

        