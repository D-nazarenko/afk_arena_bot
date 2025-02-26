import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart
import os

from keep_alive import keep_alive

keep_alive()

TOKEN = os.getenv("TOKEN")   
ADMIN_ID = 430105072   

bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# Обработчик команды /start
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет! Напиши мне вопрос, и админ получит его.")

# Обработчик входящих сообщений и медиа
@dp.message()
async def forward_to_admin(message: Message):
    if message.from_user.id == ADMIN_ID:
        if message.reply_to_message:
            user_id = None
            if message.reply_to_message.forward_from:
                user_id = message.reply_to_message.forward_from.id
            elif message.reply_to_message.text:
                parts = message.reply_to_message.text.split("ID: ")
                if len(parts) > 1:
                    user_id = int(parts[1].split("\n")[0])

            if user_id:
                try:
                    if message.text:
                        await bot.send_message(user_id, f"Ответ от админа: {message.text}")
                    elif message.photo:
                        await bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption or "Ответ от админа")
                    elif message.document:
                        await bot.send_document(user_id, message.document.file_id, caption=message.caption or "Ответ от админа")
                    elif message.video:
                        await bot.send_video(user_id, message.video.file_id, caption=message.caption or "Ответ от админа")
                    elif message.sticker:
                        await bot.send_sticker(user_id, message.sticker.file_id)
                    logging.info(f"Ответ отправлен пользователю {user_id}")
                except Exception as e:
                    await message.answer("Не удалось отправить сообщение. У пользователя скрытый профиль. Попросите его написать боту команду /start, чтобы разрешить сообщения от бота.")
                    await bot.send_message(user_id, "Админ ответил на ваш вопрос, но ваш профиль скрыт. Пожалуйста, отправьте боту команду /start, чтобы получать ответы.")
                    logging.error(f"Ошибка отправки сообщения пользователю {user_id}: {e}")
            else:
                await message.answer("Не удалось определить ID пользователя. Ответ невозможен.")
        else:
            await message.answer("Ответьте на сообщение пользователя, чтобы отправить ответ.")
    else:
        forwarded_message = await bot.forward_message(ADMIN_ID, message.from_user.id, message.message_id)
        await bot.send_message(ADMIN_ID, f"Вопрос от @{message.from_user.username} (ID: {message.from_user.id}):\n{message.text}")
        await forwarded_message.reply("Ответьте на это сообщение, чтобы отправить ответ пользователю.")
        await message.answer("Ваш вопрос отправлен админу. Ожидайте ответ.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
