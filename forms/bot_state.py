from aiogram.fsm.state import State, StatesGroup


class BotState(StatesGroup):
    waiting_for_loc_tag_input = State()
    location_added = State()
    waiting_for_support_message = State()
