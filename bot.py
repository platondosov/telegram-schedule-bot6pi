import telebot
from telebot import types
from datetime import datetime, timedelta
import requests
import os
import time
import threading
from flask import Flask
import json
import pickle
import atexit

# Flask приложение для Render
app = Flask(__name__)


@app.route('/')
def home():
    return "Bot is running!", 200


@app.route('/ping')
def ping():
    return "pong", 200


@app.route('/health')
def health():
    return "OK", 200


def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


BOT_TOKEN = "8577449187:AAEEqSAH-68KoYSHHIbiIp1ObjvHDlR6ojA"
bot = telebot.TeleBot(BOT_TOKEN)

# Дата начала весеннего семестра 2025-2026
START_DATE = datetime(2026, 2, 9)

# Словари для хранения данных пользователей
user_selected_weeks = {}
user_selected_subgroups = {}  # 1 или 2 подгруппа
DATA_FILE = "user_data.pkl"


def save_data():
    """Сохраняет данные пользователей в файл"""
    try:
        data = {
            'weeks': user_selected_weeks,
            'subgroups': user_selected_subgroups
        }
        with open(DATA_FILE, 'wb') as f:
            pickle.dump(data, f)
        print("🌸 Данные сохранены")
    except Exception as e:
        print(f"💔 Ошибка сохранения данных: {e}")


def load_data():
    """Загружает данные пользователей из файла"""
    global user_selected_weeks, user_selected_subgroups
    try:
        with open(DATA_FILE, 'rb') as f:
            data = pickle.load(f)
            user_selected_weeks = data.get('weeks', {})
            user_selected_subgroups = data.get('subgroups', {})
        print(f"🌸 Данные загружены. Пользователей: {len(user_selected_subgroups)}")
    except FileNotFoundError:
        print("💫 Файл данных не найден, создаем новый")
        user_selected_weeks = {}
        user_selected_subgroups = {}
    except Exception as e:
        print(f"💔 Ошибка загрузки данных: {e}")
        user_selected_weeks = {}
        user_selected_subgroups = {}


# Загружаем данные при старте
load_data()
atexit.register(save_data)


