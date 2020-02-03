from flask import Flask, request
import telebot
from telebot import types
import time
import datetime
import gspread
import sqlite3
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from google_sheets import create_sheet_if_not_exist, add_transaction
from db import init_database

secret = "12091995"
bot = telebot.TeleBot('986714852:AAHEIG1WGgXcHk4o3WTZ0fCQ8So7Ps_b82Q', threaded=False)

bot.remove_webhook()
time.sleep(1)
bot.set_webhook(url="https://ekaterinaklus.pythonanywhere.com/{}".format(secret))

app = Flask(__name__)

init_database()
connection = sqlite3.connect("categories.db")
cursor = connection.cursor()

# Credentials for google drive
credentials = ServiceAccountCredentials.from_json_keyfile_name("CashFlow-7de2d73b7fb7.json",
                                                               ['https://www.googleapis.com/auth/spreadsheets',
                                                                'https://www.googleapis.com/auth/drive'])


get_prnt_ctg_by_name = "SELECT name FROM categories WHERE ctg_id=(select parent_ctg_id from categories where name=?)"
get_sub_categories = "select name from categories where parent_ctg_id is not null"
get_categories = "select name, ctg_id from categories where parent_ctg_id is null"


@app.route('/{}'.format(secret), methods=["POST"])
def web_hook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    print("Message")
    return "ok", 200


@bot.message_handler(commands=['start', 'help'])
def start_command(message):
    bot.send_message(message.chat.id, 'Формат сообщений: +/- название сумма', reply_markup=types.ReplyKeyboardRemove())


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # Если сообщение из чата с ботом
    if call.message:
        if call.data.startswith("get_categories"):
            bot.send_message(call.message.chat.id, "answer")
    # Если сообщение из инлайн-режима
    elif call.inline_message_id:
        if call.data.startswith("get_categories"):
            bot.send_message(call.message.chat.id, "answer")


@bot.message_handler(content_types=['text'])
def send_text(message):
    sheets_service = apiclient.discovery.build('sheets', 'v4', credentials=credentials)
    client = gspread.authorize(credentials)
    sh = client.open("Cash-flow")

    wsheet = create_sheet_if_not_exist(sh, sheets_service)
    content = message.text.split(' ')

    if message.text.startswith('Категории'):
        cursor.execute(get_categories)
        rslt = cursor.fetchall()
        for item in rslt:
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text=item[0], callback_data="get_categories "+str(item[1]))
            keyboard.add(callback_button)

    elif len(content) == 3:
        try:
            amount = float(content[2])
        except ValueError:
            bot.send_message(message.chat.id, "Неверный формат сообщения")
            return

        if message.text.startswith('-'):
            now = datetime.datetime.now()
            my_category = "Прочее"

            cursor.execute(get_prnt_ctg_by_name, [(content[1])])
            rslt = cursor.fetchall()
            if rslt:
                my_category = rslt[0][0]

            now_date = now.strftime("%Y-%m-%d")
            t_sum = 0 - float(content[2])
            description = str(content[1])
            answer = 'Расход от ' + now_date + "\n" + "Категория: " + str(my_category) + "\n" + description + " " + str(t_sum) + "р."

            add_transaction(content[0], now_date, t_sum, description, str(my_category), wsheet)
            bot.send_message(message.chat.id, answer)

        elif message.text.startswith('+'):
            now = datetime.datetime.now()
            my_category = "Прочее"

            cursor.execute(get_prnt_ctg_by_name, [(content[1])])
            rslt = cursor.fetchall()
            if rslt:
                my_category = rslt[0][0]

            now_date = now.strftime("%Y-%m-%d")
            t_sum = float(content[2])
            description = str(content[1])
            answer = 'Доход от ' + now_date + "\n" + "Категория: " + str(my_category) + "\n" + description + " " + str(t_sum) + "р."
            add_transaction(content[0], now_date, t_sum, description, str(my_category), wsheet)
            bot.send_message(message.chat.id, answer)

    else:
        bot.send_message(message.chat.id, "Неверный формат сообщения")
