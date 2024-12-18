import asyncio
from datetime import datetime, timedelta
from aiogram.exceptions import TelegramForbiddenError

from functions.schedule import schedule
from functions.database_manager import db
from config import TIMEZONE


class Notifications:

    def __init__(self):
        self.timezone = TIMEZONE
        self.bot = None
        self.schedule = schedule

    async def update_loop(self, interval):
        while True:
            users = [user for user in await db.get_users() if user[1]]
            locations = await db.get_user_locations()
            disconnection_starts_by_turn = self.schedule.get_disconnections_start_times()
            now = datetime.now(self.timezone)
            semaphore = asyncio.Semaphore(30)

            async def check_user_notifications(user_id, minutes):
                for user_location in [loc for loc in locations if loc['user_id'] == user_id]:
                    try:
                        turn_disconnections = disconnection_starts_by_turn[user_location["turn"]]
                    except KeyError:
                        continue
                    for i, disconnection_start in enumerate(turn_disconnections):
                        notify_at = disconnection_start - timedelta(minutes=minutes)
                        if now <= self.timezone.localize(notify_at) < (now + timedelta(minutes=interval)):
                            async with semaphore:
                                await self.send_notification(minutes, user_id, user_location['location'])
                                await asyncio.sleep(0.5)
            start_time = datetime.now()
            await asyncio.gather(*(check_user_notifications(user_id, minutes) for user_id, minutes in users))
            print((datetime.now()-start_time).total_seconds(), 'секунд - Надсилання сповіщень про наближення відключення')
            await asyncio.sleep(60 * interval)

    async def send_notification(self, by_minutes, user_id, location_name):
        try:
            disconnection_notification = f"⚠ <b>Приблизно за {by_minutes} хвилин планується відключення " \
                                         f"електропостачання - <u>" \
                                         f"{location_name if location_name else 'Локація без назви'}</u></b> ⚠"
            await self.bot.send_message(user_id, disconnection_notification, parse_mode='HTML')
        except TelegramForbiddenError:
            pass


notifications = Notifications()
