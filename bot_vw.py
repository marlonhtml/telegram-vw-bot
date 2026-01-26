import telebot
from telebot import types
from dotenv import load_dotenv
import os
import requests
from datetime import datetime

load_dotenv()

bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN").strip())
access_token = os.getenv("ACCESS_TOKEN").strip()

header = {
    'Access-Token': access_token
}

staff_ranks = {
    'HELPER': 'Хелпер',
    'MODER': 'Модер',
    'WARDEN': 'Проверенный Модер',
    'CHIEF': 'Гл.Модер',
    'ADMIN': 'Гл.Админ'
}

miniGames = {}

def getMiniGames():
    response = requests.get('https://api.vimeworld.com/misc/games', headers=header)
    if response.status_code == 200:
        data = response.json()
        for game in data:
            miniGames[game['id'].lower()] = game['name']

getMiniGames()

def getGameById(id):
    return miniGames.get(id.lower(), id)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    btn2 = types.InlineKeyboardButton("Поиск игрока", callback_data='player_info')
    btn3 = types.InlineKeyboardButton("Онлайн VimeWorld", callback_data='online_count')
    btn4 = types.InlineKeyboardButton("Ссылка на разраба", url='https://guns.lol/marlonhd')
    btn5 = types.InlineKeyboardButton("Помощь", callback_data='help')
    btn6 = types.InlineKeyboardButton("Стафф онлайн", callback_data='staff_online')
    markup.add(btn2, btn3, btn5)
    markup.row(btn4, btn6)
    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}, чем могу помочь?",
        reply_markup=markup
    )

@bot.message_handler(commands=['help'])
def help(message):
    markup= types.InlineKeyboardMarkup()
    btn1= types.InlineKeyboardButton("Назад", callback_data='start')
    markup.add(btn1)
    bot.send_message(
        message.chat.id,
        f"Этот бот может предоставить информацию об игроках и количестве игроков онлайн на VimeWorld. Используйте кнопки ниже /start для навигации. Бот находится в разработке, и новые функции будут добавляться со временем."
    , reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: True)
def callback_query(callback):
    if callback.data == 'player_info':
        bot.send_message(callback.message.chat.id, "Введите ник игрока:")
        bot.register_next_step_handler(callback.message, get_player_info)

    elif callback.data == 'online_count':
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Назад", callback_data='start')
        markup.add(btn1)
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
            bot.send_message(callback.message.chat.id, answer, reply_markup=markup)
        else:
            bot.send_message(callback.message.chat.id, "Ошибка при получении данных об онлайне." , reply_markup=markup)

    elif callback.data == 'help':
        help(callback.message)

    elif callback.data == 'start':
        start(callback.message)

    elif callback.data == 'staff_online':
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Назад", callback_data='start')
        markup.add(btn1)
        response = requests.get('https://api.vimeworld.com/online/staff', headers=header)
        if response.status_code == 200:
            try:
                data = response.json()
                if not data:
                    bot.send_message(callback.message.chat.id, "Сейчас на сервере нет онлайн стаффа.", reply_markup=markup)
                else:
                    staff_info = (
                        f"👮‍♂️ Онлайн стафф VimeWorld ({len(data)} игроков):\n"
                        # f"{data[0]['username']} - {data[0]['rank']}\n"
                    )
                    bot.send_message(callback.message.chat.id, staff_info)
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
                    bot.send_message(callback.message.chat.id, staff_details, reply_markup=markup)
            except ValueError:
                bot.send_message(callback.message.chat.id, "Ошибка при обработке данных о стаффе.", reply_markup=markup)
                return

def get_player_info(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Назад", callback_data='start')
    markup.add(btn1)
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

            bot.send_message(message.chat.id, player_info, reply_markup=markup)
        except (IndexError, KeyError, ):
            bot.send_message(message.chat.id, "Нет информации об этом игроке." , reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Игрок не найден.", reply_markup=markup)

bot.polling(none_stop=True)

#TODO 
# на респонсы добавить кнпоку выхода в старт СДЕЛАНО №№№№№№№№№№№№№№ праздник
# добавить возможность просмотра онлайн-стаффа СДЕЛАНО №№№№№№№№№№№№№№ праздник
# добавить возможность просмотра гильдий
# добавить возможность следить за игрком (уведомления когда зайдет в игру) СЛОЖНО
