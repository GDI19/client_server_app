import logging
from functools import wraps
import inspect

# # function decorator
# def log(func_to_log):
#     def wrapper(*args, **kwargs):
#         # some code before
#         result = func_to_log(*args, **kwargs)
#         # some code after
#         return result
#     return wrapper


class Log:
    """
    Receive logger from client or server. From utils logger is None
    """
    def __init__(self, logger = None):
        self.logger = logger

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            parent_func_name = inspect.currentframe().f_back.f_code.co_name
            module_name = inspect.currentframe().f_back.f_code.co_filename.split('/')[-1]

            if self.logger == None:
                logger_name = module_name.replace('.py', '')
                self.logger = logging.getLogger(logger_name)

            self.logger.debug(f'Function {func.__name__} ({args}, {kwargs})'
                              f'was called from  {module_name} - {parent_func_name}')

            result = func(*args, **kwargs)
            return result
        return wrapper
