import logging
import random
import json
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


#  Функция для тестов какой нибудь дичи


@dp.message_handler(commands=['start'], state='*')
async def send_welcome(m: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb2 = types.KeyboardButton(text="Вожатый")
    kd1 = types.KeyboardButton(text="Участник")
    keyboard.add(kd1, kb2)
    await m.answer(
        "Привет! Это организационный бот, он поможет Вам удобно и главное БЫСТРО руководить боольшой группой людей. "
        "\n Вы Вожатый или Участник?",
        reply_markup=keyboard)
    await state.set_state("q0")


@dp.message_handler(lambda message: message.text == "Вожатый", state='q0')
async def Student_change(m: types.Message, state: FSMContext):
    await m.reply(f"Привет, {m.from_user.first_name}, что бы Вы хотели сделать??\nСписок зарегестрированных учеников /pupils\nПосмотреть расписание /scadle и заменить рамписание /scadle_change\nСделать объявление /msg\n", reply_markup=ReplyKeyboardRemove())
    message = "Ученики: \n"
    acc = json.loads(open('1.json', 'r', encoding='utf-8').read())
    for i in acc:
        message += "Имя:" + acc[i]['name'] + " Отряд:" + acc[i]['age'] + " Комната" + acc[i]['room'] + "\n"
    await state.set_state("q-2")  # надо дописать


@dp.message_handler(commands=['pupils'])
async def Students_list_print(m: types.Message):
    message = "Ученики: \n"
    acc = json.loads(open('1.json', 'r', encoding='utf-8').read())
    for i in acc:
        message += "Имя:" + acc[i]['name'] + " Отряд:" + acc[i]['age'] + " Комната" + acc[i]['room'] + "\n"
    await m.reply(message)


@dp.message_handler(lambda message: message.text == "Участник", state='q0')
async def Student_change(m: types.Message, state: FSMContext):
    await m.reply(f"Как тебя зовут?\nВ формате - Имя Фамилия Отчество", reply_markup=ReplyKeyboardRemove())
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
    print("ДОБАВЛЕН НОВЫЙ ПОЛЬЗОВАТЕЛЬ")
    await state.update_data({"home": home})
    await state.set_state("Homepage_student")
    data = await state.get_data()
    name = data["name"]
    age = data["age"]
    home = data["home"]
    acc = json.loads(open('1.json', 'r').read())
    acc[str(m['from']['id'])] = {"name": name, "age": age, "room": home}
    open('1.json', 'w').write(json.dumps(acc))

    await home_page(m, state)


# ВСЕ ИНАЛЙНИ КНОПКИ
ikb = InlineKeyboardMarkup()
inline_btn_1 = InlineKeyboardButton('Расписание', callback_data='button1')
inline_btn_2 = InlineKeyboardButton('Ативности', callback_data='button2')
ikb.add(inline_btn_1, inline_btn_2)

ikb2 = InlineKeyboardMarkup()
inline_btn_11 = InlineKeyboardButton('', callback_data='button3')
inline_btn_21 = InlineKeyboardButton('Ативности', callback_data='button4')
ikb2.add(inline_btn_11, inline_btn_21)


@dp.callback_query_handler(lambda c: c.data == 'button1')
async def button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_reply_markup(callback_query.from_user.id,
                                        callback_query.message.message_id,
                                        reply_markup=ikb2)
    await bot.edit_message_text(message_id=callback_query.message.message_id,
                                chat_id=callback_query.from_user.id,
                                text='Hello')


@dp.message_handler(state="Homepage_student")
async def home_page(m: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data["name"]
    age = data["age"]
    home = data["home"]
    await bot.send_message(chat_id=m.from_user.id,
                           text=f"Имя:{name}\nОтряд:{age}\nКомната:{home}",
                           reply_markup=ikb)


@dp.message_handler(state="Activites")
async def home_page(m: types.Message, state: FSMContext):
    await bot.send_message(chat_id=m.from_user.id,
                           text=f"Это все наши активности и инофрмация которая может быть полезной",
                           reply_markup=ikb2)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
