import telebot
from telebot import types
import requests
import datetime
import time
import threading

token = '5633289666:AAE3_bdGVPmfgHDKo6UIjcum6YeAxmj3VHs'
bot = telebot.TeleBot(token)
open_weather_token = '298e9ddda1933c1cb485acf0a9b2b0c3'

times = []
flag = ''
my_city = ''
last_id = 0
last_city = ''
smiles = {
    'Clear': '☀Ясно ️',
    'Clouds': '☁Облачно ️',
    'Rain': '🌧Дождь ',
    'Drizzle': '🌦Морось ',
    'Thunderstorm': '⛈Гроза ',
    'Snow': '⛈Снег ',
    'Mist': '🌫Туман '
}

@bot.message_handler(commands=['start','help'])
def help(message):
    message.text = 'Помощь ❔'
    get_user_text(message)

@bot.message_handler(commands=['now'])
def now(message):
    message.text = 'Погода'
    get_user_text(message)

@bot.message_handler(commands=['choose'])
def choose(message):
    message.text = 'Выбрать'
    get_user_text(message)

@bot.message_handler(commands=['settings'])
def settings(message):
    message.text = 'Параметры рассылки ⚙️'
    get_user_text(message)

@bot.message_handler(commands=['clean'])
def clean(message):
    message.text = 'Очистить избранный город 🗑'
    get_user_text(message)

@bot.message_handler(content_types=['text'])
def get_user_text(message):
    global flag
    global my_city
    if(flag=='choosing_city'):
        try:
            if(my_city == message.text and my_city != ''):
                bot.send_message(message.chat.id, 'У вас уже выбран этот город!', 'html')
            else:
                request = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={open_weather_token}&units=metric')
                data = request.json()
                city = data['name']
                my_city = message.text
                flag = ''
                set_start_markup(message,'Вы успешно выбрали город ' + message.text + '!')
        except:
            bot.send_message(message.chat.id, 'Пожалуйста, проверьте название города 💀')
    elif (flag == 'choosing_time'):
        if (len(message.text) == 5 and message.text[0].isdigit() and ord(message.text[0]) <= 50
                and message.text[1].isdigit() and message.text[3].isdigit() and ord(message.text[3]) <= 53
                and message.text[4].isdigit() and message.text[2] == ':' and not(ord(message.text[0]) == 50 and ord(message.text[1]) >= 52)):
            if(message.text in times):
                bot.send_message(message.chat.id, 'Такое время уже установлено!')
            else:
                times.append(message.text)
                flag = ''
                set_start_markup(message, 'Новое время рассылки установлено на ' + message.text + '!')
        else:
            bot.send_message(message.chat.id, 'Введено некорректное время!')
    else:
        if (message.text.split()[0] == 'Погода'):
            if(my_city==''):
                bot.send_message(message.chat.id, 'Вы ещё не установили избранный город!')
            else:
                get_weather(message.chat.id, my_city)
        elif (message.text.split()[0] == 'Выбрать'):
            markup = types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id, 'Введите название города:', 'html', None, None, None, None, None, None, markup)
            flag = 'choosing_city'
        elif (message.text == 'Параметры рассылки ⚙️'):
            if(len(times)==0):
                markup = types.InlineKeyboardMarkup()
                button_add = types.InlineKeyboardButton('Добавить новое время', callback_data='add')
                markup.add(button_add)
                bot.send_message(message.chat.id, 'Вы ещё не установили параметры рассылки!', 'html', None, None, None, None, None, None, markup)
            else:
                markup = types.InlineKeyboardMarkup()
                button_add = types.InlineKeyboardButton('Добавить новое время', callback_data='add')
                markup.add(button_add)
                for el in times:
                    button_el = types.InlineKeyboardButton(el, callback_data=el)
                    markup.add(button_el)
                button_clean = types.InlineKeyboardButton('Удалить всё', callback_data='clean')
                markup.add(button_clean)
                bot.send_message(message.chat.id, 'Ежедневно сообщается погода в городе ' + my_city + ' в следующее время:\n', 'html', None, None, None, None, None, None, markup)
        elif (message.text == 'Очистить избранный город 🗑'):
            if(my_city == ''):
                mes_str = 'Избранный город ещё не установлен!'
            else:
                mes_str = 'Город ' + my_city + ' больше не является избранным городом.'
            my_city = ''
            set_start_markup(message, mes_str)
        elif (message.text == 'Помощь ❔'):
            set_start_markup(message,
                f"<b>Вас приветсвтует бот прогноза погоды!</b>\n\n"
                f"Напишите ему любой город на любой раскладке и получите подробное описание погоды в данный момент времени в этом городе!\n" 
                f"Также есть возможность выбрать один город для рассылки данных о погоде в любое удобное для Вас время!\n\n" 
                f"<b>Бот поддерживает следующие команды:</b>\n/help - помощь\n/now - погода в избранном городе на данный момент\n"         
                f"/choose - выбрать новый город\n/clean - очистить избранный город\n"
                f"/settings - параметры рассылки")
        elif (len(message.text) >= 20 and message.text.split()[0] == 'Удалить'):
            r = message.text.split()[3]
            if(r in times):
                times.remove(message.text.split()[3])
                set_start_markup(message, 'Рассылка в ' + r + ' успешно удалёна!')
            else:
                set_start_markup(message, 'Рассылка в ' + r + ' уже удалёна!')
        elif(message.text == 'Отмена'):
            set_start_markup(message, 'Действие отменено.')
        else:
            try:
                get_weather(message.chat.id, message.text)
            except:
                bot.send_message(message.chat.id, 'Пожалуйста, проверьте название города 💀')
    global last_id
    last_id = message.chat.id


