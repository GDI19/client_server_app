import os
import logging


PATH = os.path.dirname(os.path.abspath(__file__))
server_client_log_path = os.path.join(PATH, 'server-client.log')

logger = logging.getLogger('client')

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(message)s ")

# 1 common log
file_handler = logging.FileHandler(server_client_log_path, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.setLevel(logging.DEBUG)

# отладка
if __name__ == '__main__':
    logger.critical('Критическая ошибка')
    logger.error('Ошибка')
    logger.debug('Отладочная информация')
    logger.info('Информационное сообщение')