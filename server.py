import argparse
import select
import socket
import sys
import json
import time

from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, MESSAGE, MESSAGE_TEXT, SENDER
from common.utils import get_message, send_message

import logging
from logs import server_log_config
from app_decorators import Log

logger = logging.getLogger('server')

@Log(logger)
def process_client_message(message, messages_list, client):
    """Receive message from client, check it.
    if presence message send response. If message append it to the  messages list,
    :param message: dict
    :return:
    """
    logger.debug(f'Разбор сообщения от клиента : {message}')

    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
        and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        send_message(client,  {RESPONSE: 200})
        return
    elif ACTION in message and message[ACTION] == MESSAGE and TIME in message \
        and MESSAGE_TEXT in message:
        messages_list.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
        return
    else:
        send_message(client, {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    })
        return

@Log(logger)
def arg_parser():
    """Command line parser"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    if not 1023 < listen_port < 65536:
        logger.critical(
            f'Попытка запуска сервера с указанием неподходящего порта '
            f'{listen_port}. Допустимы адреса с 1024 до 65535.')
        sys.exit(1)

    return listen_address, listen_port

def main():
    """
    Lunch parameters from command line.
    If there are no parameters, it uses by default.
    command: server.py -p 8888 -a 127.0.0.1
    :return: None
    """
    logger.debug('Server: Старт приложения')

    listen_address, listen_port = arg_parser()

    logger.info(
        f'Запущен сервер, порт для подключений: {listen_port}, '
        f'адрес с которого принимаются подключения: {listen_address}. '
        f'Если адрес не указан, принимаются соединения с любых адресов.')


    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # transport.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    transport.bind((listen_address, listen_port))
    transport.settimeout(0.5)

    clients = []
    messages = []

    transport.listen(MAX_CONNECTIONS)

    while True:
        try:
            client, client_address = transport.accept()
        except OSError as err:
            print(err.errno) # The error number returns None because it's just a timeout
            pass
        else:
            logger.info(f'Установлено соедение с ПК {client_address}')
            clients.append(client)

        recv_data_list = []
        send_data_list = []
        err_list = []

        # check for waiting clients
        try:
            if clients:
                recv_data_list, send_data_list, err_list = select.select(clients, clients, [], 0)
        except OSError:
            pass

        if recv_data_list:
            for client_with_message in recv_data_list:
                try:
                    process_client_message(get_message(client_with_message), messages, client_with_message)
                except:
                    logger.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                    clients.remove(client_with_message)

        if messages and send_data_list:
            message = {
                ACTION: MESSAGE,
                SENDER: messages[0][0],
                TIME: time.time(),
                MESSAGE_TEXT: messages[0][1]
            }
            del messages[0]

            for waiting_client in send_data_list:
                try:
                    send_message(waiting_client, message)
                except:
                    logger.info(f'Клиент {waiting_client.getpeername()} отключился от сервера.')
                    waiting_client.close()
                    clients.remove(waiting_client)

if __name__ == '__main__':
    main()

