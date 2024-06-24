import os
import shutil
import unittest
from unittest.mock import Mock, call

import responses

from nasa_epic import NasaEpic


def cleanup_dir(save_dir):
    try:
        shutil.rmtree(os.path.join(os.path.dirname(__file__), save_dir))
    except FileNotFoundError:
        pass


class TestNasaEpicGetImages(unittest.TestCase):
    date = '2024-06-11'
    image_data = [
        {'image': 'epic_1b_20240611003634', "date": "2024-06-11 00:31:45"},
        {"image": "epic_1b_20240611014201", 'date': "2024-06-11 01:37:12"},
    ]
    save_dir = "test_images"

    def setUp(self):
        cleanup_dir(self.save_dir)
        self.nasa_epic = NasaEpic(self.save_dir)
        self.nasa_epic.get_image = Mock(name='get_image')
        self.mock_response = responses.get(
            f"https://epic.gsfc.nasa.gov/api/natural/date/{self.date}",
            json=self.image_data
        )

    def cleanUp(self):
        cleanup_dir(self.save_dir)

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

    def setUp(self):
        cleanup_dir(self.save_dir)
        self.nasa_epic = NasaEpic(self.save_dir)
        self.image_filename = 'test-image-filename'
        self.year = '2023'
        self.month = '06'
        self.day = '11'
        self.image_json = {
            'date': f'{self.year}-{self.month}-{self.day} 00:31:45',
            'image': self.image_filename,
        }
        self.image_data = 'testimagedata'
        image_url = f"https://epic.gsfc.nasa.gov/archive/natural/{self.year}/{self.month}/{self.day}/png/{self.image_filename}.png"
        self.mock_response = responses.get(
            image_url,
            body=self.image_data,
            match=[responses.matchers.request_kwargs_matcher({'stream': True})]
        )

    def cleanUp(self):
        cleanup_dir(self.save_dir)

    @responses.activate
    def test_gets_image_from_api(self):
        self.nasa_epic.get_image(self.image_json)
        self.assertEqual(self.mock_response.call_count, 1)

    @responses.activate
    def test_saves_image(self):
        image_path, _ = self.nasa_epic.get_image(self.image_json)
        with open(image_path) as image_file:
            self.assertEqual(self.image_data, image_file.read())

    @responses.activate
    def test_returns_data(self):
        _, image_data = self.nasa_epic.get_image(self.image_json)
        self.assertEqual(image_data, self.image_json)


if __name__ == '__main__':
    unittest.main()
