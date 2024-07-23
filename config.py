import logging
import os
import sys

from aiogram import Bot, Dispatcher
import BotDB

project_folder = os.path.dirname(__file__)

data_path = os.path.join(project_folder, 'data')
database_file_path = os.path.join(data_path, 'database.db')
log_file_path = os.path.join(data_path, 'bot.log')
api_token = 'api_token'
log_users = True
log_admins = True
fragment_request_interval = 300
db_request_interval = 30
admin_id = 12345678
admin_password = 'password'

args = sys.argv
if len(args) > 1:
    try:
        for index, arg in enumerate(args):
            if index <= len(args) - 1:
                next_arg = args[index + 1]
                print(index, arg, next_arg)
                if arg.lower() == 'main.py':
                    continue
                elif arg == '-dp':
                    data_path = os.path.join(data_path, next_arg)
                elif arg == '-df':
                    database_file_path = next_arg
                elif arg == '-lf':
                    log_file_path = os.path.join(data_path, next_arg)
                elif arg == '-t':
                    api_token = os.path.join(data_path, next_arg)
                elif arg == '-lu':
                    log_users = True if next_arg.lower() in ['true', 'yes', '1'] else False
                elif arg == '-la':
                    log_admins = True if next_arg.lower() in ['true', 'yes', '1'] else False
                elif arg == '-fi':
                    fragment_request_interval = int(next_arg)
                elif arg == '-di':
                    db_request_interval = int(next_arg)
                elif arg == '-ap':
                    admin_password = next_arg
                elif arg == '-ai':
                    admin_id = int(next_arg)
                else:
                    logging.error(f'Unknown argument: {arg}')
    except Exception as e:
        logging.error(f'Argument error: {e}')

# Создание директорий
if not os.path.exists(data_path):
    os.makedirs(data_path)
if not os.path.exists(log_file_path):
    open(log_file_path, "w").close()
if not os.path.exists(database_file_path):
    open(database_file_path, "w").close()

# Запуск с выбранными настройками
logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s - %(asctime)s - %(name)s - %(message)s',
                    handlers=[
                        logging.FileHandler(log_file_path),
                        logging.StreamHandler()
                    ])

print(f'-t api_token = {api_token}'
      f'\n-ap admin_password = {admin_password}'
      f'\n-ai admin_id = {admin_id} '
      f'\n-dp data_path = {data_path} '
      f'\n-lf log_file_path = {log_file_path}'
      f'\n-df database_file_path = {database_file_path}'
      f'\n-lu log_users = {log_users}'
      f'\n-la log_admins = {log_admins}'
      f'\n-fi fragment_request_interval = {fragment_request_interval}'
      f'\n-di db_request_interval = {db_request_interval}\n')

# Инициализация бота и диспетчера
db = BotDB.BotDB(database_file_path)
bot = Bot(token=api_token)
dp = Dispatcher()
