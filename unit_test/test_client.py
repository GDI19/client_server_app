import sys
import os
import unittest
sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE
from client import create_presence, process_ans

class TestClient(unittest.TestCase):

    def test_200_ans(self):
        self.assertEqual(process_ans({RESPONSE: 200}), '200: OK')

    def test_400_ans(self):
        self.assertEqual(process_ans({RESPONSE: 400, ERROR: 'Bad Request'}), '400: Bad Request')

    def test_no_responce(self):
        self.assertRaises(ValueError, process_ans, {ERROR: 'Bad Request'})

if __name__ == '__main__':
    unittest.main()