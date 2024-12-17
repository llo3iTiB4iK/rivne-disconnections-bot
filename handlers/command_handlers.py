from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, LinkPreviewOptions
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from functions.database_manager import db
from functions.schedule import schedule
from forms.bot_state import BotState


async def start(message: Message):
    kb_buttons = [[InlineKeyboardButton(text=str(turn/10), callback_data=str(turn))] for turn in schedule.turns_list]
    kb_buttons = [kb_buttons[i] + kb_buttons[i+1] for i in range(0, len(kb_buttons), 2)]

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_buttons)
    await message.answer(f"Оберіть свою чергу відключень нижче!\n Ви можете дізнатись свою чергу відключень за "
                         f"посиланнями: 📍Місто Рівне: https://shorturl.at/oMXLU\n📍Рівненська область: "
                         f"https://shorturl.at/zVUTT", link_preview_options=LinkPreviewOptions(is_disabled=True),
                         reply_markup=keyboard, parse_mode='HTML')


async def show_disconnections(message: Message, state: FSMContext):
    await state.set_state(BotState.location_added)
    user_locations = await db.get_user_locations(message.chat.id)
    if len(user_locations):
        kb_buttons = []
        for location in user_locations:
            kb_buttons.append([InlineKeyboardButton(text=location["location"] if location["location"] else
                                                    "Локація без назви", callback_data=f"turn {location['turn']}")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb_buttons)
        await message.answer("<i>Оберіть одну з Ваших локацій, де Ви хочете переглянути графіки відключень</i>",
                             reply_markup=keyboard, parse_mode='HTML')
    else:
        await message.answer('<b>Схоже, що Ви ще не додали жодної локації, Ви можете зробити це у "Моїх локаціях" '
                             'у меню!</b>', parse_mode='HTML')


async def show_locations(message: Message, state: FSMContext):
    await state.set_state(BotState.location_added)
    user_locations = await db.get_user_locations(message.chat.id)
    kb_buttons = []
    if len(user_locations):
        for location in user_locations:
            kb_buttons.append([InlineKeyboardButton(text=location["location"] if location["location"] else
                                                    "Локація без назви", callback_data=f"delete_location {location['id']}")])
        msg_text = "<i>Натисніть на одну з Ваших локацій, щоб видалити її або оберіть <u>'Додати локацію'</u> для " \
                   "додавання нової!</i>"
    else:
        msg_text = '<b>Схоже, що Ви ще не додали жодної локації!</b>'
    kb_buttons.append([InlineKeyboardButton(text="➕ Додати локацію ➕", callback_data="add_location")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_buttons)
    try:
        await message.answer(msg_text, reply_markup=keyboard, parse_mode='HTML')
    except TelegramBadRequest:
        pass


async def notifications(message: Message, state: FSMContext):
    await state.set_state(BotState.location_added)
    button1 = InlineKeyboardButton(text='15 хв', callback_data='15 хв')
    button2 = InlineKeyboardButton(text='30 хв', callback_data='30 хв')
    button3 = InlineKeyboardButton(text='60 хв', callback_data='60 хв')
    notify_by = await db.get_user_notification_time(message.chat.id)
    if notify_by is None:
        msg_text = "Оберіть, за скільки часу Ви хотіли би отримувати сповіщення про відключення:"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[button1, button2, button3]])
    elif not notify_by:
        await message.answer('<b>Схоже, що Ви ще не додали жодної локації!</b>', parse_mode='HTML')
        return
    else:
        msg_text = f"Наразі Ви отримуєте сповіщення за {notify_by} хв до відключень\nВикористайте кнопки нижче, щоб " \
                   f"змінити час до відключення, за який Ви будете отримувати сповіщення або вимкнути їх"
        cancel_button = InlineKeyboardButton(text='Відписатись від сповіщень', callback_data='turn_off_notifications')
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[button1, button2, button3], [cancel_button]])
    await message.answer(msg_text, reply_markup=keyboard)


async def support(message: Message, state: FSMContext):
    await message.answer("<i>Напишіть повідомлення з Вашими скаргами або пропозиціями, в якому детально опишіть Вашу "
                         "проблему або ідею!</i>", parse_mode='HTML')
    await state.set_state(BotState.waiting_for_support_message)


async def donate(message: Message, state: FSMContext):
    await state.set_state(BotState.location_added)
    await message.answer("__Ви можете підтримати розробника \(@i\_v\_a\_n\_0\) за реквізитами:__\n\n"
                         "⚫Монобанк⚫: `4441 1110 4500 5703`\n\n🟢Приватбанк🟢: `4149 4390 2671 1949`",
                         parse_mode='MarkdownV2')
