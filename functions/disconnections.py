import asyncio
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest, TelegramNetworkError
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
            try:
                turns_changed = None
                if self.schedule.need_updates():
                    self.schedule.update()
                    turns_changed = self.schedule.get_changed_turns()
                if turns_changed:
                    await self.notify_schedule_change(turns_changed)
            except Exception as e:
                print(f"Помилка під час оновлення розкладу: {e}")
            await asyncio.sleep(60 * interval)

    async def show_times(self, user_id, turn):
        msg_text = ""
        try:
            schedule_by_turn = self.schedule.get_schedule_by_turn(turn)
        except KeyError:
            return
        for date, hours in schedule_by_turn.items():
            if hours:
                msg_text += f"<u>{date}</u> очікуються відключення електропостачання ☠:\n<b>{',    '.join(hours)}</b>\n\n"
            else:
                msg_text += f"<u>{date}</u> не планується відключень електропостачання 🥰\n\n"
        if not schedule_by_turn:
            msg_text += "<b><u>Відсутні актуальні дані про планові відключення електроенергії</u></b>\n\n"
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
                except (TelegramForbiddenError, TelegramBadRequest, TelegramNetworkError):
                    pass
                await asyncio.sleep(0.5)

        async def check_location_schedule_changes(user_location):
            location_turn = user_location["turn"]
            if location_turn in turns_changed_list:
                msg_text = f"З'явився або змінився графік за вашою локацією \"<b>{user_location['location']}</b>\""
                keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="Переглянути", callback_data=f"turn {location_turn}")
                ]])
                await send_message_with_limit(user_location["user_id"], msg_text, keyboard)

        start_time = datetime.now()
        await asyncio.gather(*(check_location_schedule_changes(loc) for loc in await db.get_user_locations()))
        print((datetime.now() - start_time).total_seconds(), 'секунд - Надсилання сповіщень про зміну графіків')


disconnections = Disconnections()
