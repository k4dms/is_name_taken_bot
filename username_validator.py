import re

import translate


def is_name_valid(username, user_language):
    fl = username[0]
    ll = username[-1]
    regex = '^[a-zA-Z0-9_]+$'
    symbols = '0123456789_'
    pattern = re.compile(regex)

    if len(username) < 5 or len(username) > 32:
        return False, translate.username_validator(user_language, username, 1, fl)
    if fl in symbols:
        return False, translate.username_validator(user_language, username, 2, fl)
    if not pattern.search(username):
        return False, translate.username_validator(user_language, username, 3, fl)
    if ll == "_":
        return False, translate.username_validator(user_language, username, 4, fl)
    if "__" in username:
        return False, translate.username_validator(user_language, username, 5, fl)
    return True, False
