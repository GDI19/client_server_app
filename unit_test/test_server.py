import unittest
import socket
import sys
import json
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT
from server import process_client_message


class Test_server(unittest.TestCase):

    def setUp(self) -> None:
        self.message_from_client = {
            ACTION: PRESENCE,
            TIME: 1.1,
            USER: {ACCOUNT_NAME: 'Guest'}
        }

        self.err_dict = {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }
        self.ok_dict = {RESPONSE: 200}

    def test_check_ok(self):
        self.assertEqual(process_client_message(self.message_from_client), self.ok_dict)

    def test_no_action(self):
        self.assertEqual(process_client_message({TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}}), self.err_dict)

    def test_wrong_action(self):
        self.assertEqual(process_client_message({ACTION: 'wrong', TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}}), self.err_dict)

    def test_no_time(self):
        self.assertEqual(process_client_message({ACTION: PRESENCE, USER: {ACCOUNT_NAME: 'Guest'}}), self.err_dict)

    def test_wrong_user(self):
        self.assertEqual(process_client_message({ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'This is not Guest'}}), self.err_dict)

    def test_no_user(self):
        self.assertEqual(process_client_message({ACTION: PRESENCE, TIME: 1.1}), self.err_dict)


if __name__ == '__main__':
    unittest.main()