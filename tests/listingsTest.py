import sys
import os

# Adjusts the sys.path to include the parent directory -- importing listings wasn't working otherwise
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from listings  import * 
import unittest
from unittest.mock import patch


JOBS_URL = "https://raw.githubusercontent.com/hzlsrdz/mock-jobs/main/good_jobs.json"
BAD_URL = "https://github.com/hzlsrdz/mock-jobs/blob/main/good_jobs.json"

MOCK_JSON = [
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
                "id": "17eb6180-04a0-4148-8756-07e5c051126g",
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
                "id": "27e18275-9232-498e-b2b3-409d2f2487984",
                "date_posted": 1714615432,
                "company_url": "",
                "is_visible": True
            }
        ]


class TestFetchListings(unittest.TestCase):
    
    # Tests that a valid URL returns data in this specific JSON format
    def test_fetch_listings(self):
        actual_response = fetch_listings(JOBS_URL)
        
        self.assertEqual(actual_response, MOCK_JSON)

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

    def setUp(self):
        # Fetch listings once and store them for use in tests
        self.listings = fetch_listings(JOBS_URL)

    # Tests that listings are formatted correctly
    def testFormatListings(self):
        # Test the formatting of the first job listing
        job_1 = self.listings[0]
        expected_response1 = {
            "posted": datetime.fromtimestamp(1714588234, timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z'),
            "updated": datetime.fromtimestamp(1714588234, timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z'),
            "company": "Dunder Mifflin Paper Company",
            "title": "Assistant to the Regional Manager",
            "season": "Summer",
            "sponsorship": "Offers Sponsorship",
            "active": 1,  # Converted True to 1
            "locations": ["Scranton, PA"],
            "url": "https://en.wikipedia.org/wiki/The_Office_(American_TV_series)"
        }
        actual_response1 = format_listing(job_1)
        self.assertEqual(actual_response1, expected_response1, "Mismatch in job 1 formatting")

        # Test the formatting of the second job listing
        job_2 = self.listings[1]
        expected_response2 = {
            "posted": datetime.fromtimestamp(1714613432, timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z'),
            "updated": datetime.fromtimestamp(1714613432, timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z'),
            "company": "Blog",
            "title": "Gossip Girl",
            "season": "Summer",
            "sponsorship": "Offers Sponsorship",
            "active": 1,  # Converted True to 1
            "locations": ["New York, NY"],
            "url": "https://en.wikipedia.org/wiki/Gossip_Girl"
        }
        actual_response2 = format_listing(job_2)
        self.assertEqual(actual_response2, expected_response2, "Mismatch in job 2 formatting")

if __name__ == "__main__":
    unittest.main()

