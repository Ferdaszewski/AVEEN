import os
import shutil
from datetime import datetime

import requests


class NasaEpic:
    def __init__(self, save_directory=None):
        save_directory = os.environ.get("IMAGE_DIRECTORY") if save_directory is None else save_directory
        self.save_path = os.path.join(os.path.dirname(__file__), save_directory)
        os.mkdir(self.save_path)

    def get_image(self, image):
        # 2024-06-11 00:31:45
        year, month, day = image['date'][:10].split("-")
        image_filename = f'{image["image"]}.png'
        image_path = os.path.join(self.save_path, image_filename)

        image_url = f"https://epic.gsfc.nasa.gov/archive/natural/{year}/{month}/{day}/png/{image_filename}"
        image_response = requests.get(image_url, stream=True)
        with open(image_path, 'wb') as out_file:
            shutil.copyfileobj(image_response.raw, out_file)
        del image_response
        return image_path, image

    def get_images(self, date):
        images = requests.get("https://epic.gsfc.nasa.gov/api/natural/date/%s" % date)
        return [self.get_image(image) for image in images.json()]

    def save_images(self, db_connection, date=datetime.utcnow().strftime("%Y-%m-%d")):
        saved_images = self.get_images(date)
        with db_connection as conn:
            insert_image_sql = "INSERT INTO epic_images (image_path, image_metadata) VALUES (%s, %s)"
            for path, metadata in saved_images:
                with conn.cursor() as cursor:
                    cursor.execute(insert_image_sql, (path, metadata))
