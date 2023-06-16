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
from secret import TOKEN, CODE01, CODE02, CODE03

print("*БОТ_ЗАПУЩЕН*")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

connected_users = []  # ученики

# ВСЕ ИНАЛЙНИ КНОПКИ
ikb = InlineKeyboardMarkup(row_width=2)
inline_btn_1 = InlineKeyboardButton('Расписание', callback_data='schedule')
inline_btn_2 = InlineKeyboardButton('Активности', callback_data='activities')
ikb.add(inline_btn_1, inline_btn_2)

ikb2 = InlineKeyboardMarkup(row_width=2)
inline_btn_3 = InlineKeyboardButton('Назад', callback_data='back_from_activities')
inline_btn_4 = InlineKeyboardButton(url='https://theuselessweb.com/', text="Веселый сайт", callback_data='funny_site')
inline_btn_10 = InlineKeyboardButton(url='http://ihasabucket.com/', text="Мем про ведро", callback_data='Meme')
ikb2.add(inline_btn_3, inline_btn_4)

ikb3 = InlineKeyboardMarkup(row_width=2)
inline_btn_5 = InlineKeyboardButton('Назад', callback_data='back')
ikb3.add(inline_btn_5)

ikb4 = InlineKeyboardMarkup(row_width=3)
inline_btn_7 = InlineKeyboardButton('Участники', callback_data='button7')
inline_btn_8 = InlineKeyboardButton('Сделать расссылку', callback_data='attention')
inline_btn_9 = InlineKeyboardButton('Изменить рассписание', callback_data='change_schedule')
ikb4.add(inline_btn_7, inline_btn_8, inline_btn_9)


