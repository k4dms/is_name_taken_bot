from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
import translate


async def language():
    buttons = [
        [types.KeyboardButton(text='English')],
        [types.KeyboardButton(text='Русский')]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
    )
    return keyboard


async def manage_notifications(user_language):
    buttons = [
        [types.KeyboardButton(text=translate.notification_button(user_language))]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
    )
    return keyboard


async def set_notification_fail(user_language):
    buttons = [
        [types.KeyboardButton(text=translate.notification_button(user_language))]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
    )
    return keyboard


async def set_notification_offer(user_language):
    buttons = [
        [types.KeyboardButton(text=translate.button_set_notify(user_language))],
        [types.KeyboardButton(text=translate.button_close(user_language))]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
    )
    return keyboard


async def set_notification_not_valid_name(user_language):
    buttons = [
        [types.KeyboardButton(text=translate.rules(user_language))]]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
    )
    return keyboard


async def remove_notification(notifications_list, user_language):
    builder = InlineKeyboardBuilder()
    # builder.button(text=translate.button_close(user_language), callback_data='close')
    for username in notifications_list:
        builder.button(text=f'{username}', callback_data=f'remove_notification {username}')
    builder.adjust(3)
    return builder.as_markup()


async def admin_panel():
    builder = InlineKeyboardBuilder()
    builder.button(text='X Clear table X', callback_data='clear_table')
    builder.button(text='X Clear log X', callback_data='clear_log')
    builder.button(text='Get users table', callback_data='get_users_table')
    builder.button(text='Get notify table', callback_data='get_notifications_table')
    builder.button(text='Get history table', callback_data='get_history_table')
    builder.button(text='Get user count', callback_data='get_user_count')
    builder.button(text='Get active notify count', callback_data='get_active_notifications_count')
    builder.button(text='Get log', callback_data='get_log')
    builder.button(text='Get db', callback_data='get_db')
    builder.adjust(2)
    return builder.as_markup()

