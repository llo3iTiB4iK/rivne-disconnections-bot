from aiogram.types import CallbackQuery, InaccessibleMessage
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from handlers.command_handlers import start
from functions.database_manager import db
from functions.disconnections import disconnections
from forms.bot_state import BotState


async def turn_to_add_chosen(call: CallbackQuery, state: FSMContext):
    await state.update_data(turn=int(call.data))
    try:
        await call.message.delete()
    except (TelegramBadRequest, AttributeError):
        if not isinstance(call.message, InaccessibleMessage):
            await call.message.answer("<b>Не натискайте, будь ласка, одну й ту ж кнопку декілька разів, це призводить "
                                      "до затримки обробки запитів інших користувачів</b>\n<u>Дайте назву для доданої "
                                      "Вами локації (наприклад 'Дім'):</u>", parse_mode='HTML')
        return
    await call.message.answer("<i>Дайте назву для доданої Вами локації (наприклад 'Дім'):</i>", parse_mode='HTML')
    await state.set_state(BotState.waiting_for_loc_tag_input)
    await call.answer()


async def turn_to_show_disconnections_chosen(call: CallbackQuery):
    _, turn, location_name = call.data.split("|")
    await disconnections.show_times(user_id=call.from_user.id, turn=int(turn), location_name=location_name)
    await call.answer()


async def add_location_button_pressed(call: CallbackQuery):
    try:
        await call.message.delete()
    except (TelegramBadRequest, AttributeError):
        pass
    else:
        await start(call.message)
    finally:
        await call.answer()


async def delete_location_button_pressed(call: CallbackQuery):
    location_id = int(call.data.split()[1])
    try:
        await call.message.delete()
    except (TelegramBadRequest, AttributeError):
        if not isinstance(call.message, InaccessibleMessage):
            await call.message.answer("<b>Не натискайте, будь ласка, одну й ту ж кнопку декілька разів, це призводить "
                                      "до затримки обробки запитів інших користувачів</b>\n<u>Вашу локацію було "
                                      "видалено!</u>", parse_mode='HTML')
    else:
        await db.delete_user_location(location_id)
        await call.message.answer(f'<i>Локацію було успішно видалено!</i>', parse_mode='HTML')
    finally:
        await call.answer()


async def button_in_notifications_menu_pressed(call: CallbackQuery):
    turn_off = (call.data == 'turn_off_notifications')
    try:
        await call.message.delete()
    except (TelegramBadRequest, AttributeError):
        if not isinstance(call.message, InaccessibleMessage):
            additional_txt = "<u>Сповіщення були вимкнені!</u>" if turn_off else \
                f"<u>Сповіщення за {call.data} були увімкнені!</u>"
            await call.message.answer("<b>Не натискайте, будь ласка, одну й ту ж кнопку декілька разів, це призводить "
                                      "до затримки обробки запитів інших користувачів</b>\n" + additional_txt,
                                      parse_mode='HTML')
    else:
        notify_by = None if turn_off else int(call.data.split()[0])
        await db.set_notification_time_for_user(user_id=call.message.chat.id, notify_by=notify_by)
        msg_text = '<i>Тепер для Вас не надходитимуть завчасні сповіщення про відключення!</i>' if turn_off \
            else f'<i>Тепер для Вас надходитимуть сповіщення за {call.data} до планового відключення</i>'

        await call.message.answer(msg_text, parse_mode='HTML')
    finally:
        await call.answer()
