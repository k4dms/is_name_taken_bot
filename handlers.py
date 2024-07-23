import asyncio
import logging
import os

from aiogram import types
from aiogram.filters.command import Command
from aiogram.types import FSInputFile
from aiogram import F
import keyboards
import notifications
import username_status
import formatted_log
from config import db, dp, bot, admin_password, database_file_path, log_file_path
import formatted_time
import translate
import username_validator


async def main():
    """
    Основная асинхронная функция, запускающая опрос бота.
    """
    await dp.start_polling(bot)


@dp.message(F.text == 'start')
@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    """
    Обработчик команды /start.
    """
    user_id = message.from_user.id
    user_exists = db.user_exists(user_id)
    if user_exists:
        await default_message(message)
        await set_last_message_date(user_id)
    else:
        await set_language_request(message)
    formatted_log.user_log(cmd_start, user_exists=user_exists, user_id=user_id)


@dp.message(Command('language'))
async def set_language_request(message: types.Message):
    """
    Обработчик команды /language для выбора языка.
    """
    await message.answer('Hi, choose a language that is convenient for you to work with me!\n\n'
                         'Привет, выбери язык, на котором тебе удобно работать со мной!',
                         reply_markup=await keyboards.language())
    formatted_log.user_log(set_language_request)


@dp.message(F.text == 'English')
@dp.message(F.text == 'Русский')
async def set_language_answer(message: types.Message):
    """
    Обработчик выбора языка.
    """
    user_id = message.from_user.id
    user_language = 'EN' if message.text == 'English' else 'RU'
    user_exists = db.user_exists(user_id)
    if user_exists:
        db.set_user_language(user_id, user_language)
        await default_message(message)
    else:
        await add_user_in_db(message, user_language)
    formatted_log.user_log(set_language_answer, user_exists=user_exists, user_id=user_id, user_language=user_language)


async def add_user_in_db(message: types.Message, user_language: str):
    """
    Добавляет нового пользователя в базу данных.
    """
    user_id = message.from_user.id
    username = message.from_user.username
    user_first_name = message.from_user.full_name
    time = formatted_time.get_time_now()
    db.add_user(user_id, username, user_first_name, user_language, time)
    await default_message(message)
    formatted_log.user_log(add_user_in_db, user_id=user_id, user_first_name=user_first_name,
                           user_language=user_language, time=time, username=username)


async def default_message(message: types.Message):
    """
    Отправляет сообщение по умолчанию пользователю.
    """
    user_id = message.from_user.id
    await set_last_message_date(user_id)
    user_language = db.get_user_language(user_id)
    active_notifications = db.user_have_active_notifications(user_id)
    if active_notifications:
        await message.answer(translate.default_message(user_language),
                             reply_markup=await keyboards.manage_notifications(user_language))
    else:
        await message.answer(translate.default_message(user_language),
                             reply_markup=types.ReplyKeyboardRemove())
    formatted_log.user_log(default_message, user_id=user_id, user_language=user_language,
                           active_notifications=active_notifications)


@dp.message(F.text[0] == '@')
async def username_handler(message: types.Message):
    """
    Обработчик сообщений, начинающихся с @.
    """
    user_id = message.from_user.id
    await set_last_message_date(user_id)
    user_exists = db.user_exists(user_id)
    if user_exists:
        username = message.text[1:]
        await username_check(message, username)
    else:
        await cmd_start(message)
    formatted_log.user_log(username_handler, user_exists=user_exists, user_id=user_id)


async def username_check(message: types.Message, username: str):
    """
    Проверка доступности имени пользователя.
    """
    user_id = message.from_user.id
    await set_last_message_date(user_id)
    user_language = db.get_user_language(user_id)
    is_name_valid, error = username_validator.is_name_valid(username, user_language)
    time = formatted_time.get_time_now()
    status = 6
    answer = ''
    if not is_name_valid:
        await message.answer(translate.username_check_error_occurred(user_language, error),
                             reply_markup=await keyboards.set_notification_not_valid_name(user_language))
    else:
        status, answer = await username_status.get_status_and_answer(username, user_language, user_id)
        db.add_history(user_id, username, status, time)
        if status != 1 and status != 6:
            db.set_username_checked(user_id, username)
            await message.answer(translate.username_check_offer(user_language, answer),
                                 reply_markup=await keyboards.set_notification_offer(user_language))
        else:
            await message.answer(answer, reply_markup=types.ReplyKeyboardRemove())
    formatted_log.user_log(username_check, user_id=user_id, user_language=user_language,
                           is_name_valid=is_name_valid, error=error, time=time, status=status,
                           answer=answer)


