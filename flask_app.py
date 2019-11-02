from flask import Flask, request
import telebot
from telebot import types
import time
import datetime
import gspread
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from google_sheets import create_sheet_if_not_exist, add_transaction

secret = "12091995"
bot = telebot.TeleBot('986714852:AAHEIG1WGgXcHk4o3WTZ0fCQ8So7Ps_b82Q', threaded=False)

bot.remove_webhook()
time.sleep(1)
bot.set_webhook(url="https://ekaterinaklus.pythonanywhere.com/{}".format(secret))

app = Flask(__name__)

expense_categories = {"транспорт": ["метро", "такси", "автобус"],
              "еда": ["продукты", "перекус", "столовая"],
              "развлечения": ["кино", "кафе", "бар", "ресторан"]}

income_categories = {"зарплата": ["зп", "премия", "отпускные"], "переводы": ["перевод"] }

# Credentials for google drive
credentials = ServiceAccountCredentials.from_json_keyfile_name("CashFlow-7de2d73b7fb7.json",
                                                               ['https://www.googleapis.com/auth/spreadsheets',
                                                                'https://www.googleapis.com/auth/drive'])

sheets_service = apiclient.discovery.build('sheets', 'v4', credentials=credentials)
client = gspread.authorize(credentials)
sh = client.open("table")


@app.route('/{}'.format(secret), methods=["POST"])
def web_hook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    print("Message")
    return "ok", 200


@bot.message_handler(commands=['start', 'help'])
def start_command(message):
    bot.send_message(message.chat.id, 'Hi *' + message.chat.first_name + '*!' , parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(content_types=['text'])
def send_text(message):
    wsheet = create_sheet_if_not_exist(sh, sheets_service)
    content = message.text.split(' ')
    if len(content) == 3:
        try:
            amount = int(content[2])
        except ValueError:
            bot.send_message(message.chat.id, "Неверный формат сообщения")

        if message.text.startswith('-'):
            now = datetime.datetime.now()
            my_category = "Прочее"
            for category, items in expense_categories.items():
                for item in items:
                    if item == str(content[1]):
                        my_category = category

            now_date = now.strftime("%Y-%m-%d")
            t_sum = "-" + str(content[2])
            description = str(content[1])
            answer = 'Расход от ' + now_date + "\n" + "Категория: " + str(my_category) + "\n" + description + " " + t_sum + "р."

            add_transaction(content[0], now_date, t_sum, description, str(my_category), wsheet)
            bot.send_message(message.chat.id, answer)

        elif message.text.startswith('+'):
            now = datetime.datetime.now()
            my_category = "Прочее"
            for category, items in income_categories.items():
                for item in items:
                    if item == str(content[1]):
                        my_category = category

            now_date = now.strftime("%Y-%m-%d")
            t_sum = "+" + str(content[2])
            description = str(content[1])
            answer = 'Доход от ' + now_date + "\n" + "Категория: " + str(my_category) + "\n" + description + " " + t_sum + "р."
            add_transaction(content[0], now_date, t_sum, description, str(my_category), wsheet)
            bot.send_message(message.chat.id, answer)

    else:
        bot.send_message(message.chat.id, "Неверный формат сообщения")
