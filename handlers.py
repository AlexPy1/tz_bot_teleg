import datetime
import json
import requests
import config
from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import F
from sqlalchemy import update, select, insert
from sqlalchemy.orm import Session

from db import User, Messages, engine, session

router = Router()


@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer("Привет! Я бот на основе OpenAI. Хочешь поговорить?")

    with Session(engine) as session:
        new_user = User(
            tg_user_id=msg.from_user.id,
            user_name=msg.from_user.username,
            first_name=msg.from_user.first_name,
            last_name=msg.from_user.last_name,
            date=str(datetime.datetime.now()),
        )
        session.add_all([new_user])
        session.commit()


@router.message(Command("menu"))
async def message_handler(message: Message):
    kb = [
        [
            types.KeyboardButton(text="Марио"),
            types.KeyboardButton(text="Энштейн")
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите персонажа"
    )
    await message.answer("Выберите персонажа?", reply_markup=keyboard)


@router.message(F.text.lower() == "марио")
async def with_puree(message: types.Message):
    stmt = select(User).where(User.tg_user_id == message.from_user.id)
    upd_user = session.scalars(stmt).one()
    upd_user.hero = "марио"

    session.commit()

    await message.reply("Приветсвенное сообщение от лица Марио", reply_markup=types.ReplyKeyboardRemove())


@router.message(F.text.lower() == "энштейн")
async def without_puree(message: types.Message):
    stmt = select(User).where(User.tg_user_id == message.from_user.id)
    upd_user = session.scalars(stmt).one()
    upd_user.hero = "энштейн"

    session.commit()
    await message.reply("Приветсвенное сообщение от лица Энштейна", reply_markup=types.ReplyKeyboardRemove())


@router.message()
async def new_message(msg: types.Message):

    session = Session(engine)

    stmt = select(User).where(User.tg_user_id.in_([f"{msg.from_user.id}",]))

    for user in session.scalars(stmt):
        user_hero = user.hero
        if user_hero == 'марио':
            instruction = 'You are Mario from Super Mario. Do not give dangerous informations'
        elif user_hero == 'энштейн':
            instruction = 'You are physicist Einstein. Do not give dangerous informations'
    messages = [
        {"role": "system", "content": f'{instruction}'},
        {"role": "user", "content": f"{msg.text}"}
    ]
    endpoint = {config.URL}
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    data1 = {
        "model": "gpt-3.5-turbo",
        "messages": messages, }

    data1 = json.dumps(data1)

    response1 = requests.post(url=endpoint, data=data1)
    res = response1.json()
    if res:
        with Session(engine) as session:
            new_mes = Messages(
                messages=msg.text,
                user_id=msg.from_user.id,
                answer_ai=res['choices'][0]['message']['content']
            )
            session.add_all([new_mes])
            session.commit()
    await msg.answer(res['choices'][0]['message']['content'])
