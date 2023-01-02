import argparse
import sys
import json
import socket
import time
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT, MESSAGE, MESSAGE_TEXT, SENDER
from common.utils import get_message, send_message
from app_decorators import Log
import logging
from logs import client_log_config

logger = logging.getLogger('client' )

@Log(logger)
def message_from_server(message):
    """Функция - обработчик сообщений других пользователей, поступающих с сервера"""
    if ACTION in message and message[ACTION] == MESSAGE and \
            SENDER in message and MESSAGE_TEXT in message:
        print(f'Получено сообщение от пользователя '
              f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
        logger.info(f'Получено сообщение от пользователя '
                    f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
    else:
        logger.error(f'Получено некорректное сообщение с сервера: {message}')


@Log(logger)
def create_presence(account_name = 'Guest'):
    """Create presence of a client
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
    logger.debug(f'Created message-presence {PRESENCE} of the user - {account_name}')
    return out

def create_message(sock, account_name = 'Guest'):
    """
    Create message of a client
    :param account_name: str
    :return: dict
    """
    message_text = input('Please. Enter your message or \'q\' for exit: \n')
    if message_text == 'q':
        sock.close()
        logger.info('Closing client due to user command.')
        print('Thank you for using our app!')
        sys.exit(0)
    message_to_send = {
        ACTION: MESSAGE,
        TIME: time.time(),
        ACCOUNT_NAME: account_name,
        MESSAGE_TEXT: message_text
        }

    logger.debug(f'Created message {message_to_send} of user = {account_name}')
    return message_to_send

@Log(logger)
def process_ans(message):
    """ Read the answer of the server
    :param message: dict
    :return: str
    """
    logger.debug(f'Разбор сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200: OK'
        return f'400: {message[ERROR]}'
    # elif ACTION in message and message[ACTION] == MESSAGE and SENDER in message and MESSAGE_TEXT in message:
    #     print(f'Получено сообщение от пользователя '
    #           f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
    #     logger.info(f'Получено сообщение от пользователя '
    #                 f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
    # else:
    #     logger.error(f'Получено некорректное сообщение с сервера: {message}')



def arg_parser():
    """Parse command line return 3 parameters"""
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-m', '--mode', default='send', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_mode = namespace.mode

    if not 1023 < server_port < 65536:
        logger.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. '
            f'Допустимы адреса с 1024 до 65535. Клиент завершается.')
        sys.exit(1)

    if client_mode not in ('listen', 'send'):
        logger.critical(f'Указан недопустимый режим работы {client_mode}, '
                        f'допустимые режимы: listen , send')
        sys.exit(1)

    return server_address, server_port, client_mode

def main():
    logger.debug('Client: Старт приложения')

    server_address, server_port, client_mode = arg_parser()

    logger.info(f'Запущен клиент с парамертами: адрес сервера: '
          f'{server_address}, порт: {server_port}')

    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        message_to_server = create_presence()
        send_message(transport, message_to_server)
        answer = process_ans(get_message(transport))
        logger.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print(f'Установлено соединение с сервером.')
    except json.JSONDecodeError:
        logger.error('Не удалось декодировать полученную Json строку.')
        sys.exit(1)
    except ConnectionRefusedError:
        logger.critical(
            f'Не удалось подключиться к серверу {server_address}:{server_port}, '
            f'конечный компьютер отверг запрос на подключение.')
        sys.exit(1)
    else:
        if client_mode == 'send':
            print('Режим работы - отправка сообщений.')
        else:
            print('Режим работы - приём сообщений.')

        while True:
            if client_mode == 'send':
                try:
                    send_message(transport, create_message(transport))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                        logger.error(f'Соединение с сервером {server_address} было потеряно.')
                        sys.exit(1)
            elif client_mode == 'listen':
                try:
                    message_from_server(get_message(transport))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                        logger.error(f'Соединение с сервером {server_address} было потеряно.')
                        sys.exit(1)

    # logger.debug('Client: Завершение приложения')

if __name__ == '__main__':
    main()