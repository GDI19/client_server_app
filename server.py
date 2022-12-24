import socket
import sys
import json
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT
from common.utils import get_message, send_message

import logging
from logs import server_log_config
from app_decorators import Log

logger = logging.getLogger('server')

@Log(logger)
def process_client_message(message):
    """
    Receive message from client, check it.
    :param message: dict
    :return: response (dict)
    """
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
        and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        logger.info('Request ok')
        return {RESPONSE: 200}

    logger.info('Bad Request')
    return{
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }

def main():
    """
    Lunch parameters from command line.
    If there are no parameters, it uses by default.
    command: server.py -p 8888 -a 127.0.0.1
    :return: None
    """
    logger.debug('Server: Старт приложения')
    try:
        if '-p' in sys.argv:
            listen_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            listen_port = DEFAULT_PORT
        if listen_port < 1024 or listen_port > 65535:
            raise ValueError
    except IndexError:
        #print('После параметра -\'p\' необходимо указать номер порта.')
        logger.error('После параметра -\'p\' необходимо указать номер порта.')
        sys.exit(1)
    except ValueError:
        logger.error('Номер порта может быть указано только в диапазоне от 1024 до 65535.')
        sys.exit(1)

    try:
        if '-a' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-p') + 1]
        else:
            listen_address = ''
    except IndexError:
        logger.error('После параметра \'- a\' необходимо указать адрес')
        sys.exit(1)

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    transport.bind((listen_address, listen_port))

    transport.listen(MAX_CONNECTIONS)

    while True:
        client, client_address = transport.accept()
        logger.info(f'Установлено соедение с ПК {client_address}')
        try:
            message_from_client = get_message(client)
            logger.debug(f'Получено сообщение {message_from_client}')
            print(message_from_client)

            response = process_client_message(message_from_client)
            logger.info(f'Cформирован ответ клиенту {response}')

            send_message(client, response)
            logger.debug(f'Соединение с клиентом {client_address} закрывается.')
            client.close()


        except json.JSONDecodeError:
            logger.error(f'Не удалось декодировать Json строку, '
                         f'полученную от клиента {client_address}. Соединение закрывается.')
            client.close()

        except ValueError:
            logger.error(f'От клиента {client_address} приняты некорректные данные. '
                         f'Соединение закрывается.')
            client.close()

if __name__ == '__main__':
    main()


