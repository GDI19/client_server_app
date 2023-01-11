import argparse
import sys
import json
import socket
import threading
import time
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT, MESSAGE, MESSAGE_TEXT, SENDER, DESTINATION, EXIT
from common.utils import get_message, send_message
from app_decorators import Log
import logging
from logs import client_log_config

logger = logging.getLogger('client' )


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
    destination = input('Please, enter the recipient of the message here: ')
    print('-'* 15)
    message_text = input('Please. Enter your message: \n')
    message_to_send = {
        ACTION: MESSAGE,
        SENDER: account_name,
        DESTINATION: destination,
        TIME: time.time(),
        MESSAGE_TEXT: message_text
        }
    logger.debug(f'Created message {message_to_send} of user = {account_name} to {destination}')
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


@Log(logger)
def message_from_server(sock, client_name):
    """Функция - обработчик сообщений других пользователей, поступающих с сервера"""
    while True:
        try:
            message = get_message(sock)
            if ACTION in message and message[ACTION] == MESSAGE and SENDER in message \
                    and DESTINATION in message and message[DESTINATION] == client_name \
                    and MESSAGE_TEXT in message:
                print(f'\nПолучено сообщение от пользователя '
                      f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                logger.info(f'Получено сообщение от пользователя '
                            f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
            else:
                logger.error(f'Получено некорректное сообщение с сервера: {message}')
        except (OSError, ConnectionError, ConnectionAbortedError,
                ConnectionResetError, json.JSONDecodeError):
            logger.critical(f'Потеряно соединение с сервером.')
            break

def print_help():
    """Функция выводящяя справку по использованию"""
    print(f'Available commands: \n'
            f'w - to write & send message \n'
            f'q - to quit \n'
            f'help - more options\n')


def create_exit_message(account_name):
    """Функция создаёт словарь с сообщением о выходе"""
    return {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: account_name
    }

def user_interactive(sock, client_name):
    print(f'{client_name}, welcome to Client-Server App.')
    print_help()
    while True:
        command = input('Please enter your command: ')
        if command.lower() == 'w':
            msg = create_message(sock, client_name)
            try:
                send_message(sock, msg)
                logger.info(f'Отправлено сообщение')
            except Exception as e:
                print(e)
                logger.critical('Потеряно соединение с сервером.')
                sys.exit(1)
        elif command.lower() == 'q':
            send_message(sock, create_exit_message(client_name))
            logger.info('Closing client due to user command.')
            print('Thank you for using our app!')
            # Задержка неоходима, чтобы успело уйти сообщение о выходе
            time.sleep(0.5)
            break
        elif command.lower() == 'help':
            print_help()
        else:
            print('Command is not correct')



def arg_parser():
    """Parse command line return 3 parameters"""
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--user_name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.user_name

    if not 1023 < server_port < 65536:
        logger.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. '
            f'Допустимы адреса с 1024 до 65535. Клиент завершается.')
        sys.exit(1)

    return server_address, server_port, client_name

def main():
    logger.debug('Client: Старт приложения')

    server_address, server_port, client_name = arg_parser()
    if not client_name:
        client_name = input('Введите имя пользователя: ')

    logger.info(f'Запущен клиент с парамертами: адрес сервера: '
          f'{server_address}, порт: {server_port}, имя пользователя: {client_name}')

    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        message_to_server = create_presence(client_name)
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
        receiver = threading.Thread(target=message_from_server, args=(transport, client_name))
        receiver.daemon = True
        receiver.start()

        user_interface = threading.Thread(target=user_interactive, args=(transport, client_name))
        user_interface.daemon = True
        user_interface.start()

        # Watchdog основной цикл, если один из потоков завершён,
        # то значит или потеряно соединение или пользователь
        # ввёл exit. Поскольку все события обработываются в потоках,
        # достаточно просто завершить цикл.
        while True:
            time.sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break


if __name__ == '__main__':
    main()