@bot.callback_query_handler(func=lambda c: True)
def callback(call):
    global flag
    if call.message:
        if(call.data == 'add'):
            markup = types.ReplyKeyboardRemove()
            bot.send_message(call.message.chat.id, 'Введите новое время в формате ЧЧ:ММ', 'html', None, None, None, None, None, None, markup)
            flag = 'choosing_time'
        elif (call.data == 'clean'):
            bot.send_message(call.message.chat.id, 'Вся рассылка удалена!')
            times.clear()
            flag = ''
        else:
            markup = types.ReplyKeyboardMarkup(True)
            button_delete = types.KeyboardButton('Удалить рассылку в ' + call.data)
            button_cancel = types.KeyboardButton('Отмена')
            markup.add(button_delete, button_cancel)
            bot.send_message(call.message.chat.id, 'Выберите команду:', 'html', None, None, None, None, None, None, markup)

def get_weather(id, text, add_text = ''):
    request = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={text}&appid={open_weather_token}&units=metric')
    data = request.json()
    city = data['name']
    temperature = data['main']['temp']
    description = data['weather'][0]['main']
    if description in smiles:
        weather = smiles[description]
    else:
        weather = 'Невозможно распознать погодное явление!'
    humidity = data['main']['humidity']
    pressure = data['main']['pressure']
    wind = data['wind']['speed']
    sunrise = datetime.datetime.fromtimestamp(data['sys']['sunrise'])
    sunset = datetime.datetime.fromtimestamp(data['sys']['sunset'])
    day_length = datetime.datetime.fromtimestamp(data['sys']['sunset']) - datetime.datetime.fromtimestamp(data['sys']['sunrise'])
    global last_city
    last_city = text
    bot.send_message(id, add_text +
                     f"Погода в городе {text} на данный момент ({datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}):\n"
                     f"🌡Температура: {temperature}C°\n{weather}\n"
                     f"💧Влажность: {humidity}%\n🔗Давление: {pressure} мм.рт.ст\n💨Ветер: {wind} м/с\n"
                     f"🌇Восход: {sunrise.strftime('%H:%M:%S')}\n🌃Закат: {sunset.strftime('%H:%M:%S')}\n⏳Продолжительность дня: {day_length}\n", 'html')

def set_start_markup(message, mes_str):
    markup = types.ReplyKeyboardMarkup(True)
    str = ''
    global my_city
    if (my_city == ''):
        str = 'Выбрать город ❗'
    else:
        str = 'Выбрать другой город 🔄'
        button_now = types.KeyboardButton('Погода в городе ' + my_city + ' прямо сейчас ⏰')
        markup.add(button_now)
    button_choose = types.KeyboardButton(str)
    markup.add(button_choose)
    button_delete = types.KeyboardButton('Очистить избранный город 🗑')
    markup.add(button_delete)
    button_settings = types.KeyboardButton('Параметры рассылки ⚙️')
    markup.add(button_settings)
    button_help = types.KeyboardButton('Помощь ❔')
    markup.add(button_help)
    bot.send_message(message.chat.id, mes_str, 'html', None, None, None, None, None, None, markup)

def sending():
    global my_city
    while True:
        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        time.sleep(1)
        for el in times:
            if current_time == el + ':00' and my_city != "":
                get_weather(last_id, my_city, '🔥<b>Ежедневная рассылка!</b>🔥\n')

my_thread = threading.Thread(target=sending)
my_thread.start()

bot.polling(none_stop=True)