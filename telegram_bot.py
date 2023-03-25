import requests
import re
import telebot
from bs4 import BeautifulSoup
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = "Ваш токен"
bot = telebot.TeleBot(TOKEN)

keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add("Выбрать SCP")
keyboard.add("SCP Foundation - это...")
chek = False


def get_info(number):
    if number == '001':
        return "Засекречено"
    if not (number in range(2, 1000)):
        return "Ошибка"
    number = str(number).rjust(3, '0')
    url = f'https://scpfoundation.net/scp-{number}'
    response = requests.get(url)
    if response.status_code != 200:
        return "Ошибка"
    soup = BeautifulSoup(response.text, "html.parser")

    obj_name = f'SCP-{number}'

    name = "Имя: " + (soup.find('div', id='main-content').find('div', id='page-title').text).strip()
    name = (re.sub('[ ]*SCP-[0-9]* - ', '', name)).strip()
    p = soup.find('div', id='main-content').find('div', id='page-content')
    p = p.find_all("p")
    class_obj = ''

    for i in p:
        if i.find("strong"):
            if i.find("strong").text == "Класс объекта:":
                class_obj = "Класс объекта: " + i.find("a").text
                break
    for i in p:
        if i.find("strong"):
            if i.find("strong").text == "Особые условия содержания:":
                conditions_of_detention = i.text
                continue

    index = None
    for i in p:
        if i.find("strong"):
            if i.find("strong").text == "Описание:":
                index = p.index(i)
            elif index is not None:
                max_index = p.index(i)
                if max_index > index + 4:
                    max_index = index + 3
    description = 'Описание: ' + ''.join(list(map(lambda x: x.text, p[index + 1:max_index])))
    return (obj_name, name, class_obj, conditions_of_detention, description)


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Этот бот выдаёт краткую инфомацию об SCP",
                     reply_markup=keyboard)


@bot.message_handler(regexp=r'SCP Foundation - это...')
def scp_this(message):
    msg = "Фонд SCP (англ. SCP Foundation; от англ. Secure, Contain, Protect — «Обезопасить, Удержать, Сохранить» или Special Containment Procedures — «Особые Условия Содержания») — вымышленная организация, являющаяся предметом одноимённого проекта совместного веб-творчества, в русском переводе также известная просто как Фонд или Организация."

    photo = 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/SCP_Foundation_%28emblem%29.svg/300px-SCP_Foundation_%28emblem%29.svg.png'

    bot.send_photo(message.chat.id, photo)
    bot.send_message(message.chat.id, msg)


@bot.message_handler(regexp=r'Выбрать SCP')
def scp_choose(message):
    global chek
    msg = 'Введите номер SCP(2-999)'
    chek = True
    bot.send_message(message.chat.id, msg)


@bot.message_handler(regexp=r'[1-9]+[0-9]*')
def scp_sendler(message):
    global chek
    if chek:
        msg = '\n\n'.join(y) if (y := get_info(int(message.text))) != "Ошибка" else "Ошибка"
        bot.send_message(message.chat.id, msg)
        chek = False


bot.infinity_polling()




