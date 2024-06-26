import os
import tempfile

import boto3
import ffmpeg
import pika
from dotenv import load_dotenv

from support.database import setup_db_connection


class DataProcessor:
    def __init__(self):
        self.s3_bucket = boto3.resource(
            's3',
            aws_access_key_id=os.environ.get("BUCKETEER_AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("BUCKETEER_AWS_SECRET_ACCESS_KEY"),
            region_name=os.environ.get("BUCKETEER_AWS_REGION"),
        ).Bucket(os.environ.get('BUCKETEER_BUCKET_NAME'))

    def create_video(self, image_dir, video_filename):
        (ffmpeg
         .input(image_dir, pattern_type='glob', framerate=2)
         .filter('scale', size='hd1080', force_original_aspect_ratio='decrease')
         .filter('minterpolate', fps='60', scd='none', mi_mode='mci', mc_mode='obmc', search_param=128, me='epzs',
                 vsbmc=1)
         .output(video_filename, movflags='faststart', pix_fmt='yuv420p', r=60)
         .run())

    def get_image_data(self, day):
        with setup_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT image_key FROM epic_images WHERE image_day = %s", (day,))
                rows = cursor.fetchall()
                return rows if rows is None else [row[0] for row in rows]

    def process(self, day):
        print(f"Processing started for {day}")
        image_keys = self.get_image_data(day)
        images_num = len(image_keys)
        if images_num == 0:
            print("No images found to process")
            return
        print(f"Found {images_num} images to process")

        with tempfile.TemporaryDirectory() as tmpdir:
            image_dir = os.path.join(tmpdir, 'images')
            os.mkdir(image_dir)
            for image_key in image_keys:
                file_name = image_key.split('/')[-1]
                file_path = os.path.join(image_dir, file_name)
                print(f"Downloading image with key {image_key} from s3 to {file_path}")
                with open(os.path.join(image_dir, file_name), 'wb') as data:
                    self.s3_bucket.download_fileobj(image_key, data)

            image_glob = os.path.normpath(os.path.join(image_dir, '*.png'))
            video_name = f'{day}-earth.mp4'
            video_local_path = os.path.normpath(os.path.join(tmpdir, video_name))
            video_key = f'videos/{video_name}'
            print("Starting video creation")
            self.create_video(image_glob, video_local_path)
            print(f"Video created: {video_local_path}")

            # Available at https://bucketeer-3f5efd47-dcff-47cf-ab77-76a0f9c3b9b9.s3.us-east-1.amazonaws.com/videos/2024-06-11-earth.mp4
            self.s3_bucket.upload_file(video_local_path, video_key)
            print(f"Video uploaded to s3 with key {video_key}")

            with setup_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id from space_pop ORDER BY fetched_at DESC LIMIT 1")
                    space_row = cursor.fetchone()
                    space_pop_id = space_row if space_row is None else space_row[0]
                    cursor.execute("SELECT id from world_pop ORDER BY fetched_at DESC LIMIT 1")
                    world_row = cursor.fetchone()
                    world_pop_id = world_row if world_row is None else world_row[0]

                    insert_video_sql = "INSERT INTO video_pop (video_key, video_day, space_pop_id, world_pop_id) VALUES (%s, %s, %s, %s)"
                    cursor.execute(insert_video_sql, (video_key, day, space_pop_id, world_pop_id))
        print("Processing finished")


if __name__ == "__main__":
    load_dotenv()
    params = pika.URLParameters(os.environ.get('CLOUDAMQP_URL'))
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue='aveey_new_images')  # Declare a queue


    def callback(ch, method, properties, body):
        DataProcessor().process(body.decode('utf-8'))


    channel.basic_consume('aveey_new_images',
                          callback,
                          auto_ack=True)

    print(' [*] Waiting for messages:')
    channel.start_consuming()
    connection.close()
