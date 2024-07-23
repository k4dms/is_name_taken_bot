import formatted_time
import handlers
import translate
import username_status
from config import db, fragment_request_interval


async def get_users_list(username):
    users_list = db.get_user_list(username)
    return users_list[0]


async def check_status(username):
    old_status = db.get_username_status_from_notifications(username)
    new_status = await username_status.get_status(username)
    if not new_status == 6:
        time = formatted_time.get_time_now()
        db.update_username(username, new_status, time)
        if old_status != new_status:
            users_list = await get_users_list(username)
            for user_id in users_list:
                language = db.get_user_language(user_id)
                text = translate.send_notification(language, username, new_status)
                await handlers.send_notification(user_id, text)


async def find_outdated_checks(usernames):
    for username in usernames:
        last_checked = db.get_last_check_time(username)
        time_now = formatted_time.get_time_now()
        time_delta = formatted_time.get_time_delta_seconds(time_now, last_checked)
        if time_delta > fragment_request_interval:
            await check_status(username)


async def find_active_notifications():
    if len(db.get_active_notifies()) > 0:
        usernames_with_active_notification = set(db.get_active_notifies())
        if len(usernames_with_active_notification) > 0:
            for username in usernames_with_active_notification:
                await find_outdated_checks(username)


async def add_notify(user_id, username, active, status, time):
    db.add_notify(user_id, username, active, status, time)


async def is_notify_exists(user_id, username):
    if not db.get_notify_match_status(user_id, username):
        return False
    else:
        return True
