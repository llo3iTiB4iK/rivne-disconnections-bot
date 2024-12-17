# Lib imports
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
# Own modules imports
from handlers import admin_handlers as admin, callback_handlers as callback, default_handlers as default, \
    command_handlers as command, state_handlers as state
from functions.disconnections import disconnections
from functions.notifications import notifications
from functions.database_manager import db
from forms.bot_state import BotState
from config import BOT_TOKEN, ADMIN_USER_ID, DISCONNECTIONS_CHECK_INTERVAL, NOTIFICATION_CHECK_INTERVAL

# Initialize instances
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Register commands handlers
dp.message.register(command.start, CommandStart())
dp.message.register(command.show_disconnections, Command("show_disconnections"))
dp.message.register(command.show_locations, Command("show_locations"))
dp.message.register(command.notifications, Command("notifications"))
dp.message.register(command.support, Command("support"))
dp.message.register(command.donate, Command("donate"))

# Register states handlers
dp.message.register(state.location_tag_entered, BotState.waiting_for_loc_tag_input)
dp.message.register(state.support_request_entered, BotState.waiting_for_support_message)

# Register callback handlers
dp.callback_query.register(callback.turn_to_add_chosen, lambda call: call.data.isnumeric())
dp.callback_query.register(callback.turn_to_show_disconnections_chosen, lambda call: call.data.startswith("turn "))
dp.callback_query.register(callback.add_location_button_pressed, lambda call: call.data == 'add_location')
dp.callback_query.register(callback.delete_location_button_pressed,
                           lambda call: call.data.startswith('delete_location'))
dp.callback_query.register(callback.button_in_notifications_menu_pressed,
                           lambda call: call.data.endswith('хв') or call.data == 'turn_off_notifications')

# Register admin chat handlers
dp.message.register(admin.reply_to_support_request,
                    lambda message: str(message.chat.id) == ADMIN_USER_ID and message.reply_to_message)
dp.message.register(admin.notify_all_users,
                    lambda message: str(message.chat.id) == ADMIN_USER_ID and '/all' in message.text)

# Register default handler
dp.message.register(default.echo_handler)


# Launching asynchronous tasks
async def main():
    asyncio.create_task(db.initialize())
    disconnections.bot = bot
    asyncio.create_task(disconnections.update_loop(DISCONNECTIONS_CHECK_INTERVAL))
    notifications.bot = bot
    asyncio.create_task(notifications.update_loop(NOTIFICATION_CHECK_INTERVAL))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
