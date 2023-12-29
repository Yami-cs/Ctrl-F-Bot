import asyncio
from tkinter import TRUE
from aiogram import types
from config import bot_token
from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import get_user_by_tg_id, insert_user, add_text, delete_text, update_priority, update_text, get_text
from aiogram.dispatcher.filters import Text

bot = Bot(token=bot_token)

storage = MemoryStorage()

dp = Dispatcher(bot, storage=storage)

menu = types.ReplyKeyboardMarkup(resize_keyboard=True)\
    .add(types.KeyboardButton("Добавить слово"))\
    .add(types.KeyboardButton("Удалить слово"))\
    .add(types.KeyboardButton("Список слов"))

@dp.message_handler(commands=["start"])
async def gde_mama(message: types.Message):
    tg_id = message.from_user.id
    if get_user_by_tg_id(tg_id) is None:
        insert_user(tg_id)
    await message.answer("Вот твоя клавиатура, а теперь иди нахуй отсюда!", reply_markup=menu)

class UserAdd(StatesGroup):
    text = State()
    priority = State()


@dp.message_handler(Text("Добавить слово"))
async def add(message: types.Message):
    await message.answer("Введите ключевое слово, по которому будут определяться важные сообщения.", reply_markup=types.ReplyKeyboardRemove())
    await UserAdd.text.set()

@dp.message_handler(state=UserAdd.text)
async def answer(message: types.Message, state: FSMContext):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)\
        .add(types.KeyboardButton("Да"))\
        .add(types.KeyboardButton("Нет"))
    await state.update_data(text = message.text)
    await message.answer("Введите имеет ли этот текст приоритет:", reply_markup=kb)
    await UserAdd.next();


@dp.message_handler(state=UserAdd.priority)
async def sho(message: types.Message, state: FSMContext):
    tg_id = message.from_user.id
    if message.text == "Да":
        await state.update_data(priority = 1)
    else:
        await state.update_data(priority = 0)
    data = await state.get_data()
    update_text(tg_id, data["text"], data["priority"])
    await state.finish()
    await message.answer("Слово добавлено.", reply_markup=menu);


class UserDelete(StatesGroup):
    text = State()

@dp.message_handler(Text("Удалить слово"))
async def delete(message: types.Message):
    user_text = get_text(message.from_user.id);
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for elem in user_text:
        kb.add(types.KeyboardButton(elem["text"]))
    await message.answer("Введите слово или номер слова, которое нужно удалить.", reply_markup=kb)
    await UserDelete.text.set()

@dp.message_handler(state=UserDelete.text)
async def answer(message: types.Message, state: FSMContext):
    delete_text(message.from_user.id, message.text)
    await state.finish()
    await message.answer("Слово удалено.", reply_markup=menu);


@dp.message_handler(Text("Список слов"))
async def user_word(message: types.Message):
    chat_id = message.from_user.id
    text = []
    user_text = get_text(chat_id)
    for elem in user_text:
        if elem["priority"]:
            text.append(f'{elem["text"]}: С приоритетом')
        else:
            text.append(f'{elem["text"]}: Без приоритета')
        
    await message.answer("Ваши слова:\n" +"\n".join(text, ), reply_markup=menu)


async def start_bot():
    print("Bot started")
    try:
        await dp.start_polling()

    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.close()


if __name__ == "__main__":
    asyncio.run(start_bot())
