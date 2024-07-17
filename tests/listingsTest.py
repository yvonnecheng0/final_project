import sys
import os

# Adjusts the sys.path to include the parent directory -- importing listings wasn't working otherwise
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from listings  import * 
import unittest
from unittest.mock import patch


JOBS_URL = "https://raw.githubusercontent.com/hzlsrdz/mock-jobs/main/good_jobs.json"
BAD_URL = "https://github.com/hzlsrdz/mock-jobs/blob/main/good_jobs.json"

class TestFetchListings(unittest.TestCase):
    
    # Tests that a valid URL returns data in this specific JSON format
    def test_fetch_listings(self):
        expected_response = [
            {
                "date_updated": 1714588234,
                "url": "https://en.wikipedia.org/wiki/The_Office_(American_TV_series)",
                "locations": [
                    "Scranton, PA"
                ],
                "season": "Summer",
                "sponsorship": "Offers Sponsorship",
                "active": True,
                "company_name": "Dunder Mifflin Paper Company",
                "title": "Assistant to the Regional Manager",
                "source": "Ouckah",
                "id": "17eb6180-04a0-4148-8756-07e5c051123f",
                "date_posted": 1714588234,
                "company_url": "",
                "is_visible": True
            },
            {
                "date_updated": 1714613432,
                "url": "https://en.wikipedia.org/wiki/Gossip_Girl",
                "locations": [
                    "New York, NY"
                ],
                "season": "Summer",
                "sponsorship": "Offers Sponsorship",
                "active": True,
                "company_name": "Blog",
                "title": "Gossip Girl",
                "source": "Secret",
                "id": "27e18275-9232-498e-b2b3-409d2f248775",
                "date_posted": 1714613432,
                "company_url": "",
                "is_visible": True
            },
            {
                "date_updated": 1714589234,
                "url": "https://en.wikipedia.org/wiki/Peaky_Blinders_(TV_series)",
                "locations": [
                    "Birmingham, PA", "Antioch, CA", "Bay Point, CA"
                ],
                "season": "Summer",
                "sponsorship": "Offers Sponsorship",
                "active": True,
                "company_name": "The Shelby Company Limited",
                "title": "Crime Boss",
                "source": "Netflix",
                "id": "17eb6180-04a0-4148-8756-07e5c051123f",
                "date_posted": 1714688234,
                "company_url": "",
                "is_visible": True
            },
            {
                "date_updated": 1724613432,
                "url": "https://en.wikipedia.org/wiki/Gossip_Girl",
                "locations": [
                    "New York, NY"
                ],
                "season": "Summer",
                "sponsorship": "Offers Sponsorship",
                "active": True,
                "company_name": "Blog",
                "title": "Gossip Girl",
                "source": "Secret",
                "id": "27e18275-9232-498e-b2b3-409d2f248775",
                "date_posted": 1714615432,
                "company_url": "",
                "is_visible": True
            }
        ]
        
        actual_response = fetch_listings(JOBS_URL)
        
        self.assertEqual(actual_response, expected_response)

    # Tests that a JSON URL that isn't "raw" returns an empty list
    def test_fetch_wrong_url(self):
        actual_response = fetch_listings(BAD_URL)

        self.assertEqual(actual_response, [])
    
    # Tests that 400 errors are handled
    @patch('requests.get')
    def test_fetch_400_error(self, mock_get):
        mock_get.return_value.status_code = 400
        actual_response = fetch_listings("https://httpbin.org/status/400")
        self.assertEqual(actual_response, [])

    # Tests that 500 errors are handled
    @patch('requests.get')
    def test_fetch_500_error(self, mock_get):
        mock_get.return_value.status_code = 500
        actual_response = fetch_listings("https://httpbin.org/status/500")
        self.assertEqual(actual_response, [])

class TestParseListings(unittest.TestCase):

    # Tests that listings are formatted correctly
    def testFormatListings(self):
        job_1 = fetch_listings(JOBS_URL)[0]
        expected_response1 = {
            "date": datetime.fromtimestamp(1714588234, timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z'),
            "company": "Dunder Mifflin Paper Company",
            "title": "Assistant to the Regional Manager",
            "locations": ["Scranton, PA"],
            "url": "https://en.wikipedia.org/wiki/The_Office_(American_TV_series)"
        }
        actual_response1 = format_listing(job_1)

        job_2 = fetch_listings(JOBS_URL)[2]
        expected_response2 = {
            "date": datetime.fromtimestamp(1714589234, timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z'),
            "company": "The Shelby Company Limited",
            "title": "Crime Boss",
            "locations": ["Birmingham, PA", "Antioch, CA", "Bay Point, CA"],
            "url": "https://en.wikipedia.org/wiki/Peaky_Blinders_(TV_series)"
        }
        actual_response2 = format_listing(job_2)

        self.assertEqual(actual_response1, expected_response1)
        self.assertEqual(actual_response2, expected_response2)

if __name__ == "__main__":
    unittest.main()

