import unittest
import responses

from space_pop import SpacePop


class GetSpacePop(unittest.TestCase):
    def setUp(self):
        self.mock_response = responses.get("http://api.open-notify.org/astros.json", json={"number": 33})

    @responses.activate
    def test_queries_api(self):
        SpacePop().get_space_pop()
        self.assertEqual(self.mock_response.call_count, 1)

    @responses.activate
    def test_returns_api_data(self):
        self.assertEqual(SpacePop().get_space_pop(), 33)


if __name__ == '__main__':
    unittest.main()
