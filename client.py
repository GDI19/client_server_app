import sys
import json
import socket
import time
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT
from common.utils import get_message, send_message

import logging
from logs import client_log_config

logger = logging.getLogger('client' )

def create_presence(account_name = 'Guest'):
    """
    Create presence of a client
    :param account_name: str
    :return: dict
    """
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER:{
            ACCOUNT_NAME: account_name
        }
    }
    return out


def process_ans(message):
    """
    Read the answer of the server
    :param message: dict
    :return: str
    """
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200: OK'
        return f'400: {message[ERROR]}'
    logger.error('Bad request')
    raise ValueError



def main():
    logger.debug('Client: Старт приложения')

    try:
        server_address = sys.argv[1]
        server_port = int(sys.argv[2])
        if server_port < 1024 or server_port > 65535:
            raise ValueError
    except IndexError:
        server_address = DEFAULT_IP_ADDRESS
        server_port = DEFAULT_PORT
        logger.info('No ip and/or port')
    except ValueError:
        logger.error('В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.connect((server_address, server_port))
    message_to_server = create_presence()
    send_message(transport, message_to_server)
    logger.info('socket: %s', transport)
    try:
        answer = process_ans(get_message(transport))
        logger.info(answer)
    except (ValueError, json.JSONDecodeError):
        logging.error('Не удалось декодировать сообщение сервера.')

    logger.debug('Client: Завершение приложения')

if __name__ == '__main__':
    main()