import sys
import os

# Adjusts the sys.path to include the parent directory -- importing listings wasn't working otherwise
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from databases import *
import unittest
from listingsTest import JOBS_URL
from listings import *


class TestUsers(unittest.TestCase):

    mock_users = {"Rodya1866": "38JEbnjw@1H!!", "Sonya4U": "4Jewo0323w9eq", "DunyaIsSad": "0k2oL@j4skjw", "PorfiryLives": "heijoJO@092e"}

    def setup(self):
        create_tables("test_job_tracker.db")
        for user in self.mock_users.keys():
            register_user(user, user+"@fake.edu", self.mock_users[user], db="test_job_tracker.db")

    # Tests that users are actually being added to the table
    def testPresense(self):
        self.setup()
        actual = is_user("DunyaIsSad", db="test_job_tracker.db")
        self.assertEqual(actual, True)
    
    # Tests that duplicate usernames are not possible
    def testBadUser(self):
        attempt1 = register_user("Sonya4U", "newEmail@bob.net", "newPassword", db="test_job_tracker.db")
        self.assertEqual(attempt1, 1)

    # Tests that users are properly removed
    def testRemoveUser(self):
        remove_user("Sonya4U", db="test_job_tracker.db")
        attempt2 = register_user("Sonya4U", "newEmail@bob.net", "newPassword", db="test_job_tracker.db")
        self.assertEqual(attempt2, None)
        
    # Tests that reseting the database deletes the tables within too 
    def testDeletion(self):
        reset_all("test_job_tracker.db")
        with self.assertRaises(sqlite3.OperationalError) as cm:
            register_user("Sonya4U", "newEmail@bob.net", "newPassword", db="test_job_tracker.db")
        self.assertIn("no such table: users", str(cm.exception))

    # Tests that database is gone from file paths
    def testGoneDB(self):
        create_tables("test_job_tracker.db")
        reset_all("test_job_tracker.db")
        self.assertFalse(os.path.exists("test_job_tracker.db"), "Database file should not exist")

class TestJobs(unittest.TestCase):
    
    def testAddJob(self):
        create_tables("test_job_tracker.db")
        listings = fetch_listings(JOBS_URL)

        listing_dict = format_listing(listings[0])
        add_job(listing_dict["id"], listing_dict["date"], listing_dict["company"], listing_dict["title"], 
                listing_dict["locations"], listing_dict["url"], db="test_job_tracker.db")
        
        self.assertEqual(isJob("17eb6180-04a0-4148-8756-07e5c051123f", "test_job_tracker.db"), True)

    def testAddMultipleJobs(self):
        listings = fetch_listings(JOBS_URL)
        for listing in listings:
            lDict = format_listing(listing)
            add_job(lDict["id"], lDict["date"], lDict["company"], lDict["title"], 
                lDict["locations"], lDict["url"], db="test_job_tracker.db")
            
        self.assertEqual(isJob("17eb6180-04a0-4148-8756-07e5c051126g", "test_job_tracker.db"), True)

if __name__ == "__main__":
    unittest.main()