@dp.message(F.text == 'Close')
@dp.message(F.text == 'Закрыть')
async def cmd_close(message: types.Message):
    """
    Обработчик команды закрытия.
    """
    user_id = message.from_user.id
    await set_last_message_date(user_id)
    await default_message(message)
    formatted_log.user_log(cmd_close, user_id=user_id)


@dp.message(Command('rules'))
@dp.message(F.text == 'Правила')
@dp.message(F.text == 'Rules')
async def rules(message: types.Message):
    """
    Обработчик команды /rules.
    """
    await set_last_message_date(message.from_user.id)
    user_language = db.get_user_language(message.from_user.id)
    await message.answer(translate.cmd_rules(user_language),
                         reply_markup=types.ReplyKeyboardRemove())
    await default_message(message)
    formatted_log.user_log(rules, user_language=user_language)


@dp.message(F.text == 'Установить уведомление')
@dp.message(F.text == 'Set notify')
async def button_notify(message: types.Message):
    """
    Обработчик кнопки установки уведомления.
    """
    user_id = message.from_user.id
    user_exists = db.user_exists(user_id)
    if user_exists:
        username = db.get_username_checked(user_id)
        user_language = db.get_user_language(user_id)
        status = db.get_username_status_from_history(username, user_id)
        is_notify_exists = await notifications.is_notify_exists(user_id, username)
        time = formatted_time.get_time_now()
        if not is_notify_exists:
            await notifications.add_notify(user_id, username, 1, status, time)
            await message.answer(translate.set_notify(user_language),
                                 reply_markup=types.ReplyKeyboardRemove())
        else:
            await message.answer(translate.set_notify_fail(user_language),
                                 reply_markup=await keyboards.set_notification_fail(user_language))
        formatted_log.user_log(button_notify, user_id=user_id, user_language=user_language, time=time,
                               status=status, is_notify_exists=is_notify_exists)
    await default_message(message)
    formatted_log.user_log(button_notify, user_id=user_id, user_exists=user_exists)


@dp.message(F.text == 'Manage notifications')
@dp.message(F.text == 'Управление уведомлениями')
@dp.message(Command('notify'))
async def manage_notifications(message: types.Message):
    """
    Обработчик команды /notify для управления уведомлениями.
    """
    user_id = message.from_user.id
    await set_last_message_date(user_id)
    user_language = db.get_user_language(user_id)
    active_notifications = db.user_have_active_notifications(user_id)
    notifications_list = []
    if active_notifications:
        notifications_list = db.get_user_notifications(user_id)
        if notifications_list:
            await message.answer(translate.manage_notifications(user_language),
                                 reply_markup=types.ReplyKeyboardRemove())
            await message.answer(translate.notifications_manage(user_language),
                                 reply_markup=await keyboards.remove_notification(notifications_list, user_language))
        else:
            await message.answer(translate.no_notifications(user_language))
            await default_message(message)
    else:
        await message.answer(translate.no_notifications(user_language))
        await default_message(message)
    formatted_log.user_log(manage_notifications, user_id=user_id, user_language=user_language,
                           active_notifications=active_notifications,
                           notifications_list=notifications_list)


