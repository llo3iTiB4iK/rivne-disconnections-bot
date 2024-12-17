import asyncio
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

from functions.schedule import schedule
from functions.database_manager import db
from config import DISCONNECTIONS_URL


class Disconnections:

    def __init__(self):
        self.bot = None
        self.schedule = schedule

    async def update_loop(self, interval):
        while True:
            turns_changed = None
            if self.schedule.need_updates():
                self.schedule.update()
                turns_changed = self.schedule.get_changed_turns()
            if turns_changed:
                await self.notify_schedule_change(turns_changed)
            await asyncio.sleep(60 * interval)

    async def show_times(self, user_id, turn):
        msg_text = ""
        try:
            schedule_by_turn = self.schedule.get_schedule_by_turn(turn)
        except KeyError:
            return
        for date, hours in schedule_by_turn.items():
            if hours:
                msg_text += f"<u>{date}</u> очікуються відключення електропостачання ☠:\n<b>{',/t'.join(hours)}</b>\n\n"
            else:
                msg_text += f"<u>{date}</u> не планується відключень електропостачання 🥰\n\n"
        msg_text += f"<i>{self.schedule.last_updated} (з офіційного сайту Рівнеобленерго)</i>"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Рівнеобленерго",
                                                                               url=DISCONNECTIONS_URL)]])
        try:
            await self.bot.send_message(user_id, msg_text, reply_markup=keyboard, parse_mode='HTML')
        except TelegramForbiddenError:
            pass

    async def notify_schedule_change(self, turns_changed_list):
        semaphore = asyncio.Semaphore(30)

        async def send_message_with_limit(user_id, msg_text, keyboard):
            async with semaphore:
                try:
                    await self.bot.send_message(user_id, msg_text, reply_markup=keyboard, parse_mode='HTML')
                except (TelegramForbiddenError, TelegramBadRequest):
                    pass
                await asyncio.sleep(1)

        async def check_user_schedule_changes(user_id):
            for user_location in await db.get_user_locations(user_id):
                location_turn = user_location["turn"]
                if location_turn in turns_changed_list:
                    msg_text = f"З'явився або змінився графік за вашою локацією \"<b>{user_location['location']}</b>\""
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                        InlineKeyboardButton(text="Переглянути", callback_data=f"turn {location_turn}")
                    ]])
                    await send_message_with_limit(user_id, msg_text, keyboard)

        start_time = datetime.now()
        await asyncio.gather(*(check_user_schedule_changes(user_id) for user_id, _ in await db.get_users()))
        print((datetime.now() - start_time).total_seconds(), 'секунд - Надсилання сповіщень про зміну графіків')


disconnections = Disconnections()
