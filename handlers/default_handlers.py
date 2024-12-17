from aiogram.types import Message


async def echo_handler(message: Message) -> None:
    await message.reply('<i>Повідомлення не було розпізнане як команда, скористайтеся кнопками на панелі!</i>',
                        parse_mode='HTML')
