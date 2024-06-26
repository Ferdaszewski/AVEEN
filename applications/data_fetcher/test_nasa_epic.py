import os
import tempfile
import unittest
from datetime import datetime
from unittest.mock import Mock, call

import boto3
import responses
from dotenv import load_dotenv

from nasa_epic import NasaEpic


class TestNasaEpicGetImages(unittest.TestCase):
    date = '2024-06-11'
    image_data = [
        {'image': 'epic_1b_20240611003634', "date": "2024-06-11 00:31:45"},
        {"image": "epic_1b_20240611014201", 'date': "2024-06-11 01:37:12"},
    ]
    save_dir = "test_images"

    def setUp(self):
        self.nasa_epic = NasaEpic(self.save_dir)
        self.nasa_epic.get_image = Mock(name='get_image')
        self.mock_response = responses.get(
            f"https://epic.gsfc.nasa.gov/api/natural/date/{self.date}",
            json=self.image_data
        )

    @responses.activate
    def test_calls_api(self):
        self.nasa_epic.get_images(self.date)
        self.assertEqual(self.mock_response.call_count, 1)

    @responses.activate
    def test_calls_get_image(self):
        self.nasa_epic.get_images(self.date)
        self.nasa_epic.get_image.assert_has_calls([call(self.image_data[0]), call(self.image_data[1])])

    @responses.activate
    def test_returns_get_image(self):
        ret1 = {'test': 'return value'}
        ret2 = {'test2': 'another return value'}
        self.nasa_epic.get_image.side_effect = [ret1, ret2]
        self.assertEqual(self.nasa_epic.get_images(self.date), [ret1, ret2])


class TestNasaEpicGetImage(unittest.TestCase):
    save_dir = 'test_images'

    def cleanup_s3(self):
        response = self.s3_bucket.delete_objects(
            Delete={
                'Objects': [
                    {
                        'Key': self.image_key
                    }
                ]
            }
        )

    def setUp(self):
        load_dotenv()
        self.s3_bucket = boto3.resource('s3',
                                        aws_access_key_id=os.environ.get("BUCKETEER_AWS_ACCESS_KEY_ID"),
                                        aws_secret_access_key=os.environ.get("BUCKETEER_AWS_SECRET_ACCESS_KEY"),
                                        region_name=os.environ.get("BUCKETEER_AWS_REGION"),
                                        ).Bucket(os.environ.get('BUCKETEER_BUCKET_NAME'))
        self.nasa_epic = NasaEpic(self.save_dir)
        self.image_filename = 'test-image-filename'
        self.year = '2023'
        self.month = '06'
        self.day = '11'
        self.image_json = {
            'date': f'{self.year}-{self.month}-{self.day} 00:31:45',
            'image': self.image_filename,
        }
        self.image_key = f'{self.save_dir}/{self.year}-{self.month}-{self.day}/{self.image_filename}.png'
        self.image_data = f'{datetime.utcnow()}'
        image_url = f"https://epic.gsfc.nasa.gov/archive/natural/{self.year}/{self.month}/{self.day}/png/{self.image_filename}.png"
        self.mock_response = responses.get(
            image_url,
            body=self.image_data,
        )

    def tearDown(self):
        self.cleanup_s3()

    @responses.activate
    def test_gets_image_from_api(self):
        self.nasa_epic.get_image(self.image_json)
        self.assertEqual(self.mock_response.call_count, 1)

    @responses.activate
    def test_saves_image(self):
        self.cleanup_s3()
        image_key, _ = self.nasa_epic.get_image(self.image_json)
        with tempfile.TemporaryFile() as data:
            self.s3_bucket.download_fileobj(image_key, data)
            data.seek(0)
            self.assertEqual(self.image_data, data.read().decode('utf-8'))

    @responses.activate
    def test_returns_data(self):
        _, image_data = self.nasa_epic.get_image(self.image_json)
        self.assertEqual(image_data, self.image_json)


if __name__ == '__main__':
    unittest.main()
