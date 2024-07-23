import logging
import os
import aiohttp

import contact_admin
import translate
from bs4 import BeautifulSoup
from config import db


async def get_status(username):
    url = f'https://fragment.com/?query={username}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/124.0.0.0 YaBrowser/24.6.0.0 Safari/537.36'
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                text = await response.text()
                status = await set_status(username, text)
                if status == 6:
                    status = await get_status_tme(username)
                return status
    except aiohttp.ClientError as e:
        logging.error(f'aiohttp.ClientError {e}')
        current_file = os.path.realpath(__file__)
        current_directory = os.path.dirname(current_file)
        await contact_admin.contact_admin(e=e, username=username, current_file=current_file,
                                          current_directory=current_directory,
                                          func_name='async def get_status(username):')
        return 6
    except Exception as e:
        logging.error(f'request error {e}')
        current_file = os.path.realpath(__file__)
        current_directory = os.path.dirname(current_file)
        await contact_admin.contact_admin(e=e, username=username, current_file=current_file,
                                          current_directory=current_directory,
                                          func_name='async def get_status(username):')
        return 6


async def set_status(username, text):
    bs = BeautifulSoup(text, 'html.parser')
    text = bs.getText()
    try:
        if f'@{username}\nUnavailable' in text:
            return 1
        elif f'@{username}\nTaken' in text:
            return 2
        elif f'@{username}\nOn auction' in text:
            return 3
        elif f'@{username}\nAvailable' in text:
            return 4
        elif f'@{username}\nSold' in text:
            return 5
    except Exception as e:
        logging.error(f'status error {e}')
        current_file = os.path.realpath(__file__)
        current_directory = os.path.dirname(current_file)
        await contact_admin.contact_admin(e=e, username=username, current_file=current_file,
                                          current_directory=current_directory,
                                          func_name='async def set_status(username, text)')
        return 6


async def get_status_tme(username):
    url = f'https://t.me/{username}'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                text = await response.text()
                status = await set_status_tme(username, text)
                return status
    except aiohttp.ClientError as e:
        logging.error(f'aiohttp.ClientError {e}')
        current_file = os.path.realpath(__file__)
        current_directory = os.path.dirname(current_file)
        await contact_admin.contact_admin(e=e, username=username, current_file=current_file,
                                          current_directory=current_directory,
                                          func_name='async def get_status(username):')
        return 6
    except Exception as e:
        logging.error(f'request error {e}')
        current_file = os.path.realpath(__file__)
        current_directory = os.path.dirname(current_file)
        await contact_admin.contact_admin(e=e, username=username, current_file=current_file,
                                          current_directory=current_directory,
                                          func_name='async def get_status(username):')
        return 6


async def set_status_tme(username, text):
    try:
        if 'you can view and join <br><strong>' in text:
            return 2
        elif 'you can contact <br><strong>' in text:
            return 2
        elif 'you can contact <a class="tgme_username_link"' in text:
            return 1
    except Exception as e:
        logging.error(f'status error {e}')
        current_file = os.path.realpath(__file__)
        current_directory = os.path.dirname(current_file)
        await contact_admin.contact_admin(e=e, username=username, current_file=current_file,
                                          current_directory=current_directory,
                                          func_name='async def set_status(username, text)')
        return 6


async def get_text(username, user_language, status):
    auc_url = f'https://fragment.com/username/{username}'
    return translate.statuses(user_language, username, auc_url, status)


async def get_status_and_answer(username, user_language, user_id):
    status = await get_status(username)
    answer = await get_text(username, user_language, status)
    db.set_username_checked(user_id, username)
    return status, answer
