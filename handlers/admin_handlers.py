import asyncio
from aiogram.types import Message
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from datetime import datetime

from functions.database_manager import db


async def reply_to_support_request(message: Message):
    forwarded_message = message.reply_to_message
    user_id = await db.get_user_id_by_support_request_message(forwarded_message.message_id)
    if user_id:
        await message.send_copy(user_id)
        await message.answer('Відповідь була успішно надіслана користувачеві!')


async def notify_all_users(message: Message):
    msg_text = message.text[5:]
    is_silent = msg_text.startswith('/quiet')
    if is_silent:
        msg_text = msg_text[7:]
    user_data = await db.get_users()
    bot = message.bot
    semaphore = asyncio.Semaphore(30)

    async def send_to_user(user_id):
        async with semaphore:
            try:
                await bot.send_message(chat_id=user_id, text=msg_text, disable_notification=is_silent)
            except (TelegramForbiddenError, TelegramBadRequest):
                pass
            await asyncio.sleep(0.5)

    start_time = datetime.now()
    await asyncio.gather(*(send_to_user(user[0]) for user in user_data))
    print((datetime.now() - start_time).total_seconds(), 'секунд - Розсилка повідомлень для УСІХ')
