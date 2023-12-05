
from telegram.ext import (Updater, CommandHandler, ConversationHandler,
                          MessageHandler,Filters, CallbackContext)
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update

from memory_datasource import MemoryDataSource
import os
import threading
import time


ADD_REMINDER_TEXT = 'Add a reminder ❤️'
INTERVAL = 30


TOKEN = os.getenv("TOKEN")
ENTER_MESSAGE, ENTER_TIME = range(2)
dataSource = MemoryDataSource()


def start_handler(update, context):
    update.message.reply_text("hello creator!", reply_markup=add_reminder_button())

def add_reminder_button():
    keyboard = [[KeyboardButton(ADD_REMINDER_TEXT)]]
    return ReplyKeyboardMarkup(keyboard)

def add_reminder_handler(update: Update, context: CallbackContext):
    update.message.reply_text("Please enter a message of reminder:")
    return ENTER_MESSAGE

def enter_messgae_handler(update: Update, context: CallbackContext):
    update.message.reply_text("Please enter a time when bot should remind:")
    context.user_data["message_text"] = update.message.text
    return ENTER_TIME

def enter_time_handler(update: Update, context: CallbackContext):
    message_text = context.user_data["message_text"]
    time = update.message.text
    message_data = dataSource.add_reminder(update.message.chat_id, message_text, time)
    update.message.reply_text("Your reminder: "+message_data.__repr__())
    return ConversationHandler.END

def start_check_reminders_task():
    thread = threading.Thread(target=check_reminders, args=())
    thread.daemon = True
    thread.start()


def check_reminders():
    while True:
        for chat_id in dataSource.reminders:
            if dataSource.reminders[chat_id].should_be_fired():
                dataSource.reminders[chat_id].fire()
                updater.bot.send_message(chat_id, dataSource.reminders[chat_id].message)

        time.sleep(INTERVAL)

if __name__ == '__main__':
    updater = Updater(TOKEN, use_context=True, request_kwargs={'proxy_url': 'socks5h://127.0.0.1:7890/'})
    updater.dispatcher.add_handler(CommandHandler("start",  start_handler))
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(ADD_REMINDER_TEXT), add_reminder_handler)],
        states={
            ENTER_MESSAGE: [MessageHandler(Filters.all, enter_messgae_handler)],
            ENTER_TIME: [MessageHandler(Filters.all, enter_time_handler)]
        },
        fallbacks=[]
    )

    updater.dispatcher.add_handler(conv_handler)
    updater.start_polling()
    start_check_reminders_task()

