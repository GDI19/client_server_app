import logging
import logging.handlers
import os

PATH = os.path.dirname(os.path.abspath(__file__))
only_server_log_path = os.path.join(PATH, 'server.log')
server_client_log_path = os.path.join(PATH, 'server-client.log')

logger = logging.getLogger('server')

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(message)s ")

file_handler = logging.FileHandler(server_client_log_path, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

file_handler_server_time_rotate = logging.handlers.TimedRotatingFileHandler(only_server_log_path, when='D', interval=1,
                                                          backupCount=2, encoding='utf-8')
file_handler_server_time_rotate.setLevel(logging.DEBUG)
file_handler_server_time_rotate.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(file_handler_server_time_rotate)
logger.addHandler(console_handler)

logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    logger.critical('Критическая ошибка')
    logger.error('Ошибка')
    logger.debug('Отладочная информация')
    logger.info('Информационное сообщение')