@dp.callback_query(lambda c: c.data.startswith('remove_notification '))
async def remove_notification(callback_query: types.CallbackQuery):
    """
    Обработчик кнопки удаления уведомления.
    """
    message = callback_query.message
    user_id = callback_query.from_user.id

    user_language = db.get_user_language(user_id)
    username_to_remove = callback_query.data.replace('remove_notification ', '')
    is_removed = db.remove_notification(user_id, username_to_remove)
    notifications_list = []
    active_notifications = db.user_have_active_notifications(user_id)
    if is_removed:
        notifications_list = db.get_user_notifications(user_id)
        await callback_query.message.edit_reply_markup(
            reply_markup=await keyboards.remove_notification(notifications_list, user_language))
        if not active_notifications:
            await callback_query.answer(f'{translate.remove_notification_success(user_language)}\n'
                                        f'{translate.no_notifications(user_language)}')
            await message.edit_text(translate.no_notifications(user_language))
            await message.answer(translate.default_message(user_language))
        else:
            await callback_query.answer(translate.remove_notification_success(user_language))
    else:
        await callback_query.answer(translate.remove_notification_fail(user_language))
    formatted_log.user_log(remove_notification, user_id=user_id, user_language=user_language,
                           is_removed=is_removed, notifications_list=notifications_list,
                           active_notifications=active_notifications)


async def set_last_message_date(user_id: int):
    """
    Устанавливает дату последнего сообщения пользователя.
    """
    last_message_date = formatted_time.get_time_now()
    db.set_last_message_date(user_id, last_message_date)
    formatted_log.user_log(set_last_message_date, user_id=user_id, last_message_date=last_message_date)


async def send_notification(user_id: int, text: str):
    """
    Отправляет уведомление пользователю.
    """
    user_language = db.get_user_language(user_id)
    kb = [
        [types.KeyboardButton(text=translate.notification_button(user_language))]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
    )
    await bot.send_message(user_id, text,
                           reply_markup=keyboard)
    formatted_log.user_log(send_notification, user_id=user_id, user_language=user_language, text=text)


# Обработчик админ пароля
@dp.message(F.text == admin_password)
async def make_admin(msg: types.Message):
    user_id = msg.from_user.id
    if db.user_exists(user_id):
        db.make_admin(user_id)
        await msg.answer('теперь админ')
    else:
        await msg.answer('сначала зарегайся')
    formatted_log.admin_log(make_admin, user_id=user_id)


# Обработчик для кнопки "Clear table"
@dp.callback_query(lambda c: c.data == 'clear_table')
async def clear_table(cq: types.CallbackQuery):
    user_id = cq.from_user.id
    is_admin = await is_admin_pass(user_id)
    if is_admin:
        if db.clear_all_tables():
            await cq.answer('Готово, таблица удалена, автоинкременты почищены')
        else:
            await cq.answer('Ошибка при удалении таблицы')
    formatted_log.admin_log(clear_table, user_id=user_id)


# Обработчик для кнопки "Get users table"
@dp.callback_query(lambda c: c.data == 'get_users_table')
async def get_users_table(cq: types.CallbackQuery):
    user_id = cq.from_user.id
    is_admin = await is_admin_pass(user_id)
    if is_admin:
        user_info = db.get_user_info()
        if user_info:
            await cq.answer('Готово')
            await cq.message.answer(f'User Info:\n{user_info}')
        else:
            await cq.message.answer('Ошибка при получении информации о пользователях')
    formatted_log.admin_log(get_users_table, user_id=user_id)


# Обработчик для кнопки "Get notifications table"
@dp.callback_query(lambda c: c.data == 'get_notifications_table')
async def get_notifications_table(cq: types.CallbackQuery):
    user_id = cq.from_user.id
    is_admin = await is_admin_pass(user_id)
    if is_admin:
        notifications_info = db.get_notifications_info()
        if notifications_info:
            await cq.answer('Готово')
            await cq.message.answer(f'Notifications Info:\n{notifications_info}')
        else:
            await cq.message.answer('Ошибка при получении информации о уведомлениях')
    formatted_log.admin_log(get_notifications_table, user_id=user_id)


# Обработчик для кнопки "Get history table"
@dp.callback_query(lambda c: c.data == 'get_history_table')
async def get_history_table(cq: types.CallbackQuery):
    user_id = cq.from_user.id
    is_admin = await is_admin_pass(user_id)
    if is_admin:
        history_info = db.get_history_info()
        if history_info:
            await cq.answer('Готово')
            await cq.message.answer(f'History Info:\n{history_info}')
        else:
            await cq.message.answer('Ошибка при получении информации о истории')
    formatted_log.admin_log(get_history_table, user_id=user_id)


