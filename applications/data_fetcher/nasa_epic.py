import os
import boto3
from dotenv import load_dotenv

import requests
from psycopg2._json import Json


class NasaEpic:
    def __init__(self, save_directory=None):
        load_dotenv()
        self.save_directory = os.environ.get("IMAGE_DIRECTORY", "images") if save_directory is None else save_directory
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
        print(f"Downloading image: {image_url}")
        image_response = requests.get(image_url)
        print(f"Uploading image to s3 with key: {image_key}")
        self.s3_bucket.put_object(Key=image_key, Body=image_response.content)
        return image_key, image

    def get_images(self, date):
        images = requests.get("https://epic.gsfc.nasa.gov/api/natural/date/%s" % date)
        return [self.get_image(image) for image in images.json()]

    def get_new_date(self, db_connection):
        with db_connection as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT image_day FROM epic_images ORDER BY fetched_at DESC LIMIT 1")
                row = cursor.fetchone()
                db_date = row if row is None else row[0]
                available_dates = requests.get("https://epic.gsfc.nasa.gov/api/natural/all")
                newest_date = available_dates.json()[0]["date"]
                return newest_date if newest_date != db_date else None

    def save_images(self, db_connection):
        new_date = self.get_new_date(db_connection)
        if new_date is None:
            print("No new image data available")
            return
        print(f"Starting image gathering from NASA for {new_date}")
        saved_images = self.get_images(new_date)
        with db_connection as conn:
            insert_image_sql = "INSERT INTO epic_images (image_key, image_metadata, image_day) VALUES (%s, %s, %s)"
            for key, metadata in saved_images:
                with conn.cursor() as cursor:
                    cursor.execute(insert_image_sql, (key, Json(metadata), new_date))
        print(f"Finished image gathering from NASA for {new_date}")
