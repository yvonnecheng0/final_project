import sys
import os

# Adjusts the sys.path to include the parent directory -- importing listings wasn't working otherwise
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from databases import *
import unittest


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
        actual = register_user("Sonya4U", "newEmail@bob.net", "newPassword", db="test_job_tracker.db")
        self.assertEqual(actual, 1)

    # Tests that reseting the database deletes the tables within too 
    def testDeletion(self):
        reset_all("test_job_tracker.db")
        with self.assertRaises(sqlite3.OperationalError) as cm:
            register_user("Sonya4U", "newEmail@bob.net", "newPassword", db="test_job_tracker.db")
        self.assertIn("no such table: users", str(cm.exception))
    


if __name__ == "__main__":
    unittest.main()