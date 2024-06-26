import os
import boto3
from dotenv import load_dotenv
from datetime import datetime

import requests


class NasaEpic:
    def __init__(self, save_directory=None):
        load_dotenv()
        self.save_directory = os.environ.get("IMAGE_DIRECTORY") if save_directory is None else save_directory
        self.s3_bucket = boto3.resource(
            's3',
            aws_access_key_id=os.environ.get("BUCKETEER_AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("BUCKETEER_AWS_SECRET_ACCESS_KEY"),
            region_name=os.environ.get("BUCKETEER_AWS_REGION"),
        ).Bucket(os.environ.get('BUCKETEER_BUCKET_NAME'))

    def get_image(self, image):
        # 2024-06-11 00:31:45
        year, month, day = image['date'][:10].split("-")
        image_directory = f"{self.save_directory}/{year}-{month}-{day}"
        image_filename = f'{image["image"]}.png'
        image_key = f"{image_directory}/{image_filename}"

        image_url = f"https://epic.gsfc.nasa.gov/archive/natural/{year}/{month}/{day}/png/{image_filename}"
        image_response = requests.get(image_url)
        self.s3_bucket.put_object(Key=image_key, Body=image_response.content)
        return image_key, image

    def get_images(self, date):
        images = requests.get("https://epic.gsfc.nasa.gov/api/natural/date/%s" % date)
        return [self.get_image(image) for image in images.json()]

    def save_images(self, db_connection, date=datetime.utcnow().strftime("%Y-%m-%d")):
        saved_images = self.get_images(date)
        with db_connection as conn:
            insert_image_sql = "INSERT INTO epic_images (image_key, image_metadata, image_day) VALUES (%s, %s, %s)"
            for key, metadata in saved_images:
                with conn.cursor() as cursor:
                    cursor.execute(insert_image_sql, (key, metadata, date))
