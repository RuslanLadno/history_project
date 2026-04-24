import asyncio
import os
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command


TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ====== СОСТОЯНИЕ ======
LOCK_MINUTES = 1
locks = {}  # chat_id -> время разблокировки


# ====== КЛАВИАТУРА ======
def get_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔎 Подсказка 1 - 2 вопрос", callback_data="hint1")],
            [InlineKeyboardButton(text="💡 Подсказка 2 - 3 вопрос", callback_data="hint2")],
            [InlineKeyboardButton(text="🔐 Подсказка 3 - 4 вопрос", callback_data="hint3")]
        ]
    )


# ====== /start ======
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Выберите подсказку 👇", reply_markup=get_keyboard())


# ====== ОБРАБОТКА ======
@dp.callback_query(F.data.startswith("hint"))
async def send_hint(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    now = datetime.now()

    # Проверка блокировки
    if chat_id in locks:
        if now < locks[chat_id]:
            remaining = int((locks[chat_id] - now).total_seconds())
            await callback.answer(
                f"⏳ Подсказки будут доступны через {remaining} сек",
                show_alert=True
            )
            return
        else:
            del locks[chat_id]

    # Подсказки
    hints = {
        "hint1": "🔎 Чтобы посчитать молярную массу, вспомните, что карбонат кальция состоит из трех элементов: кальция, углерода и кислорода. Найдите атомные массы каждого элемента в таблице Менделеева.",
        "hint2": "💡 Это слово связано с формой, в которой мы принимаем лекарства. Оно начинается с буквы <т> и заканчивается на <ка>.",
        "hint3": "🔐 Молекулярная масса углеводорода — это сумма масс всех его атомов. Не забудьте учесть количество атомов каждого элемента."
    }

    await callback.message.answer(hints[callback.data])
    await callback.answer("Подсказка получена!")

    # Ставим блокировку
    locks[chat_id] = now + timedelta(minutes=LOCK_MINUTES)

    # Авто-уведомление о разблокировке
    asyncio.create_task(unlock(chat_id))


# ====== РАЗБЛОКИРОВКА ======
async def unlock(chat_id):
    await asyncio.sleep(LOCK_MINUTES * 60)

    if chat_id in locks:
        del locks[chat_id]

    await bot.send_message(
        chat_id,
        "⏳ Подсказки снова доступны!",
        reply_markup=get_keyboard()
    )


# ====== ЗАПУСК ======
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())