@dp.message_handler(commands=['start'], state='*')
async def send_welcome(m: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb2 = types.KeyboardButton(text="Куратор")
    kd1 = types.KeyboardButton(text="Участник")
    keyboard.add(kd1, kb2)
    await m.answer(
        "☸Привет! Это организационный бот, он поможет Вам удобно и главное БЫСТРО руководить боольшой группой людей.фы В этом боте есть Куратор и Участник: чтобы быть куратором вы должны ввести код,который может быть получен от администрации, чтобы быть участником Вам надо всего то пройти быструю регистрцию. (данная версия бота являеться первой и узконаправленной) "
        "\n Вы Куратор или Участник?",
        reply_markup=keyboard)
    await state.set_state("q0")


@dp.message_handler(lambda message: message.text == "Куратор", state='q0')
async def Student_change1(m: types.Message, state: FSMContext):
    await m.reply(
        f"⛔Привет, {m.from_user.first_name}, чтобы Зарегестрироваться как Куратор, Вам нужно написать код для входа:",
        reply_markup=ReplyKeyboardRemove())
    await state.set_state("q-2")  # надо дописать


@dp.message_handler(lambda message: message.text == "Участник", state='q0')
async def Student_change2(m: types.Message, state: FSMContext):
    await m.reply(f"☒Как тебя зовут?\nВ формате - Фамилия Имя Отчество", reply_markup=ReplyKeyboardRemove())
    await state.set_state("q1")


@dp.message_handler(lambda message: message.text == CODE01 or message.text == CODE02 or message.text == CODE03, state="q-2")
async def Curator_key(m: types.Message, state: FSMContext):
    await m.answer(f"❖{m.from_user.first_name}, что Вы хотите сделать?", reply_markup=ikb4)
    await state.set_state("q-3")


@dp.message_handler(state="q-3")
async def Curator_home(m: types.Message, state: FSMContext):
    await m.answer(f"❖{m.from_user.first_name}, что Вы хотите сделать?", reply_markup=ikb4)


@dp.callback_query_handler(lambda c: c.data == 'attention', state="*")
async def Students_atension(m: types.CallbackQuery, state: FSMContext):
    await bot.send_message(m.from_user.id, "Напишите сообщение:")
    await state.set_state("wait_message_for_mail")


@dp.message_handler(state="wait_message_for_mail")
async def mail(m: types.Message, state: FSMContext):
    acc = json.loads(open('1.json', 'r', encoding='utf-8').read())
    for i in acc:
        await bot.send_message(chat_id=i, text=f'@{m.from_user.username} пишет:\n"{m.text}"')
    await state.reset_state(with_data=False)


@dp.callback_query_handler(lambda c: c.data == 'change_schedule', state="*")
async def schedule_satart(m: types.CallbackQuery, state: FSMContext):
    await bot.send_message(chat_id=m.from_user.id, text=f'⊚Напишите расписание в формате\nОбед 13:40\nУжин 14:30\nБез лишних слов информации: Название Время:')
    await state.set_state("schedule0")


@dp.message_handler(state="schedule0")
async def schedule_input(m: types.Message, state: FSMContext):
    text = m.text
    new_schedule = {}
    for line in text.split('\n'):
        label, time = line.split()
        new_schedule[label] = time

    with open('schedule.json', 'w') as file:
        file.write(json.dumps(new_schedule))
    await bot.send_message(chat_id=m.from_user.id, text="✅Расписание успешно записано!")
    await state.set_state("q-3")


#  Печать всех учеников по тексту Участиники
@dp.callback_query_handler(lambda c: c.data == 'button7', state="*")
async def students_list(m: types.CallbackQuery, state: FSMContext):
    message = "Ученики:\n"
    acc = json.loads(open('1.json', 'r', encoding='utf-8').read())
    for i in acc:
        message += "➣ Имя:" + acc[i]['name'] + "\n  ◆ Курс:" + acc[i]['age'] + "\n  ◆ Комната" + acc[i]['room'] + "\n"
    await bot.send_message(chat_id=m.from_user.id, text=message)


# Записываем отряд ученикам
@dp.message_handler(state="q1")
async def process_name(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data({"name": name})
    await message.answer("☒На каком курсе ты учишься?\nВ формате - Название")
    await state.set_state("q2")


# Отправляет портфолио и Добавление новых пользователей и home_page Student
@dp.message_handler(state="q2")
async def process_age(m: types.Message, state: FSMContext):
    age = m.text
    await state.update_data({"age": age})
    await m.answer("☒Где ты живешь?\nВ формате - Корпус-Комната")
    home = m.text
    print("ДОБАВЛЕН НОВЫЙ ПОЛЬЗОВАТЕЛЬ")
    await state.update_data({"home": home})
    await state.set_state("Homepage_student")
    data = await state.get_data()
    name = data["name"]
    age = data["age"]
    home = data["home"]
    with open('1.json', 'r', encoding='utf-8') as file:
        acc = json.loads(file.read())
    acc[str(m['from']['id'])] = {"name": name, "age": age, "room": home}
    open('1.json', 'w').write(json.dumps(acc))
    connected_users.append(m.from_user.id)
    await state.set_state("q3")


#  Добавление новых пользователей и home_page Student
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
    connected_users.append(m.from_user.id)
    await m.answer(text="✅Регистрация прошла успешно!")
    await bot.send_message(chat_id=m.from_user.id,
                           text=f"❧Твой профиль!☙\n◉ Имя:{name}\n◎ Курс:{age}\n◎ Комната:{home}",
                           reply_markup=ikb)
    await state.set_state("Homepage_student")


@dp.message_handler(state="Homepage_student")
async def home_page(m: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data["name"]
    age = data["age"]
    home = data["home"]
    await bot.send_message(chat_id=m.from_user.id,
                           text=f"❧Твой профиль!☙\n◉ Имя:{name}\n◎ Курс:{age}\n◎ Комната:{home}",
                           reply_markup=ikb)


@dp.callback_query_handler(lambda c: c.data == '', state='*')
async def back_to_curator_home_page(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(chat_id=callback_query.from_user.id, text=f"❖{callback_query.from_user.id.first_name}, что Вы хотите сделать?", reply_markup=ikb4)
    await state.set_state("q-3")


#Расписание
@dp.callback_query_handler(lambda c: c.data == 'schedule', state='*')
async def button1(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    message = "ℹ️Расписание:\n"
    acc = json.loads(open('schedule.json', 'r').read())
    for i in acc:
        message += i + " : " + acc[i] + "\n"
    await bot.edit_message_text(message_id=callback_query.message.message_id,
                                chat_id=callback_query.from_user.id,
                                text=message, reply_markup=ikb3)


@dp.callback_query_handler(lambda c: c.data == 'activities', state='*')
async def button2(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                text=f"★Все интересные активности которые пока доступны!★",
                                reply_markup=ikb2)


#  buttonback_from_activities3 - Назад
@dp.callback_query_handler(lambda c: c.data == 'back_from_activities', state='*')
async def button3(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    data = await state.get_data()
    name = data["name"]
    age = data["age"]
    home = data["home"]
    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                text=f"❧Твой профиль!☙\n◉ Имя:{name}\n◎ Курс:{age}\n◎ Комната:{home}",
                                reply_markup=ikb)


#  back - Назад
@dp.callback_query_handler(lambda c: c.data == 'back', state='*')
async def button5(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    data = await state.get_data()
    name = data["name"]
    age = data["age"]
    home = data["home"]
    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                text=f"❧Твой профиль!☙\n◉ Имя:{name}\n◎ Курс:{age}\n◎ Комната:{home}",
                                reply_markup=ikb)


@dp.callback_query_handler(lambda c: c.data == 'back_from_activities', state='*')
async def button5_(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    data = await state.get_data()
    name = data["name"]
    age = data["age"]
    home = data["home"]
    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                text=f"❧Твой профиль!☙\n◉ Имя:{name}\n◎ Курс:{age}\n◎ Комната:{home}",
                                reply_markup=ikb)


@dp.callback_query_handler(state='*')
async def any_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query_id=callback_query.id)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
