from unittest import TestCase

from nasa_epic import NasaEpic


class TestNasaEpic(TestCase):
    def test_get_images(self):
        NasaEpic("test_images").get_images("2024-06-11")
