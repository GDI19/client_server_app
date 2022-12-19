import sys
import os
import unittest
import json
sys.path.insert(0, os.path.join(os.getcwd(), '..'))
print(sys.path)
from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE, ENCODING
from common.utils import get_message, send_message


class TestSocket:
    """
    Replace methods recv & send of the real socket
    Uses dictionary to test the receiving and sending message.
    Remember the received message and the message after transformations
    """
    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.received_message =None

    def send(self, message_to_send):
        """
        from dictionary convert to json then encode message,
        :param message_to_send: dict
        :return: None
        """
        json_test_message = json.dumps(self.test_dict)
        self.encoded_message = json_test_message.encode(ENCODING)
        self.received_message = message_to_send

    def recv(self, max_len):
        """
        Receive dictionary from socket encode it
        :param max_len:
        :return:
        """
        json_test_message = json.dumps(self.test_dict)
        return json_test_message.encode(ENCODING)


class TestUtils(unittest.TestCase):

    test_dict_send = {
        ACTION: PRESENCE,
        TIME: 111111.111111,
        USER: {
            ACCOUNT_NAME: 'testik'
        }
    }
    test_dict_recv_ok = {RESPONSE: 200}
    test_dict_recv_err = {RESPONSE: 400, ERROR: 'Bad Request'}

    def test_send_message_true(self):
        """ Test sending message """
        test_socket = TestSocket(self.test_dict_send)
        send_message(test_socket, self.test_dict_send)
        self.assertEqual(test_socket.encoded_message, test_socket.received_message)

    def test_send_message_with_error(self):
        test_socket = TestSocket(self.test_dict_send)
        # <<self.assertRaises(TypeError, test_function, args)>>
        self.assertRaises(TypeError, send_message, test_socket, "wrong_dictionary_to_send")

    def test_get_message_ok(self):
        test_socket = TestSocket(self.test_dict_recv_ok)
        recv_message = get_message(test_socket)
        self.assertEqual(recv_message, self.test_dict_recv_ok)

    def test_get_message_error(self):
        test_socket = TestSocket(self.test_dict_recv_err)
        recv_message = get_message(test_socket)
        self.assertEqual(recv_message, self.test_dict_recv_err)


if __name__ == '__main__':
    unittest.main()