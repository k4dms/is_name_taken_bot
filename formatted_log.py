import logging

from config import log_users, log_admins


# Включение отключение в конфиге
def admin_log(func, *args, **kwargs) -> None:
    if log_admins:
        info = f'ADMIN: `{func.__name__}` '
        for index, arg in enumerate(args):
            info += f'`{arg}` '
        for kwarg in kwargs:
            info += f'`{kwarg}` = `{kwargs[kwarg]}` '
        logging.info(info)


# Включение отключение в конфиге
def user_log(func, *args, **kwargs) -> None:
    if log_users:
        info = f'USER: `{func.__name__}` '
        for index, arg in enumerate(args):
            info += f'`{arg}` '
        for kwarg in kwargs:
            info += f'`{kwarg}` = `{kwargs[kwarg]}` '
        logging.info(info)
