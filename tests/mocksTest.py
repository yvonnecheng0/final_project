import sys
import os

# Adjusts the sys.path to include the parent directory -- importing listings wasn't working otherwise
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from mock_interviews import *
from flask import Flask, jsonify, request

class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_generate_question(self):
        response = self.app.post('/generate_question')
        self.assertEqual(response.status_code, 200)
        self.assertIn('question', response.json)

    def test_get_feedback(self):
        response = self.app.post('/get_feedback', json={'answer': 'This is a test answer.'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('feedback', response.json)

if __name__ == '__main__':
    unittest.main()

