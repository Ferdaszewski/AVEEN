import unittest
import responses

from world_pop import WorldPop


class GetWorldPop(unittest.TestCase):
    def setUp(self):
        json_response = {'world': {'pop_midnight': 333}}
        self.mock_response = responses.get("https://www.census.gov/popclock/data/population.php/world", json=json_response)

    @responses.activate
    def test_queries_api(self):
        WorldPop().get_world_pop()
        self.assertEqual(self.mock_response.call_count, 1)

    @responses.activate
    def test_returns_api_data(self):
        self.assertEqual(WorldPop().get_world_pop(), 333)


if __name__ == '__main__':
    unittest.main()
