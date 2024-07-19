import sys
import os

# Adjusts the sys.path to include the parent directory -- importing listings wasn't working otherwise
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from databases import *
import unittest
from listingsTest import JOBS_URL
from listings import *

TEST_DB = "test_job_tracker.db"

class TestUsers(unittest.TestCase):

    mock_users = {"Rodya1866": "38JEbnjw@1H!!", "Sonya4U": "4Jewo0323w9eq", "DunyaIsSad": "0k2oL@j4skjw", "PorfiryLives": "heijoJO@092e"}

    def setUp(self):
        create_tables(TEST_DB)
        for user in self.mock_users.keys():
            register_user(user, user+"@fake.edu", self.mock_users[user], db=TEST_DB)

    # Tests that users are actually being added to the table
    def testPresense(self):
        self.setUp()
        actual = is_user("DunyaIsSad", db=TEST_DB)

        self.assertEqual(actual, True)
        reset_all(TEST_DB)
    
    # Tests that duplicate usernames are not possible
    def testBadUser(self):
        self.setUp()
        attempt1 = register_user("Sonya4U", "newEmail@bob.net", "newPassword", db=TEST_DB)

        self.assertEqual(attempt1, 1)
        reset_all(TEST_DB)

    # Tests that removed old users can be replaced
    def testRemoveUser(self):
        self.setUp()
        remove_user("Sonya4U", db=TEST_DB)
        attempt2 = register_user("Sonya4U", "newEmail@bob.net", "newPassword", db=TEST_DB)

        self.assertEqual(attempt2, None)
        reset_all(TEST_DB)
        
    # Tests that reseting the database deletes the tables within too 
    def testDeletion(self):
        reset_all(TEST_DB)
        with self.assertRaises(sqlite3.OperationalError) as cm:
            register_user("Sonya4U", "newEmail@bob.net", "newPassword", db=TEST_DB)

        self.assertIn("no such table: users", str(cm.exception))
        reset_all(TEST_DB)

    # Tests that database is gone from file paths
    def testGoneDB(self):
        create_tables(TEST_DB)
        reset_all(TEST_DB)

        self.assertFalse(os.path.exists(TEST_DB), "Database file should not exist")

class TestJobs(unittest.TestCase):
    
    # Tests adding a single job
    def testAddJob(self):
        create_tables(TEST_DB)
        listings = fetch_listings(JOBS_URL)

        dic = format_listing(listings[0])
        add_job(dic["posted"], dic["updated"], dic["company"], dic["title"], 
            dic["season"], dic["sponsorship"], dic["active"], dic["locations"], dic["url"], db=TEST_DB)
        
        self.assertEqual(isJob("Dunder Mifflin Paper Company", "Assistant to the Regional Manager", "Summer", TEST_DB), True)
        reset_all(TEST_DB)

    # Tests adding multiple jobs
    def testAddMultipleJobs(self):
        create_tables(TEST_DB)
        listings = fetch_listings(JOBS_URL)
        for listing in listings:
            lDict = format_listing(listing)
            quick_add_job(lDict, TEST_DB)

        self.assertEqual(isJobID(3, TEST_DB), True)
        reset_all(TEST_DB)

class testApplications(unittest.TestCase):

    mock_users = {"Karma4Me": "332feedH!!", "L00k18": "4Jejmsoww9eq", "oH30D": "jelo@j4skjw", "yoUUUw": "hebjJO@092e"}
    
    def setUp2(self):
        reset_all(TEST_DB)
        create_tables(TEST_DB)
        register_user("NickiFan", "areYouAFan@like.net", "dontp1ay", db=TEST_DB)
        listings = fetch_listings(JOBS_URL)
        for listing in listings:
            lDict = format_listing(listing)
            quick_add_job(lDict, db=TEST_DB)
        for user in self.mock_users.keys():
            register_user(user, user+"@fake.edu", self.mock_users[user], db=TEST_DB)

    # Tests adding an application
    def testAddApp(self):
        self.setUp2()
        add_application(1, 1, "2024-07-19 15:51:34 UTC", "Ready to Apply", "2024-07-19 18:30:34 UTC",
                        "Cardi", "t09skd@hotmail.com", db=TEST_DB)
        
        self.assertEqual(isApplication(1, 1, db=TEST_DB), True)
        reset_all(TEST_DB)
    
    # Tests that add_application returns 1 if there is no user in users with that id or username
    def testNoUser(self):
        self.setUp2()
        x = add_application(9999, 1, "2024-07-19 15:51:34 UTC", "Ready to Apply", "2024-07-19 18:30:34 UTC",
                        "Cardi", "t09skd@hotmail.com", db=TEST_DB)
        
        self.assertEqual(x, 1)
        reset_all(TEST_DB)
    
    # Tests that add_application returns 2 if there is no job in jobs with that id
    def testNoJob(self):
        self.setUp2()
        x = add_application(1, "17eolivia80-04a0-4148-8756-07jjdjww23f", "2024-07-19 15:51:34 UTC", "Ready to Apply", "2024-07-19 18:30:34 UTC",
                        "Cardi", "t09skd@hotmail.com", db=TEST_DB)
        
        self.assertEqual(x, 2)
        reset_all(TEST_DB)
    
    def testQuickAddApp(self):
        self.setUp2()
        quick_add_app(1, 1, TEST_DB)
        self.assertEqual(isApplication(1, 1, db=TEST_DB), True)
        reset_all(TEST_DB)

    def testUpdateApp(self):
        self.setUp2()
        quick_add_app(1, 1, TEST_DB)
        quick_add_app(1, 2, TEST_DB)

        update_application_status(2, "OA Offered", TEST_DB)
        self.assertEqual(get_status(2, TEST_DB), "OA Offered")

        update_recruiter_info(2, "Lee", "sweetpea@company.name", TEST_DB)
        self.assertEqual(get_recruiter_email(2, TEST_DB), "sweetpea@company.name")

if __name__ == "__main__":
    unittest.main()
    