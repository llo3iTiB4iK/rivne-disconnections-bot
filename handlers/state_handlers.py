from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from functions.database_manager import db
from functions.disconnections import disconnections
from forms.bot_state import BotState
from config import ADMIN_USER_ID


async def location_tag_entered(message: Message, state: FSMContext):
    data = await state.get_data()
    await db.add_user_location(user_id=message.chat.id, turn=data.get("turn"), location_tag=message.text)
    await db.add_user(message.chat.id)
    await message.answer(f"Локацію <b>'{message.text}'</b> було успішно додано!", parse_mode='HTML')
    await disconnections.show_times(message.chat.id, turn=data.get("turn"))
    await message.answer("<i>Надалі Ви можете використовувати команду з меню (зліва від поля введення повідомлення) для"
                         " відображення графіків відключень!</i>", parse_mode='HTML')
    await state.set_state(BotState.location_added)


async def support_request_entered(message: Message, state: FSMContext):
    forwarded_message = await message.forward(ADMIN_USER_ID)
    await db.add_support_request(user_id=message.chat.id, request_message_id=forwarded_message.message_id)
    await state.set_state(BotState.location_added)
    await message.reply("Ваше повідомлення надіслано. Дякуємо!")
