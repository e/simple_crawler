import unittest
from sainsburys_crawler import Client as SainsburysClient
 
class TestCrawler(unittest.TestCase):
 
    def setUp(self):
        self.client = SainsburysClient()
 
    def test_get_data(self):
        data = self.client.get_data()
        self.assertEqual(type(data), dict)

if __name__ == '__main__':
    unittest.main()
