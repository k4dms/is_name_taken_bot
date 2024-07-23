import sqlite3
import logging


class BotDB:
    def __init__(self, db_file: str):
        try:
            self.conn = sqlite3.connect(db_file)
            self.cursor = self.conn.cursor()
            self.create_tables()
        except sqlite3.Error as e:
            logging.error(f"Error connecting to database: {e}")
            raise

    def create_tables(self):
        try:
            sql_script = """
            BEGIN TRANSACTION;
            -- Table: history
            CREATE TABLE IF NOT EXISTS history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER REFERENCES users (user_id) ON DELETE CASCADE NOT NULL,
                        username TEXT NOT NULL,
                        status INTEGER,
                        time TEXT
                    );

            -- Table: notifications
            CREATE TABLE IF NOT EXISTS notifications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER REFERENCES users (user_id) ON DELETE CASCADE,
                        username TEXT,
                        active INTEGER DEFAULT (0),
                        status INTEGER,
                        last_checked TEXT
                    );

            -- Table: users
            CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER UNIQUE NOT NULL,
                        username TEXT,
                        user_first_name TEXT,
                        user_language TEXT DEFAULT 'EN',
                        join_date TEXT,
                        last_message_date TEXT,
                        username_checked TEXT,
                        state INTEGER DEFAULT (0),
                        admin INTEGER DEFAULT (0),
                        message_count INTEGER DEFAULT 0
                    );

            -- Trigger: increment_message_count_history
            CREATE TRIGGER IF NOT EXISTS increment_message_count_history
                    AFTER INSERT ON history
                    BEGIN
                        UPDATE users
                        SET message_count = message_count + 1
                        WHERE user_id = NEW.user_id;
                    END;

            COMMIT TRANSACTION;
            PRAGMA foreign_keys = on;
            """
            self.cursor.executescript(sql_script)
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error creating tables: {e}")
            self.conn.rollback()
            raise

    def user_exists(self, user_id: int) -> bool:
        try:
            result = self.cursor.execute("SELECT id FROM users WHERE user_id = ?",
                                         (user_id,))
            return bool(result.fetchone())
        except sqlite3.Error as e:
            logging.error(f"Error checking if user exists: {e}")
            return False

    def username_exists_in_notifications(self, username: str) -> bool:
        try:
            result = self.cursor.execute("SELECT id FROM notifications WHERE username = ?",
                                         (username,))
            return bool(result.fetchone())
        except sqlite3.Error as e:
            logging.error(f"Error checking if username exists in notifications: {e}")
            return False

    def user_have_active_notifications(self, user_id: int) -> bool:
        try:
            result = self.cursor.execute("SELECT id FROM notifications WHERE user_id = ? AND active = ?",
                                         (user_id, 1))
            return bool(result.fetchone())
        except sqlite3.Error as e:
            logging.error(f"Error checking if user have notifications: {e}")
            return False

    def add_user(self, user_id: int, username: str, user_first_name: str, user_language: str, join_date: str) -> None:
        try:
            self.cursor.execute(
                """INSERT OR IGNORE INTO users (user_id, username, user_first_name, user_language, join_date)
                VALUES (?, ?, ?, ?, ?)""",
                (user_id, username, user_first_name, user_language, join_date)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error adding user: {e}")

    def add_history(self, user_id: int, username: str, status: int, time: str) -> None:
        try:
            self.cursor.execute(
                """INSERT OR IGNORE INTO history (user_id, username, status, time)
                VALUES (?, ?, ?, ?)""",
                (user_id, username, status, time)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error adding history: {e}")

    def add_notify(self, user_id: int, username: str, active: int, status: int, time: str) -> None:
        try:
            self.cursor.execute(
                """INSERT OR IGNORE INTO notifications (user_id, username, active, status, last_checked)
                VALUES (?, ?, ?, ?, ?)""",
                (user_id, username, active, status, time)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error adding notification: {e}")

    def set_username_checked(self, user_id: int, username: str) -> None:
        try:
            self.cursor.execute("UPDATE users SET username_checked = ? WHERE user_id = ?",
                                (username, user_id))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error setting username checked: {e}")

    def set_user_language(self, user_id: int, user_language: str) -> None:
        try:
            self.cursor.execute("UPDATE users SET user_language = ? WHERE user_id = ?",
                                (user_language, user_id))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error setting user language: {e}")

    def set_last_message_date(self, user_id: int, last_message_date: str) -> None:
        try:
            self.cursor.execute("UPDATE users SET last_message_date = ? WHERE user_id = ?",
                                (last_message_date, user_id))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error setting last message date: {e}")

    def get_username_checked(self, user_id: int) -> str:
        try:
            result = self.cursor.execute("SELECT username_checked FROM users WHERE user_id = ?",
                                         (user_id,))
            return result.fetchone()[0]
        except sqlite3.Error as e:
            logging.error(f"Error getting username checked: {e}")
            return ""

    def get_username_status_from_history(self, username: str, user_id: int) -> int:
        try:
            result = self.cursor.execute("SELECT status FROM history WHERE username = ? AND user_id = ?",
                                         (username, user_id))
            return result.fetchone()[0]
        except sqlite3.Error as e:
            logging.error(f"Error getting username status from history: {e}")
            return -1

    def get_username_status_from_notifications(self, username: str) -> int:
        try:
            result = self.cursor.execute("SELECT status FROM notifications WHERE username = ?",
                                         (username,))
            return result.fetchone()[0]
        except sqlite3.Error as e:
            logging.error(f"Error getting notify username status: {e}")
            return -1

    def get_notify_match_status(self, user_id: int, username: str) -> bool:
        try:
            result = self.cursor.execute("SELECT status FROM notifications WHERE user_id = ? AND username = ?",
                                         (user_id, username))
            return bool(result.fetchone())
        except sqlite3.Error as e:
            logging.error(f"Error getting notify match status: {e}")
            return False

    def get_active_notifies(self) -> list:
        try:
            result = self.cursor.execute("SELECT username FROM notifications WHERE active = ?",
                                         (1,))
            return result.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error getting active notifies: {e}")
            return []

    def get_user_list(self, username: str) -> list:
        try:
            result = self.cursor.execute("SELECT user_id FROM notifications WHERE username = ?",
                                         (username,))
            return result.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error getting user list: {e}")
            return []

    def get_user_id_notify(self, username: str) -> int:
        try:
            result = self.cursor.execute("SELECT user_id FROM notifications WHERE username = ?",
                                         (username,))
            return result.fetchone()[0]
        except sqlite3.Error as e:
            logging.error(f"Error getting user ID from notify: {e}")
            return -1

    def get_username_data(self, username: str) -> tuple:
        try:
            result = self.cursor.execute("SELECT status, time FROM history WHERE username = ?",
                                         (username,))
            return result.fetchone(), result.fetchone()
        except sqlite3.Error as e:
            logging.error(f"Error getting username data: {e}")
            return (), ()

    def get_user_id(self, user_id: int) -> int:
        try:
            result = self.cursor.execute("SELECT id FROM users WHERE user_id = ?",
                                         (user_id,))
            return result.fetchone()[0]
        except sqlite3.Error as e:
            logging.error(f"Error getting user ID: {e}")
            return -1

    def get_user_language(self, user_id: int) -> str:
        try:
            result = self.cursor.execute("SELECT user_language FROM users WHERE user_id = ?",
                                         (user_id,))
            return result.fetchone()[0]
        except sqlite3.Error as e:
            logging.error(f"Error getting user language: {e}")
            return ""

    def get_user_state(self, user_id: int) -> str:
        try:
            result = self.cursor.execute("SELECT state FROM users WHERE user_id = ?",
                                         (user_id,))
            return result.fetchone()[0]
        except sqlite3.Error as e:
            logging.error(f"Error getting user state: {e}")
            return ""

    def get_last_check_time(self, username: str) -> str:
        try:
            result = self.cursor.execute("SELECT last_checked FROM notifications WHERE username = ?",
                                         (username,))
            return result.fetchone()[0]
        except sqlite3.Error as e:
            logging.error(f"Error getting last check time: {e}")
            return ""

    def get_user_notifications(self, user_id: int) -> list:
        try:
            result = self.cursor.execute("SELECT username FROM notifications WHERE user_id = ? AND active = ?",
                                         (user_id, 1))
            results = result.fetchall()
            if results:
                return [res[0] for res in results]
            else:
                return []
        except sqlite3.Error as e:
            logging.error(f"Error getting user notifications: {e}")
            return []

    def update_username(self, username: str, status: int, time: str) -> None:
        try:
            self.cursor.execute("UPDATE notifications SET status = ?, last_checked = ? WHERE username = ?",
                                (status, time, username))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error updating username: {e}")

    def remove_notification(self, user_id: int, username: str) -> bool:
        try:
            self.cursor.execute("DELETE FROM notifications WHERE user_id = ? AND username = ?",
                                (user_id, username))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error removing notification: {e}")
            return False

    def make_admin(self, user_id: int):
        try:
            self.cursor.execute('UPDATE users SET admin = 1 WHERE user_id = ?', (user_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Make admin error: {e}")
            return None

    def is_admin(self, user_id: int):
        try:
            self.cursor.execute('SELECT admin FROM users WHERE user_id = ?', (user_id,))
            result = self.cursor.fetchone()
            if result and result[0] == 1:
                return True
            else:
                return False
        except sqlite3.Error as e:
            logging.error(f"Is admin error: {e}")
            return None

    def user_count(self):
        try:
            result = self.cursor.execute("SELECT COUNT(*) FROM users")
            count = result.fetchone()[0]
            return count
        except sqlite3.Error as e:
            logging.error(f"Error counting users: {e}")
            return None

    def active_notifications_count(self):
        try:
            result = self.cursor.execute("SELECT COUNT(*) FROM notifications WHERE active = 1")
            count = result.fetchone()[0]
            return count
        except sqlite3.Error as e:
            logging.error(f"Error counting active notifications: {e}")
            return None

    def clear_all_tables(self):
        try:
            self.cursor.execute("DELETE FROM users")
            self.cursor.execute(f'DELETE FROM sqlite_sequence WHERE name="users";')
            self.cursor.execute("DELETE FROM history")
            self.cursor.execute(f'DELETE FROM sqlite_sequence WHERE name="history";')
            self.cursor.execute("DELETE FROM notifications")
            self.cursor.execute(f'DELETE FROM sqlite_sequence WHERE name="notifications";')
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error clearing tables: {e}")
            return False

    def get_user_info(self):
        try:
            result = self.cursor.execute("SELECT * FROM users")
            users = result.fetchall()
            return "\n".join([str(user) for user in users])
        except sqlite3.Error as e:
            logging.error(f"Error getting user info: {e}")
            return None

    def get_notifications_info(self):
        try:
            result = self.cursor.execute("SELECT * FROM notifications")
            notifications = result.fetchall()
            return "\n".join([str(notification) for notification in notifications])
        except sqlite3.Error as e:
            logging.error(f"Error getting notifications info: {e}")
            return None

    def get_history_info(self):
        try:
            result = self.cursor.execute("SELECT * FROM history")
            history = result.fetchall()
            return "\n".join([str(hist) for hist in history])
        except sqlite3.Error as e:
            logging.error(f"Error getting history info: {e}")
            return None

    def close(self) -> None:
        try:
            self.conn.close()
        except sqlite3.Error as e:
            logging.error(f"Error closing database connection: {e}")
