import argparse
import select
import socket
import sys
import json
import time

from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, MESSAGE, MESSAGE_TEXT, SENDER, RESPONSE_200, RESPONSE_400, DESTINATION, \
    EXIT
from common.utils import get_message, send_message

import logging
from logs import server_log_config
from app_decorators import Log

logger = logging.getLogger('server')

@Log(logger)
def process_client_message(message, messages_list, client, clients, user_names):
    """Receive message from client, check it.
    if presence message send response. If message append it to the  messages list,
    :param message: dict
    :return:
    """
    logger.debug(f'Разбор сообщения от клиента : {message}')

    if ACTION in message and message[ACTION] == PRESENCE \
            and TIME in message and USER in message:
        if message[USER][ACCOUNT_NAME] not in user_names.keys():
            user_names[message[USER][ACCOUNT_NAME]] = client
            send_message(client,  RESPONSE_200)
        else:
            response = RESPONSE_400
            response[ERROR] = 'The username is already in use'
            send_message(client, response)
            clients.remove(client)
            client.close()
        return
    elif ACTION in message and message[ACTION] == MESSAGE and \
            DESTINATION in message and TIME in message \
            and SENDER in message and MESSAGE_TEXT in message:
        messages_list.append(message)
        return
    elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
        # clients.remove(user_names[message[ACCOUNT_NAME]])
        # user_names[message[ACCOUNT_NAME]].close()
        # del user_names[message[ACCOUNT_NAME]]
        clients.remove(client)
        client.close()
        return
    else:
        response = RESPONSE_400
        response[ERROR] = 'Request is not correct.'
        send_message(client, response)
        return


def process_message(message, user_names, listen_socks):
    """Take message and send to certain user which is listening now.
    :param message: list of dicts
    :param user_names: dict
    :param listen_socks: list of dict
    :return: None
    """
    if message[DESTINATION] in user_names and user_names[message[DESTINATION]] in listen_socks:
        send_message(user_names[message[DESTINATION]], message)
        logger.info(f'Отправлено сообщение пользователю {message[DESTINATION]} '
                    f'от пользователя {message[SENDER]}.')
    elif message[DESTINATION] in user_names and user_names[message[DESTINATION]] not in listen_socks:
        raise ConnectionError
    else:
        logger.error(
            f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, или не в сети(не слушает.) '
            f'отправка сообщения невозможна.')


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
    clients = []
    messages = []
    user_names = dict() # {client_name: client_socket}

    logger.debug('Server: Старт приложения')

    listen_address, listen_port = arg_parser()

    logger.info(
        f'Запущен сервер, порт для подключений: {listen_port}, '
        f'адрес с которого принимаются подключения: {listen_address}. '
        f'Если адрес не указан, принимаются соединения с любых адресов.')


    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    transport.bind((listen_address, listen_port))
    transport.settimeout(0.5)
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
                    process_client_message(get_message(client_with_message), messages, client_with_message, clients, user_names)
                except:
                    logger.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                    clients.remove(client_with_message)

        for msg in messages:
            try:
                process_message(msg, user_names, send_data_list)
            except Exception:
                logger.info(f'Связь с клиентом с именем {msg[DESTINATION]} была потеряна')
                clients.remove(user_names[msg[DESTINATION]])
                del user_names[msg[DESTINATION]]
        messages.clear()

if __name__ == '__main__':
    main()

