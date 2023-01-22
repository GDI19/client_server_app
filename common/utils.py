import json
from common.variables import MAX_PACKAGE_LENGTH, ENCODING
from app_decorators import Log

@Log()
def get_message(client):
    """
    Receive bytes and decode message.
    :param client: client
    :return: dict or ValueError
    """
    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        if isinstance(json_response, str):
            response = json.loads(json_response)
            if isinstance(response, dict):
                return response
            raise ValueError
        raise ValueError
    raise ValueError


@Log()
def send_message(sock, message):
    """
    Encode and send message.
    Receive dict convert it to str then to bytes.
    :param sock: socket
    :param message: dict
    :return: None
    """
    if not isinstance(message, dict):
        raise TypeError
    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock.send(encoded_message)
