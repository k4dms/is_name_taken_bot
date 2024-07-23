import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import handlers
import notifications
import logging
from config import db_request_interval


def set_scheduled_jobs(scheduler, *args, **kwargs):
    """
    Устанавливает запланированные задачи для планировщика.

    :param scheduler: Экземпляр AsyncIOScheduler
    """
    scheduler.add_job(notifications.find_active_notifications, 'interval', seconds=db_request_interval)


async def main():
    """
    Основная асинхронная функция, которая настраивает планировщик и запускает основной обработчик.
    """
    # Создаем и запускаем планировщик
    scheduler = AsyncIOScheduler()
    set_scheduled_jobs(scheduler)
    scheduler.start()

    try:
        await handlers.main()
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
    finally:
        # Корректное завершение работы планировщика
        scheduler.shutdown(wait=False)


if __name__ == '__main__':
    try:
        logging.info("STARTING")
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("STOPPING")
    except Exception as e:
        logging.error(f"STARTING ERROR: {e}")