# Функция определения текущей недели
def get_current_week():
    today = datetime.now()
    if today < START_DATE:
        return "I"

    days_diff = (today - START_DATE).days
    week_num = (days_diff // 7) % 2
    return "I" if week_num == 0 else "II"


# Функция получения недели для конкретного пользователя
def get_user_week(user_id):
    """Возвращает неделю для пользователя: выбранную или автоматическую"""
    if user_id in user_selected_weeks:
        if user_selected_weeks[user_id] == "auto":
            return get_current_week()
        return user_selected_weeks[user_id]
    return get_current_week()


# Функция получения подгруппы пользователя
def get_user_subgroup(user_id):
    """Возвращает подгруппу пользователя (1 или 2)"""
    return user_selected_subgroups.get(user_id, 1)  # По умолчанию 1 подгруппа


# Расписание для двух подгрупп (ВАШЕ НОВОЕ РАСПИСАНИЕ)
schedule = {
    # Подгруппа 1
    1: {
        "Понедельник": {
            "I": """🌸 *ПОНЕДЕЛЬНИК | I неделя | Подгруппа 1*

✨ *1 пара (08:00-09:25):*
• Английский язык (пз 233-2 общ.)

✨ *2 пара (09:35-11:00):*
• Физика (лк 137-4)

✨ *3 пара (11:25-12:50):*
• Физика (лр 506, 512, 503, 513-1)

✨ *4 пара (13:00-14:25):*
• Основы алгоритмизации и программирования (лр 324-1)""",

            "II": """🌸 *ПОНЕДЕЛЬНИК | II неделя | Подгруппа 1*

✨ *1 пара (08:00-09:25):*
• Свободно

✨ *2 пара (09:35-11:00):*
• Великая Отечественная война советского народа (лк 222-4)

✨ *3 пара (11:25-12:50):*
• Физика (лр 506, 512, 503, 513-1)

✨ *4 пара (13:00-14:25):*
• Основы алгоритмизации и программирования (лр 324-1)"""
        },

        "Вторник": {
            "I": """🌸 *ВТОРНИК | I неделя | Подгруппа 1*

✨ *1 пара (08:00-09:25):*
• Свободно

✨ *2 пара (09:35-11:00):*
• Основы алгоритмизации и программирования (лк 100-3а)

✨ *3 пара (11:25-12:50):*
• Физика (лк 114-4)

✨ *4 пара (13:00-14:25):*
• Конструирование программного обеспечения (лр 322-1)""",

            "II": """🌸 *ВТОРНИК | II неделя | Подгруппа 1*

✨ *1 пара (08:00-09:25):*
• Алгоритмы и структуры данных (лр 209-1)

✨ *2 пара (09:35-11:00):*
• Основы алгоритмизации и программирования (лк 100-3а)

✨ *3 пара (11:25-12:50):*
• Физика (лк 114-4)

✨ *4 пара (13:00-14:25):*
• Конструирование программного обеспечения (лр 322-1)"""
        },

        "Среда": {
            "I": """🌸 *СРЕДА | I неделя | Подгруппа 1*

✨ *1 пара (08:00-09:25):*
• История мировой культуры (пз 149-4) / Политология (пз 334-4)

✨ *2 пара (09:35-11:00):*
• История мировой культуры (лк 100-3а) / Политология (лк 137-4)

✨ *3 пара (11:25-12:50):*
• Алгоритмы и структуры данных (лк 440-4)

✨ *4 пара (13:00-14:25):*
• Физическая культура 🏃‍♀️""",

            "II": """🌸 *СРЕДА | II неделя | Подгруппа 1*

✨ *1 пара (08:00-09:25):*
• Свободно

✨ *2 пара (09:35-11:00):*
• История мировой культуры (лк 100-3а) / Политология (лк 137-4)

✨ *3 пара (11:25-12:50):*
• Компьютерные системы и сети (лк 440-4)

✨ *4 пара (13:00-14:25):*
• Физическая культура 🏃‍♀️"""
        },

        "Четверг": {
            "I": """🌸 *ЧЕТВЕРГ | I неделя | Подгруппа 1*

✨ *1 пара (08:00-09:25):*
• Физика (пз 110-4)

✨ *2 пара (09:35-11:00):*
• История белорусской государственности (лк 301-4)

✨ *3 пара (11:25-12:50):*
• История белорусской государственности (пз 334-4)

✨ *4 пара (13:00-14:25):*
• Математический анализ (пз 226-4)""",

            "II": """🌸 *ЧЕТВЕРГ | II неделя | Подгруппа 1*

✨ *1 пара (08:00-09:25):*
• Английский язык (пз 123-2 общ.)

✨ *2 пара (09:35-11:00):*
• История белорусской государственности (лк 301-4)

✨ *3 пара (11:25-12:50):*
• История белорусской государственности (пз 334-4)

✨ *4 пара (13:00-14:25):*
• Математический анализ (пз 226-4)"""
        },

        "Пятница": {
            "I": """🌸 *ПЯТНИЦА | I неделя | Подгруппа 1*

✨ *1 пара (08:00-09:25):*
• Математический анализ (лк 100-3а)

✨ *2 пара (09:35-11:00):*
• Конструирование программного обеспечения (лк 132-4)

✨ *3 пара (11:25-12:50):*
• Английский язык (пз 123-2 общ.)

✨ *4 пара (13:00-14:25):*
• Свободно 🎀""",

            "II": """🌸 *ПЯТНИЦА | II неделя | Подгруппа 1*

✨ *1 пара (08:00-09:25):*
• Математический анализ (лк 100-3а)

✨ *2 пара (09:35-11:00):*
• Конструирование программного обеспечения (лк 132-4)

✨ *3 пара (11:25-12:50):*
• Английский язык (пз 123-2 общ.)

✨ *4 пара (13:00-14:25):*
• Свободно 🎀"""
        },

        "Суббота": {
            "I": """🌸 *СУББОТА | I неделя | Подгруппа 1*

✨ *1 пара (08:00-09:25):*
• Свободно

✨ *2 пара (09:35-11:00):*
• Физическая культура 🏃‍♀️

✨ *3 пара (11:25-12:50):*
• Компьютерные системы и сети (лр 413-1)

✨ *4 пара (13:00-14:25):*
• Свободно 🎀""",

            "II": """🌸 *СУББОТА | II неделя | Подгруппа 1*

✨ *1 пара (08:00-09:25):*
• Свободно

✨ *2 пара (09:35-11:00):*
• Физическая культура 🏃‍♀️

✨ *3 пара (11:25-12:50):*
• Свободно

✨ *4 пара (13:00-14:25):*
• Свободно 🎀"""
        }
    },

    # Подгруппа 2
    2: {
        "Понедельник": {
            "I": """🌸 *ПОНЕДЕЛЬНИК | I неделя | Подгруппа 2*

✨ *1 пара (08:00-09:25):*
• Свободно

✨ *2 пара (09:35-11:00):*
• Физика (лк 137-4)

✨ *3 пара (11:25-12:50):*
• Конструирование программного обеспечения (лр 322-1)

✨ *4 пара (13:00-14:25):*
• Физика (лр 506, 512, 503, 513-1)""",

            "II": """🌸 *ПОНЕДЕЛЬНИК | II неделя | Подгруппа 2*

✨ *1 пара (08:00-09:25):*
• Свободно

✨ *2 пара (09:35-11:00):*
• Великая Отечественная война советского народа (лк 222-4)

✨ *3 пара (11:25-12:50):*
• Конструирование программного обеспечения (лр 322-1)

✨ *4 пара (13:00-14:25):*
• Физика (лр 506, 512, 503, 513-1)"""
        },

        "Вторник": {
            "I": """🌸 *ВТОРНИК | I неделя | Подгруппа 2*

✨ *1 пара (08:00-09:25):*
• Алгоритмы и структуры данных (лр 209-1)

✨ *2 пара (09:35-11:00):*
• Основы алгоритмизации и программирования (лк 100-3а)

✨ *3 пара (11:25-12:50):*
• Физика (лк 114-4)

✨ *4 пара (13:00-14:25):*
• Английский язык (пз 235-2 общ.)""",

            "II": """🌸 *ВТОРНИК | II неделя | Подгруппа 2*

✨ *1 пара (08:00-09:25):*
• Свободно

✨ *2 пара (09:35-11:00):*
• Основы алгоритмизации и программирования (лк 100-3а)

✨ *3 пара (11:25-12:50):*
• Физика (лк 114-4)

✨ *4 пара (13:00-14:25):*
• Английский язык (пз 235-2 общ.)"""
        },

        "Среда": {
            "I": """🌸 *СРЕДА | I неделя | Подгруппа 2*

✨ *1 пара (08:00-09:25):*
• История мировой культуры (пз 149-4) / Политология (пз 334-4)

✨ *2 пара (09:35-11:00):*
• История мировой культуры (лк 100-3а) / Политология (лк 137-4)

✨ *3 пара (11:25-12:50):*
• Алгоритмы и структуры данных (лк 440-4)

✨ *4 пара (13:00-14:25):*
• Физическая культура 🏃‍♀️""",

            "II": """🌸 *СРЕДА | II неделя | Подгруппа 2*

✨ *1 пара (08:00-09:25):*
• Свободно

✨ *2 пара (09:35-11:00):*
• История мировой культуры (лк 100-3а) / Политология (лк 137-4)

✨ *3 пара (11:25-12:50):*
• Компьютерные системы и сети (лк 440-4)

✨ *4 пара (13:00-14:25):*
• Физическая культура 🏃‍♀️"""
        },

        "Четверг": {
            "I": """🌸 *ЧЕТВЕРГ | I неделя | Подгруппа 2*

✨ *1 пара (08:00-09:25):*
• Физика (пз 110-4)

✨ *2 пара (09:35-11:00):*
• История белорусской государственности (лк 301-4)

✨ *3 пара (11:25-12:50):*
• История белорусской государственности (пз 334-4)

✨ *4 пара (13:00-14:25):*
• Математический анализ (пз 226-4)""",

            "II": """🌸 *ЧЕТВЕРГ | II неделя | Подгруппа 2*

✨ *1 пара (08:00-09:25):*
• Свободно

✨ *2 пара (09:35-11:00):*
• История белорусской государственности (лк 301-4)

✨ *3 пара (11:25-12:50):*
• История белорусской государственности (пз 334-4)

✨ *4 пара (13:00-14:25):*
• Математический анализ (пз 226-4)"""
        },

        "Пятница": {
            "I": """🌸 *ПЯТНИЦА | I неделя | Подгруппа 2*

✨ *1 пара (08:00-09:25):*
• Математический анализ (лк 100-3а)

✨ *2 пара (09:35-11:00):*
• Конструирование программного обеспечения (лк 132-4)

✨ *3 пара (11:25-12:50):*
• Основы алгоритмизации и программирования (лр 209-1)

✨ *4 пара (13:00-14:25):*
• Свободно 🎀""",

            "II": """🌸 *ПЯТНИЦА | II неделя | Подгруппа 2*

✨ *1 пара (08:00-09:25):*
• Математический анализ (лк 100-3а)

✨ *2 пара (09:35-11:00):*
• Конструирование программного обеспечения (лк 132-4)

✨ *3 пара (11:25-12:50):*
• Основы алгоритмизации и программирования (лр 209-1)

✨ *4 пара (13:00-14:25):*
• Свободно 🎀"""
        },

        "Суббота": {
            "I": """🌸 *СУББОТА | I неделя | Подгруппа 2*

✨ *1 пара (08:00-09:25):*
• Английский язык (пз 233-2 общ.)

✨ *2 пара (09:35-11:00):*
• Физическая культура 🏃‍♀️

✨ *3 пара (11:25-12:50):*
• Свободно

✨ *4 пара (13:00-14:25):*
• Свободно 🎀""",

            "II": """🌸 *СУББОТА | II неделя | Подгруппа 2*

✨ *1 пара (08:00-09:25):*
• Английский язык (пз 233-2 общ.)

✨ *2 пара (09:35-11:00):*
• Физическая культура 🏃‍♀️

✨ *3 пара (11:25-12:50):*
• Компьютерные системы и сети (лр 413-1)

✨ *4 пара (13:00-14:25):*
• Свободно 🎀"""
        }
    }
}


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id

    # Если пользователь не выбрал подгруппу, показываем меню выбора
    if user_id not in user_selected_subgroups:
        show_subgroup_selection(message)
        return

    # Продолжаем обычный старт
    user_week = get_user_week(user_id)
    user_subgroup = get_user_subgroup(user_id)
    today = datetime.now()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    # Кнопки дней недели с эмодзи
    days = ['🌸 Понедельник', '🌷 Вторник', '🌼 Среда', '💐 Четверг', '🌺 Пятница', '🌻 Суббота']
    buttons = [types.KeyboardButton(day) for day in days]

    # Располагаем по 2 кнопки в ряд
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            markup.row(buttons[i], buttons[i + 1])
        else:
            markup.row(buttons[i])

    # Дополнительные кнопки с эмодзи
    markup.row(
        types.KeyboardButton('📅 Сегодня'),
        types.KeyboardButton('📆 Завтра')
    )
    markup.row(
        types.KeyboardButton('🌸 Какая неделя?'),
        types.KeyboardButton('🔄 Сменить неделю')
    )
    markup.row(
        types.KeyboardButton('👥 Сменить подгруппу'),
        types.KeyboardButton('💖 Помощь')
    )

    # Определяем статус недели
    week_status = ""
    if user_id in user_selected_weeks:
        if user_selected_weeks[user_id] == "auto":
            week_status = "Автоматический режим ✨"
        else:
            week_status = f"Ручной режим: {user_selected_weeks[user_id]} неделя 💫"
    else:
        week_status = "Автоматический режим ✨"

    # Приветственное сообщение в девчачьем стиле
    week_num = (today - START_DATE).days // 7 + 1 if today >= START_DATE else 0
    welcome_msg = f"""
🌸✨ *Расписание БГТУ* ✨🌸

*💖 Семестр начинается:* 09.02.2026
*🌸 Текущая неделя:* {get_current_week()} неделя
*💫 Ваша неделя:* {user_week} неделя
*👥 Ваша подгруппа:* {user_subgroup}
*✨ Режим:* {week_status}
*📚 С начала семестра:* {week_num} учебная неделя

📅 *{today.strftime('%d.%m.%Y')}* ({['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'][today.weekday()]})

🌸 *Выберите день недели:*
"""

    bot.send_message(message.chat.id, welcome_msg,
                     reply_markup=markup, parse_mode='Markdown')
    # Сохраняем данные
    save_data()


def show_subgroup_selection(message):
    """Показывает меню выбора подгруппы"""
    markup = types.InlineKeyboardMarkup(row_width=2)

    btn_subgroup_1 = types.InlineKeyboardButton(
        '🌸 Подгруппа 1',
        callback_data='select_subgroup_1'
    )
    btn_subgroup_2 = types.InlineKeyboardButton(
        '🌷 Подгруппа 2',
        callback_data='select_subgroup_2'
    )

    markup.row(btn_subgroup_1, btn_subgroup_2)

    bot.send_message(
        message.chat.id,
        "🌸✨ *Добро пожаловать в бот расписания БГТУ!* ✨🌸\n\n"
        "💖 *Пожалуйста, выберите вашу подгруппу:*\n\n"
        "Вы всегда сможете сменить подгруппу в главном меню. 🎀",
        reply_markup=markup,
        parse_mode='Markdown'
    )


@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
🌸✨ *Помощь по боту* ✨🌸

*🌸 Основные команды:*
/start - Главное меню
/today - Расписание на сегодня
/tomorrow - Расписание на завтра
/week - Какая сейчас неделя (I/II)
/switch_week - Сменить неделю
/auto_week - Вернуться к автоматическому определению
/change_subgroup - Сменить подгруппу
/help - Эта справка

*💫 Как пользоваться:*
1. При первом запуске выберите свою подгруппу 👥
2. Нажмите на кнопку с днем недели 📅
3. Бот покажет расписание для этого дня ✨
4. Используйте кнопку "🔄 Сменить неделю" для переключения

*🎀 Режимы работы:*
• Автоматический - бот сам определяет текущую неделю 🤖
• Ручной - вы выбираете неделю вручную 👑

*💖 Информация:*
• Бот автоматически определяет I или II неделя
• Даты начала семестра: 09.02.2026
• Если пара не указана - время свободно 🎉

*✨ Приятного использования!* 🌸
"""
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')


@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = message.chat.id

    # Проверяем, выбрана ли подгруппа
    if user_id not in user_selected_subgroups:
        show_subgroup_selection(message)
        return

    # Убираем эмодзи для сравнения
    clean_text = message.text.replace('🌸 ', '').replace('🌷 ', '').replace('🌼 ', '') \
        .replace('💐 ', '').replace('🌺 ', '').replace('🌻 ', '')

    if message.text == '📅 Сегодня':
        show_day_schedule(message, "today")
    elif message.text == '📆 Завтра':
        show_day_schedule(message, "tomorrow")
    elif message.text == '🌸 Какая неделя?':
        week_command(message)
    elif message.text == '🔄 Сменить неделю':
        show_week_selection_menu(message)
    elif message.text == '👥 Сменить подгруппу':
        show_subgroup_selection(message)
    elif message.text == '💖 Помощь':
        help_command(message)
    elif clean_text in ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]:
        show_day_with_week_buttons(message, clean_text)
    else:
        bot.send_message(message.chat.id,
                         "🌸 Пожалуйста, выберите день недели из меню ниже 👇")


def show_day_schedule(message, day_type):
    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
    today = datetime.now().weekday()

    if day_type == "today":
        if today < 6:
            day_name = days[today]
            prefix = f"🌸✨ *СЕГОДНЯ ({day_name})* ✨🌸"
        else:
            bot.send_message(message.chat.id,
                             "🌸 Сегодня воскресенье - выходной день! 🎉✨\nОтдыхайте и готовьтесь к новой неделе! 💖")
            return
    else:  # tomorrow
        tomorrow = (today + 1) % 7
        if tomorrow < 6:
            day_name = days[tomorrow]
            tomorrow_date = datetime.now() + timedelta(days=1)
            prefix = f"🌸✨ *ЗАВТРА ({day_name}, {tomorrow_date.strftime('%d.%m')})* ✨🌸"
        else:
            bot.send_message(message.chat.id,
                             "🌸 Завтра воскресенье - выходной день! 🎉✨")
            return

    show_day_with_week_buttons(message, day_name, prefix)


def week_command(message):
    user_id = message.chat.id
    if user_id not in user_selected_subgroups:
        show_subgroup_selection(message)
        return

    current_week = get_current_week()
    user_week = get_user_week(user_id)
    user_subgroup = get_user_subgroup(user_id)
    today = datetime.now()
    week_num = (today - START_DATE).days // 7 + 1 if today >= START_DATE else 0

    week_info = f"""
🌸✨ *Информация о неделе* ✨🌸

*🌸 Текущая неделя:* {current_week}
*💫 Ваша неделя:* {user_week}
*👥 Ваша подгруппа:* {user_subgroup}
*📚 Учебная неделя №:* {week_num}
*📅 Дата:* {today.strftime('%d.%m.%Y')}

*🎀 Начало семестра:* 09.02.2026
*✨ Прошло дней:* {(today - START_DATE).days if today >= START_DATE else 0}

*💖 Режим:* {"Ручной 👑" if user_id in user_selected_weeks and user_selected_weeks[user_id] != "auto" else "Автоматический 🤖"}
"""
    bot.send_message(message.chat.id, week_info, parse_mode='Markdown')


def show_week_selection_menu(message):
    """Показывает меню выбора недели"""
    user_id = message.chat.id
    if user_id not in user_selected_subgroups:
        show_subgroup_selection(message)
        return

    current_week = get_current_week()

    markup_inline = types.InlineKeyboardMarkup(row_width=2)

    btn_week_i = types.InlineKeyboardButton(
        '🌸 I неделя',
        callback_data='set_week_I'
    )
    btn_week_ii = types.InlineKeyboardButton(
        '🌷 II неделя',
        callback_data='set_week_II'
    )
    btn_auto = types.InlineKeyboardButton(
        '✨ Автоматически',
        callback_data='set_week_auto'
    )
    btn_current_week = types.InlineKeyboardButton(
        f'💖 Текущая ({current_week})',
        callback_data='set_week_current'
    )
    btn_cancel = types.InlineKeyboardButton(
        '💔 Отмена',
        callback_data='cancel_week_switch'
    )

    markup_inline.row(btn_week_i, btn_week_ii)
    markup_inline.row(btn_auto, btn_current_week)
    markup_inline.row(btn_cancel)

    # Определяем текущий статус
    current_mode = "Автоматический ✨" if user_id not in user_selected_weeks or user_selected_weeks[
        user_id] == "auto" else "Ручной 👑"
    current_week_display = get_user_week(user_id)

    bot.send_message(
        message.chat.id,
        f"🌸✨ *Смена недели* ✨🌸\n\n"
        f"*💫 Текущий режим:* {current_mode}\n"
        f"*🌸 Показывается неделя:* {current_week_display}\n"
        f"*📅 Текущая неделя:* {current_week}\n\n"
        f"🎀 *Выберите действие:*",
        reply_markup=markup_inline,
        parse_mode='Markdown'
    )


def show_day_with_week_buttons(message, day_name, prefix=""):
    user_id = message.chat.id
    user_week = get_user_week(user_id)
    user_subgroup = get_user_subgroup(user_id)

    # Проверяем наличие расписания для данной подгруппы, дня и недели
    if (user_subgroup in schedule and
            day_name in schedule[user_subgroup] and
            user_week in schedule[user_subgroup][day_name]):

        response = f"{prefix}\n\n"
        response += schedule[user_subgroup][day_name][user_week]

        # Отправляем расписание
        bot.send_message(message.chat.id, response, parse_mode='Markdown')

        # Создаем inline-кнопки
        markup_inline = types.InlineKeyboardMarkup(row_width=2)

        # Определяем какую неделю показывать для переключения
        other_week = "II" if user_week == "I" else "I"
        current_week = get_current_week()

        btn_other_week = types.InlineKeyboardButton(
            f'🔄 Показать {other_week} неделю',
            callback_data=f'week_{other_week}_{day_name}'
        )
        btn_switch_global = types.InlineKeyboardButton(
            f'✨ Сменить на {other_week}',
            callback_data=f'switch_global_{other_week}'
        )
        btn_today = types.InlineKeyboardButton(
            '📅 Сегодня',
            callback_data='show_today'
        )
        btn_auto = types.InlineKeyboardButton(
            '🤖 Авто',
            callback_data='switch_auto'
        )
        btn_menu = types.InlineKeyboardButton(
            '🏠 Меню',
            callback_data='back_to_menu'
        )

        markup_inline.row(btn_other_week)
        markup_inline.row(btn_switch_global)
        markup_inline.row(btn_today, btn_auto, btn_menu)

        mode_text = "Ручной режим 👑" if user_id in user_selected_weeks and user_selected_weeks[
            user_id] != "auto" else "Автоматический режим 🤖"

        bot.send_message(
            message.chat.id,
            f"*🌸 Сейчас отображается {user_week} неделя*\n"
            f"*👥 Подгруппа:* {user_subgroup}\n"
            f"*✨ Режим:* {mode_text}\n"
            f"*📅 Текущая неделя:* {current_week}",
            reply_markup=markup_inline,
            parse_mode='Markdown'
        )
    else:
        bot.send_message(message.chat.id,
                         f"🌸 Расписание на {day_name} для подгруппы {user_subgroup} не найдено")


# Остальной код остается БЕЗ ИЗМЕНЕНИЙ (все callback-обработчики, команды /today, /tomorrow и т.д.)

@bot.message_handler(commands=['today'])
def today_command(message):
    user_id = message.chat.id
    if user_id not in user_selected_subgroups:
        show_subgroup_selection(message)
        return
    show_day_schedule(message, "today")


@bot.message_handler(commands=['tomorrow'])
def tomorrow_command(message):
    user_id = message.chat.id
    if user_id not in user_selected_subgroups:
        show_subgroup_selection(message)
        return
    show_day_schedule(message, "tomorrow")


@bot.message_handler(commands=['week'])
def week_command_handler(message):
    week_command(message)


@bot.message_handler(commands=['switch_week'])
def switch_week_command(message):
    """Команда для смены недели"""
    user_id = message.chat.id
    if user_id not in user_selected_subgroups:
        show_subgroup_selection(message)
        return
    show_week_selection_menu(message)


@bot.message_handler(commands=['auto_week'])
def auto_week_command(message):
    """Вернуться к автоматическому определению недели"""
    user_id = message.chat.id
    if user_id not in user_selected_subgroups:
        show_subgroup_selection(message)
        return

    user_selected_weeks[user_id] = "auto"
    save_data()

    bot.send_message(
        message.chat.id,
        "🌸✅ *Режим переключен на автоматический!* ✅🌸\n\n"
        f"Теперь бот будет показывать расписание *{get_current_week()} недели* "
        "(текущей недели). ✨",
        parse_mode='Markdown'
    )


@bot.message_handler(commands=['change_subgroup'])
def change_subgroup_command(message):
    """Сменить подгруппу"""
    show_subgroup_selection(message)


@bot.callback_query_handler(func=lambda callback: True)
def callback_handler(callback):
    user_id = callback.message.chat.id

    # Обработка выбора подгруппы
    if callback.data == 'select_subgroup_1':
        user_selected_subgroups[user_id] = 1
        save_data()

        bot.edit_message_text(
            "🌸✅ *Выбрана Подгруппа 1!* ✅🌸\n\n"
            "Теперь бот будет показывать расписание для первой подгруппы. ✨\n"
            "Для смены подгруппы используйте кнопку '👥 Сменить подгруппу' в главном меню. 🎀",
            callback.message.chat.id,
            callback.message.message_id,
            parse_mode='Markdown'
        )

        # Запускаем обычный старт
        time.sleep(1)
        msg = bot.send_message(user_id, "🌸 Загрузка меню...")
        start(msg)

    elif callback.data == 'select_subgroup_2':
        user_selected_subgroups[user_id] = 2
        save_data()

        bot.edit_message_text(
            "🌷✅ *Выбрана Подгруппа 2!* ✅🌷\n\n"
            "Теперь бот будет показывать расписание для второй подгруппы. ✨\n"
            "Для смены подгруппы используйте кнопку '👥 Сменить подгруппу' в главном меню. 🎀",
            callback.message.chat.id,
            callback.message.message_id,
            parse_mode='Markdown'
        )

        # Запускаем обычный старт
        time.sleep(1)
        msg = bot.send_message(user_id, "🌷 Загрузка меню...")
        start(msg)

    elif callback.data.startswith('week_I_'):
        # Показать I неделю для конкретного дня
        day_name = callback.data.split('_')[2]
        user_subgroup = get_user_subgroup(user_id)

        if (user_subgroup in schedule and
                day_name in schedule[user_subgroup] and
                "I" in schedule[user_subgroup][day_name]):
            try:
                bot.edit_message_text(
                    schedule[user_subgroup][day_name]["I"],
                    callback.message.chat.id,
                    callback.message.message_id - 1
                )
                # Обновляем кнопки
                markup_inline = types.InlineKeyboardMarkup(row_width=2)
                btn_other_week = types.InlineKeyboardButton(
                    '🌷 II неделя',
                    callback_data=f'week_II_{day_name}'
                )
                btn_switch_global = types.InlineKeyboardButton(
                    '✨ Сменить на II',
                    callback_data='switch_global_II'
                )
                btn_today = types.InlineKeyboardButton(
                    '📅 Сегодня',
                    callback_data='show_today'
                )
                btn_auto = types.InlineKeyboardButton(
                    '🤖 Авто',
                    callback_data='switch_auto'
                )
                btn_menu = types.InlineKeyboardButton(
                    '🏠 Меню',
                    callback_data='back_to_menu'
                )
                markup_inline.row(btn_other_week)
                markup_inline.row(btn_switch_global)
                markup_inline.row(btn_today, btn_auto, btn_menu)

                bot.edit_message_reply_markup(
                    callback.message.chat.id,
                    callback.message.message_id,
                    reply_markup=markup_inline
                )
                bot.answer_callback_query(callback.id, "🌸 Показана I неделя")
            except Exception as e:
                print(f"💔 Ошибка: {e}")
                bot.answer_callback_query(callback.id, "💔 Ошибка обновления")

    elif callback.data.startswith('week_II_'):
        # Показать II неделю для конкретного дня
        day_name = callback.data.split('_')[2]
        user_subgroup = get_user_subgroup(user_id)

        if (user_subgroup in schedule and
                day_name in schedule[user_subgroup] and
                "II" in schedule[user_subgroup][day_name]):
            try:
                bot.edit_message_text(
                    schedule[user_subgroup][day_name]["II"],
                    callback.message.chat.id,
                    callback.message.message_id - 1
                )
                # Обновляем кнопки
                markup_inline = types.InlineKeyboardMarkup(row_width=2)
                btn_other_week = types.InlineKeyboardButton(
                    '🌸 I неделя',
                    callback_data=f'week_I_{day_name}'
                )
                btn_switch_global = types.InlineKeyboardButton(
                    '✨ Сменить на I',
                    callback_data='switch_global_I'
                )
                btn_today = types.InlineKeyboardButton(
                    '📅 Сегодня',
                    callback_data='show_today'
                )
                btn_auto = types.InlineKeyboardButton(
                    '🤖 Авто',
                    callback_data='switch_auto'
                )
                btn_menu = types.InlineKeyboardButton(
                    '🏠 Меню',
                    callback_data='back_to_menu'
                )
                markup_inline.row(btn_other_week)
                markup_inline.row(btn_switch_global)
                markup_inline.row(btn_today, btn_auto, btn_menu)

                bot.edit_message_reply_markup(
                    callback.message.chat.id,
                    callback.message.message_id,
                    reply_markup=markup_inline
                )
                bot.answer_callback_query(callback.id, "🌷 Показана II неделя")
            except Exception as e:
                print(f"💔 Ошибка: {e}")
                bot.answer_callback_query(callback.id, "💔 Ошибка обновления")

    elif callback.data.startswith('switch_global_'):
        # Глобальное переключение недели
        week_to_set = callback.data.split('_')[2]
        user_selected_weeks[user_id] = week_to_set
        save_data()

        # Удаляем сообщение с кнопками
        try:
            bot.delete_message(callback.message.chat.id, callback.message.message_id)
        except:
            pass

        bot.send_message(
            user_id,
            f"🌸✅ *Расписание переключено на {week_to_set} неделю!* ✅🌸\n\n"
            f"Теперь все дни будут показываться для *{week_to_set} недели*. ✨\n"
            f"Для возврата к автоматическому режиму используйте команду /auto_week 🎀",
            parse_mode='Markdown'
        )
        bot.answer_callback_query(callback.id, f"🌸 Установлена {week_to_set} неделя")

    elif callback.data == 'switch_auto':
        # Включить автоматический режим
        user_selected_weeks[user_id] = "auto"
        save_data()

        current_week = get_current_week()
        bot.answer_callback_query(
            callback.id,
            f"✨ Включен автоматический режим. Текущая неделя: {current_week}"
        )

        # Обновляем сообщение
        try:
            bot.delete_message(callback.message.chat.id, callback.message.message_id)
        except:
            pass

        bot.send_message(
            user_id,
            f"🌸✅ *Включен автоматический режим!* ✅🌸\n\n"
            f"Теперь бот показывает расписание *{current_week} недели* (текущей). ✨",
            parse_mode='Markdown'
        )

    elif callback.data == 'set_week_I':
        # Установить I неделю
        user_selected_weeks[user_id] = "I"
        save_data()

        bot.edit_message_text(
            "🌸✅ *Расписание переключено на I неделю!* ✅🌸\n\n"
            "Теперь все дни будут показываться для *I недели*. ✨\n"
            "Для возврата к автоматическому режиму используйте кнопку ниже или команду /auto_week 🎀",
            callback.message.chat.id,
            callback.message.message_id,
            parse_mode='Markdown'
        )

        markup_inline = types.InlineKeyboardMarkup()
        btn_auto = types.InlineKeyboardButton(
            '✨ Вернуться к авторежиму',
            callback_data='set_week_auto'
        )
        markup_inline.row(btn_auto)

        bot.edit_message_reply_markup(
            callback.message.chat.id,
            callback.message.message_id,
            reply_markup=markup_inline
        )
        bot.answer_callback_query(callback.id, "🌸 Установлена I неделя")

    elif callback.data == 'set_week_II':
        # Установить II неделю
        user_selected_weeks[user_id] = "II"
        save_data()

        bot.edit_message_text(
            "🌷✅ *Расписание переключено на II неделю!* ✅🌷\n\n"
            "Теперь все дни будут показываться для *II недели*. ✨\n"
            "Для возврата к автоматическому режиму используйте кнопку ниже или команду /auto_week 🎀",
            callback.message.chat.id,
            callback.message.message_id,
            parse_mode='Markdown'
        )

        markup_inline = types.InlineKeyboardMarkup()
        btn_auto = types.InlineKeyboardButton(
            '✨ Вернуться к авторежиму',
            callback_data='set_week_auto'
        )
        markup_inline.row(btn_auto)

        bot.edit_message_reply_markup(
            callback.message.chat.id,
            callback.message.message_id,
            reply_markup=markup_inline
        )
        bot.answer_callback_query(callback.id, "🌷 Установлена II неделя")

    elif callback.data == 'set_week_auto':
        # Включить автоматический режим
        user_selected_weeks[user_id] = "auto"
        save_data()
        current_week = get_current_week()

        bot.edit_message_text(
            f"✨✅ *Включен автоматический режим!* ✅✨\n\n"
            f"Теперь бот показывает расписание *{current_week} недели* (текущей). 🌸",
            callback.message.chat.id,
            callback.message.message_id,
            parse_mode='Markdown'
        )

        markup_inline = types.InlineKeyboardMarkup()
        btn_menu = types.InlineKeyboardButton(
            '🏠 В главное меню',
            callback_data='back_to_menu'
        )
        markup_inline.row(btn_menu)

        bot.edit_message_reply_markup(
            callback.message.chat.id,
            callback.message.message_id,
            reply_markup=markup_inline
        )
        bot.answer_callback_query(callback.id, f"✨ Включен авторежим. Текущая неделя: {current_week}")

    elif callback.data == 'set_week_current':
        # Установить текущую неделю
        current_week = get_current_week()
        user_selected_weeks[user_id] = current_week
        save_data()

        bot.edit_message_text(
            f"💖✅ *Установлена текущая неделя ({current_week})!* ✅💖\n\n"
            f"Теперь бот показывает расписание *{current_week} недели*. ✨",
            callback.message.chat.id,
            callback.message.message_id,
            parse_mode='Markdown'
        )

        markup_inline = types.InlineKeyboardMarkup()
        btn_auto = types.InlineKeyboardButton(
            '✨ Включить авторежим',
            callback_data='set_week_auto'
        )
        markup_inline.row(btn_auto)

        bot.edit_message_reply_markup(
            callback.message.chat.id,
            callback.message.message_id,
            reply_markup=markup_inline
        )
        bot.answer_callback_query(callback.id, f"💖 Установлена {current_week} неделя")

    elif callback.data == 'cancel_week_switch':
        # Отмена смены недели
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        bot.answer_callback_query(callback.id, "💔 Отменено")

    elif callback.data == 'back_to_menu':
        try:
            bot.delete_message(callback.message.chat.id, callback.message.message_id)
        except:
            pass
        # Отправляем обновленное меню
        msg = bot.send_message(callback.message.chat.id, "🌸 Обновление меню...")
        start(msg)

    elif callback.data == 'show_today':
        try:
            bot.delete_message(callback.message.chat.id, callback.message.message_id)
        except:
            pass
        today_command(callback.message)


# ================ ЗАПУСК ================

def run_flask_server():
    try:
        port = int(os.environ.get('PORT', 10000))
        print(f"🌸 Flask сервер запускается на порту: {port}")
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False, threaded=True)
    except Exception as e:
        print(f"💔 Ошибка Flask: {e}")
        return


def keep_alive():
    """
    Периодически пингует бота, чтобы он не засыпал на Render Free
    """
    time.sleep(40)

    # Ваш URL с Render (ЗАМЕНИТЕ на ваш настоящий URL!)
    YOUR_RENDER_URL = "https://telegram-schedule-bot6pi.onrender.com"  # <-- ЗАМЕНИТЕ ЭТО!

    while True:
        try:
            response = requests.get(f"{YOUR_RENDER_URL}/ping", timeout=10)
            print(f"🌸 Keep-alive ping отправлен: {response.status_code}")
        except Exception as e:
            print(f"💫 Keep-alive не удался: {e}")

        time.sleep(480)


def run_telegram_bot():
    print("🌸✨ Telegram бот запущен! ✨🌸")
    print(f"📅 Семестр начинается: {START_DATE.strftime('%d.%m.%Y')}")
    print(f"🌸 Текущая неделя: {get_current_week()}")
    bot.polling(none_stop=True, interval=1, timeout=60)


if __name__ == "__main__":
    print("🌸✨ ===== НАЧАЛО ЗАПУСКА СИСТЕМЫ ===== ✨🌸")

    # Загружаем данные
    load_data()

    # 1. Запускаем keep-alive в отдельном потоке
    print("1. Запуск системы keep-alive... 🌸")
    keep_alive_thread = threading.Thread(target=keep_alive)
    keep_alive_thread.daemon = True
    keep_alive_thread.start()

    # 2. Запускаем Flask сервер
    print("2. Запуск Flask сервера... 🌸")
    flask_thread = threading.Thread(target=run_flask_server)
    flask_thread.daemon = True
    flask_thread.start()

    # 3. Ждем запуска Flask
    print("3. Ожидание запуска компонентов (5 секунд)... 💫")
    time.sleep(5)

    # 4. Запускаем Telegram бота
    print("4. Запуск Telegram бота... 🌸")
    run_telegram_bot()


    print("🏁 Все системы успешно запущены! ✨🌸")

