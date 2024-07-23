def language_default_text():
    return ('Hi, choose a language that is convenient for you to work with me!\n\n'
            'Привет, выбери язык, на котором тебе удобно работать со мной!')


def username_check_error_occurred(language, error):
    return exit_func(
        f'An error has occurred.\n{error}\nPlease check the rules: /rules',
        f'Произошла ошибка.\n{error}\nПожалуйста, посмотрите: /rules',
        language
    )


def button_set_notify(language):
    return exit_func('Set notify', 'Установить уведомление', language)


def button_close(language):
    return exit_func('Close', 'Закрыть', language)


def username_check_offer(language, answer):
    return exit_func(
        f'{answer}\nDo you want to set notification when it becomes available?',
        f'{answer}\nВы хотите установить уведомление, когда это имя станет доступно?',
        language
    )


def notifications_manage(language):
    return exit_func(
        'To unsubscribe, click on the username below:',
        'Чтобы отписаться, нажмите на имя ниже:',
        language
    )


def cmd_rules(language):
    rules_en = (
        '1. The minimum length of the username must be 5 characters.\n\n'
        '2. The maximum length is 32 characters.\n\n'
        '3. The username can contain letters (a-Z), numbers (0-9), and underscores.\n\n'
        '4. The first character of the username should be a letter.\n\n'
        '5. Two or more underscores cannot be used in a row.\n\n'
        '6. The username cannot end with an underscore.'
    )

    rules_ru = (
        '1. Минимальная длина имени 5 символов.\n\n'
        '2. Максимальная длина имени 32 символа.\n\n'
        '3. Имя должно состоять из английских букв (a-Z), цифр (0-9) и символа подчеркивания.\n\n'
        '4. Первая буква имени должна быть буквой.\n\n'
        '5. Два или более символа подчеркивания не могут идти подряд.\n\n'
        '6. Имя не может заканчиваться символом подчеркивания.'
    )

    return exit_func(rules_en, rules_ru, language)


def default_message(language):
    return exit_func(
        'I can check if a username is available.\nPlease provide the username in the format:\n@username or username',
        'Я могу проверить, доступно ли имя.\nНапиши имя в формате:\n@username или username',
        language
    )


def set_notify(language):
    return exit_func(
        'Notification is ON!\n\n/notify - manage',
        'Уведомление включено!\n\n/notify - изменить',
        language
    )


def manage_notifications(language):
    return exit_func(
        'Notifications manager',
        'Управление уведомлениями',
        language
    )


def set_notify_fail(language):
    return exit_func(
        'Notification is already ON!\n/notify - manage',
        'Уведомление УЖЕ включено!\n/notify - изменить',
        language
    )


def send_notification(language, username, status):
    status_text = status_switcher(language, status)
    return exit_func(
        f'ALERT! Username @{username} is {status_text}!',
        f'ВНИМАНИЕ! Имя @{username} теперь {status_text}!',
        language
    )


def rules(language):
    return exit_func('Rules', 'Правила', language)


def notification_button(language):
    return exit_func('Manage notifications', 'Управление уведомлениями', language)


def remove_notification_success(language):
    return exit_func('Notify removed', 'Уведомление удалено', language)


def remove_notification_fail(language):
    return exit_func('Error occured', 'Произошла ошибка', language)


def no_notifications(user_language):
    en = 'No active notifications!'
    ru = 'У вас нет активных уведомлений'
    return exit_func(en, ru, user_language)


def status_switcher(language, status):
    statuses_en = {
        1: 'available',
        2: 'taken',
        3: 'on auction',
        4: 'on sale',
        5: 'sold',
        6: 'error'
    }

    statuses_ru = {
        1: 'доступен',
        2: 'занят',
        3: 'на аукционе',
        4: 'на продаже',
        5: 'был продан ранее',
        6: 'ошибка'
    }

    return statuses_en.get(status, 'unknown status') if language == 'EN' else statuses_ru.get(status,
                                                                                              'неизвестный статус')


def username_validator(language, name, error, fl):
    errors_en = {
        1: f'Username length is incorrect: {len(name)}.\nIt should be between 5 and 32.',
        2: f'Username should starts with a letter, not the {fl}.',
        3: 'Username contains invalid characters.',
        4: 'Username cannot end with an underscore.',
        5: 'Username cannot contain two or more underscores in a row.'
    }

    errors_ru = {
        1: f'Некорректная длина имени: {len(name)}.\nДлина должна быть от 5 до 32 символов.',
        2: f'Имя должно начинаться с буквы, а не с {fl}.',
        3: 'Имя содержит недопустимые символы.',
        4: 'Имя не может заканчиваться символом подчеркивания.',
        5: 'В имени не может быть двух и более подчеркиваний подряд.'
    }

    return errors_en.get(error, 'unknown error') if language == 'EN' else errors_ru.get(error, 'неизвестная ошибка')


def statuses(language, name, auc_url, status):
    status_en = {
        1: f'Username @{name} is available.',
        2: f'Username @{name} is taken.',
        3: f'Username @{name} is currently bidding on an active auction:\n{auc_url}',
        4: f'Username @{name} is currently on sale:\n{auc_url}',
        5: f'Username @{name} has been sold before.\n{auc_url}',
        6: 'An unexpected error has occurred, and the administrator has been notified.\nContact the administrator: @k4dms'
    }

    status_ru = {
        1: f'Имя @{name} доступно.',
        2: f'Имя @{name} занято.',
        3: f'Имя @{name} сейчас находится на аукционе:\n{auc_url}',
        4: f'Имя @{name} сейчас находится в продаже:\n{auc_url}',
        5: f'Имя @{name} было продано ранее:\n{auc_url}',
        6: 'Произошла непредвиденная ошибка, администратор оповещён.\nСвязь с администратором: @k4dms'
    }

    return status_en.get(status, 'unknown status') if language == 'EN' else status_ru.get(status, 'неизвестный статус')


def exit_func(en, ru, language):
    return en if language == 'EN' else ru
