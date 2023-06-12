import logging
import random
from random import randint
import asyncio
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardRemove
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.dispatcher.filters import Command
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import pandas as pd
from secret import TOKEN

print("*БОТ_ЗАПУЩЕН*")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

connected_users = []  # ученики
vip_users = []  # вожатые


# оздание стиха
class Makarov:
    # текст для обучения модели на основе цепей Маркова
    text = '''
    На заре ты еще со мной,
    На заре ты со мною.
    Но позже ты приходишь в дом,
    Где я одна сижу.
    '''

    # создаем словарь для цепей Маркова
    def generate_dict(text):
        words = text.split()
        word_dict = {}
        for i in range(len(words) - 1):
            if words[i] not in word_dict:
                word_dict[words[i]] = []
            word_dict[words[i]].append(words[i + 1])
        return word_dict

    # генерация нового текста на основе цепей Маркова
    def generate_text(word_dict, length=50):
        start_word = random.choice(list(word_dict.keys()))
        new_text = [start_word]
        for i in range(length):
            last_word = new_text[-1]
            if last_word in word_dict:
                next_word = random.choice(word_dict[last_word])
                new_text.append(next_word)
            else:
                start_word = random.choice(list(word_dict.keys()))
                new_text.append(start_word)
        return ' '.join(new_text)

    # создание словаря на основе текста
    word_dict = generate_dict(text)

    # генерация нового стиха
    new_text = generate_text(word_dict)
    print(new_text)


#  Функция для тестов какой нибудь дичи

@dp.message_handler(commands=['test'])
async def send_test(m: types.Message):
    await m.answer(m['Message'])


@dp.message_handler(commands=['start'], state='*')
async def send_welcome(m: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb2 = types.KeyboardButton(text="Вожатый")
    kd1 = types.KeyboardButton(text="Участник")
    keyboard.add(kd1, kb2)
    await m.answer(
        "Привет! Это организационный бот, он поможет Вам удобно и главное БЫСТРО руководить боольшой группой людей. \n Вы Вожатый или Участник?",
        reply_markup=keyboard)
    await state.set_state("q0")


@dp.message_handler(lambda message: message.text == "Вожатый", state='q0')
async def Student_change(m: types.Message, state: FSMContext):
    await m.reply(f"Привет, {m.from_user.first_name}", reply_markup=ReplyKeyboardRemove())
    await state.set_state("q-2")  # надо дописать


@dp.message_handler(lambda message: message.text == "Участник", state='q0')
async def Student_change(m: types.Message, state: FSMContext):
    await m.reply("Введите Своё ФИО в формате - Фамилия Имя Отчества", reply_markup=ReplyKeyboardRemove())
    await state.set_state("q1")


# @dp.message_handler(state='q-1')
# async def send_welcome(m: types.Message, state: FSMContext):
#     await m.reply("Введите Своё ФИО в формате - Фамилия Имя Отчества")
#     await state.set_state("q1")


# @dp.message_handler(state="q")
# async def choose(message: types.Message, state: FSMContext):
# if message.text == "3040":


# Записываем отряд ученикам
@dp.message_handler(state="q1")
async def process_name(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data({"name": name})
    await message.answer("Кто твои важатые?\nВ формате - Имя и Имя")
    await state.set_state("q2")


# Отправляет портфолио
@dp.message_handler(state="q2")
async def process_age(message: types.Message, state: FSMContext):
    age = message.text
    await state.update_data({"age": age})
    await message.answer("Где ты живешь?\nВ формате - Корпус-Комната")
    await state.set_state("q3")


@dp.message_handler(state="q3")
async def home_state(m: types.Message, state: FSMContext):
    home = m.text
    await state.update_data({"home": home})
    await state.set_state("Homepage_student")
    await home_page(m, state)


ikb = InlineKeyboardMarkup()
inline_btn_1 = InlineKeyboardButton('Расписание', callback_data='button1')
inline_btn_2 = InlineKeyboardButton('Ативности', callback_data='button2')
ikb.add(inline_btn_1, inline_btn_2)


@dp.message_handler(state="Homepage_student")
async def home_page(m: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data["name"]
    age = data["age"]
    home = data["home"]
    await bot.send_message(chat_id=m.from_user.id,
                           text=f"Имя:{name}\nОтряд:{age}\nКомната:{home}",
                           reply_markup=ikb)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