# Обработчик для кнопки "Get user count"
@dp.callback_query(lambda c: c.data == 'get_user_count')
async def get_user_count(cq: types.CallbackQuery):
    user_id = cq.from_user.id
    is_admin = await is_admin_pass(user_id)
    if is_admin:
        user_count = db.user_count()
        if user_count is not None:
            await cq.answer('Готово')
            await cq.message.answer(f'Total users: {user_count}')
        else:
            await cq.message.answer('Ошибка при получении количества пользователей')
    formatted_log.admin_log(get_user_count, user_id=user_id)


# Обработчик для кнопки "Get active notifications count"
@dp.callback_query(lambda c: c.data == 'get_active_notifications_count')
async def get_active_notifications_count(cq: types.CallbackQuery):
    user_id = cq.from_user.id
    is_admin = await is_admin_pass(user_id)
    if is_admin:
        active_notifications_count = db.active_notifications_count()
        if active_notifications_count is not None:
            await cq.answer('Готово')
            await cq.message.answer(f'Total active notifications: {active_notifications_count}')
        else:
            await cq.message.answer('Ошибка при получении количества активных уведомлений')
    formatted_log.admin_log(get_active_notifications_count, user_id=user_id)


# Обработки отправки лога
@dp.callback_query(lambda c: c.data == 'get_log')
async def get_log(cq: types.CallbackQuery):
    user_id = cq.from_user.id
    is_admin = await is_admin_pass(user_id)
    if is_admin:
        try:
            log_file = FSInputFile(log_file_path)
            if log_file:
                await bot.send_document(user_id, document=log_file)
                await cq.message.answer('Готово')
        except Exception as e:
            logging.error(f'Ошибка при отправке лога:  {e}')
            await cq.message.answer('Ошибка при отправке лога')


@dp.callback_query(lambda c: c.data == 'get_db')
async def get_db(cq: types.CallbackQuery):
    user_id = cq.from_user.id
    is_admin = await is_admin_pass(user_id)
    if is_admin:
        try:
            db_file = FSInputFile(database_file_path)
            if db_file:
                await bot.send_document(user_id, document=db_file)
                await cq.message.answer('Готово')
        except Exception as e:
            logging.error(f'Ошибка при отправке базы данных:  {e}')
            await cq.message.answer('Ошибка при отправке базы данных')


@dp.callback_query(lambda c: c.data == 'clear_log')
async def clear_log(cq: types.CallbackQuery):
    user_id = cq.from_user.id
    is_admin = await is_admin_pass(user_id)
    if is_admin:
        try:
            file = open(log_file_path, 'w')
            file.write('')
            await cq.answer('Готово, лог очищен')
        except Exception as e:
            await cq.answer('Ошибка при очистка лога')
            logging.error(f'Ошибка при очистке лога: {e}')
    formatted_log.admin_log(clear_table, user_id=user_id)


@dp.message(Command('admin'))
async def admin_panel(msg: types.Message):
    user_id = msg.from_user.id
    is_admin = await is_admin_pass(user_id)
    if is_admin:
        await msg.answer('Админ-панель',
                         reply_markup=await keyboards.admin_panel())
    formatted_log.admin_log(admin_panel, user_id=user_id, is_admin=is_admin)


async def is_admin_pass(user_id: int):
    is_admin = db.is_admin(user_id)
    user_language = db.get_user_language(user_id)
    if is_admin:
        formatted_log.admin_log(is_admin_pass, user_id=user_id, is_admin=is_admin, user_language=user_language)
        return True
    else:
        await bot.send_message(user_id, translate.default_message(user_id))
        formatted_log.admin_log(is_admin_pass, user_id=user_id, is_admin=is_admin, user_language=user_language)
        return False


@dp.message()
async def not_handled(message: types.Message):
    user_id = message.from_user.id
    if db.user_exists(user_id):
        message_text = message.text
        await set_last_message_date(user_id)
        await username_check(message, message_text)
        formatted_log.admin_log(not_handled, user_id=user_id, message_text=message_text)
    else:
        await cmd_start(message)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("BOT STOPPED BY USER")
    except Exception as e:
        logging.error(f"BOT STOPPED BY ERROR: {e}")
