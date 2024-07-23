import formatted_time
from config import bot, admin_id


async def contact_admin(*args, **kwargs):
    """
    Отправляет сообщение администратору при возникновении ошибки.
    """
    time = formatted_time.get_time_now()
    text = f'Произошла необработанная ошибка. \nВремя ошибки: {time}\nАргументы:\n\n'
    for index, arg in enumerate(args):
        text += f'Arg {index}: {arg}\n'
    for key, value in kwargs.items():
        text += f'\n{key}:\n{value}\n'
    await bot.send_message(admin_id, text)
