import unittest

from applications.data_fetcher.nasa_epic import NasaEpic
from applications.data_fetcher.space_pop import SpacePop
from applications.data_fetcher.world_pop import WorldPop
from support.database import setup_db_connection


class TestIntegration(unittest.TestCase):
    def test_fetcher_and_processor(self):
        connection = setup_db_connection()
        SpacePop().save_space_pop(connection)
        WorldPop().save_space_pop(connection)
        NasaEpic().save_images(connection)


if __name__ == '__main__':
    unittest.main()
