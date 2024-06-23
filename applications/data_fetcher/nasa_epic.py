import os
import shutil

import requests


class NasaEpic:
    def __init__(self, save_directory):
        save_directory = os.environ.get("IMAGE_DIRECTORY") if save_directory is None else save_directory
        self.save_path = os.path.join(os.path.dirname(__file__), save_directory)
        os.mkdir(self.save_path)

    def get_images(self, date):
        year, month, day = date.split("-")
        images = requests.get("https://epic.gsfc.nasa.gov/api/natural/date/%s" % date)
        for image in images.json():
            image_filename = f'{image["image"]}.png'
            image_url = f"https://epic.gsfc.nasa.gov/archive/natural/{year}/{month}/{day}/png/{image_filename}"
            image_response = requests.get(image_url, stream=True)
            with open(os.path.join(self.save_path, image_filename), 'wb') as out_file:
                shutil.copyfileobj(image_response.raw, out_file)
            del image_response
