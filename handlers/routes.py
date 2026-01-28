from datetime import datetime
import requests
from config import VIMEtoken
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

router = Router()

header = {
    'Access-Token': VIMEtoken
}

staff_ranks = {
    'HELPER': 'Хелпер',
    'MODER': 'Модер',
    'WARDEN': 'Проверенный Модер',
    'CHIEF': 'Гл.Модер',
    'ADMIN': 'Гл.Админ'
}

miniGames = {}

class Form(StatesGroup):
    nickname = State()

def getMiniGames():
    response = requests.get('https://api.vimeworld.com/misc/games', headers=header)
    if response.status_code == 200:
        data = response.json()
        for game in data:
            miniGames[game['id'].lower()] = game['name']

getMiniGames()

def getGameById(id):
    return miniGames.get(id.lower(), id)

def get_main_inline_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
             InlineKeyboardButton(text="Поиск игрока", callback_data='search_player'), 
             InlineKeyboardButton(text="Онлайн VimeWorld", callback_data='online_count'),
             InlineKeyboardButton(text="Помощь", callback_data='help')
            ],

            [
             InlineKeyboardButton(text="Ссылка на разраба", url="https://guns.lol/marlonhd"),
             InlineKeyboardButton(text="Стафф онлайн", callback_data='staff_online')
            ]
        ]
    )
    return keyboard

def back_to_main_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data='backToMain')]
        ]
    )
    return keyboard

@router.callback_query(lambda c: c.data == "more_info")
async def process_more_info(callback: CallbackQuery):
    await callback.message.answer("Here is more information about the bot!", reply_markup=back_to_main_keyboard())
    await callback.answer()

@router.callback_query(lambda c: c.data == "backToMain")
async def process_back_to_main(callback: CallbackQuery):
    await start(callback.message)
    await callback.answer()

@router.callback_query(lambda c: c.data == "online_count")
async def process_online_count(callback: CallbackQuery):
    response = requests.get('https://api.vimeworld.com/online', headers=header)

    if response.status_code == 200:
        data = response.json()
        total = data['total']
        totalSeparate = data['separated']
        sorted_modes = sorted([(getGameById(mode), count) for mode, count in totalSeparate.items()], key=lambda x: x[1], reverse=True)
        modes_str = []
        tab = "\n\t- "

        for modes in sorted_modes:
            modes_str.append(f"{modes[0]}: {modes[1]}")

        # print(totalSeparate)
        answer = f"🌐 Сейчас на сервере VimeWorld: {total} игроков онлайн.\n\n🕹️ Топ 5 режимов по онлайну:\n\t- {tab.join(modes_str[:5])}"
        await callback.message.answer(answer, reply_markup=back_to_main_keyboard())
    else:
        await callback.message.answer("Ошибка при получении данных об онлайне.", reply_markup=back_to_main_keyboard())
    await callback.answer()

@router.callback_query(lambda c: c.data == "help")
async def process_help(callback: CallbackQuery):
    await help(callback.message)
    await callback.answer()

@router.callback_query(lambda c: c.data == "staff_online")
async def process_staff_online(callback: CallbackQuery):
    response = requests.get('https://api.vimeworld.com/online/staff', headers=header)

    if response.status_code == 200:
        try:
            data = response.json()

            if not data:
                await callback.message.answer("Сейчас на сервере нет онлайн стаффа.", reply_markup=back_to_main_keyboard())
            else:
                staff_info = (
                    f"👮‍♂️ Онлайн стафф VimeWorld ({len(data)} игроков):\n"
                )
                await callback.message.answer(staff_info)
                staff_details = ""
                for staff in data:
                    if staff['rank'] not in staff_ranks:
                        continue
                    else:
                        staff['rank'] = staff_ranks[staff['rank']]
                    staff_detatails = (
                        f"👤 Игрок: {staff['username']}\n\t- Должность: {staff['rank']}\n"
                    )
                    staff_details += staff_detatails + "\n"
                await callback.message.answer(staff_details, reply_markup=back_to_main_keyboard())
        except ValueError:
            await callback.message.answer("Ошибка при обработке данных о стаффе.", reply_markup=back_to_main_keyboard())
            return
    await callback.answer()

@router.callback_query(lambda c: c.data == "search_player")
async def process_search_player(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Пожалуйста, введите имя игрока для поиска:")
    await state.set_state(Form.nickname)
    await callback.answer()

@router.message(Form.nickname, F.text.lower())
async def process_player_nickname(message: Message, state: FSMContext):
    # nickname = message.text.strip()
    response = requests.get(f'https://api.vimeworld.com/user/name/{message.text}', headers=header)
    if response.status_code == 200:
        try:
            data = response.json()
            
            # Обработка lastSeen - может быть timestamp или строка
            last_seen = data[0]['lastSeen']
            if isinstance(last_seen, (int, float)):
                try:
                    last_seen_str = datetime.fromtimestamp(last_seen).strftime('%d-%m-%Y %H:%M:%S')
                except (OSError, ValueError):
                    # Если timestamp некорректный
                    last_seen_str = "очень давно"
            else:
                last_seen_str = str(last_seen)
            
            player_info = (
                f"👤 Игрок: {data[0]['username']}\n"
                f"🆔 ID: {data[0]['id']}\n"
                f"⭐ Ранг: {data[0]['rank']}\n"
                f"📊 Уровень: {data[0]['level']}\n"
                f"⏱️ Наиграно: {data[0]['playedSeconds'] // 3600}ч\n"
                f"👨‍💻 Последний раз в сети: {last_seen_str}"
                
            )
            response2 = requests.get(f'https://api.vimeworld.com/user/session/{data[0]["id"]}', headers=header)
            try:
                if response2.status_code == 200:
                    data2 = response2.json()

                    if data2[0]['online']['value']:
                        player_info += f"\n🟢 Статус: В сети, {data2[0]['online']['message']}"
                    else:
                        player_info += f"\n🔴 Статус: Не в сети"
                        
            except (IndexError, KeyError):
                player_info += f"\n☠️ Статус: Неизвестен"

            await message.answer(player_info, reply_markup=back_to_main_keyboard())
        except (IndexError, KeyError, ):
            await message.answer("Нет информации об этом игроке." , reply_markup=back_to_main_keyboard())
    else:
        await message.answer("Игрок не найден.", reply_markup=back_to_main_keyboard())
    await state.clear()

@router.message(Command("start"))
@router.message(F.text.lower() == "start")
async def start(message: Message):
    await message.answer(f"Привет, {message.from_user.first_name}, чем могу помочь?", reply_markup=get_main_inline_keyboard())

@router.message(Command("help"))
async def help(message: Message):
    await message.answer("Этот бот может предоставить информацию об игроках и количестве игроков онлайн на VimeWorld. Используйте кнопки ниже /start для навигации. Бот находится в разработке, и новые функции будут добавляться со временем.", reply_markup=back_to_main_keyboard())