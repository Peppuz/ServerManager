import test
import telegram
import logging
import os
import json
from functools import wraps
from telegram import (
    Emoji,
    ForceReply,
    InlineKeyboardButton,
    InlineKeyboardMarkup)
from telegram.ext import (
    Updater,
    MessageHandler,
    Filters,
    CommandHandler,
    CallbackQueryHandler)
from telegram import ReplyKeyboardMarkup as RKM

logging.basicConfig(format='%(asctime)s - %(message)s',
                    datefmt='%I:%M',
                    level=logging.DEBUG)

# loads from json all user custom data
config = json.load(open('config.json'))

bot = telegram.Bot(config['token'])
updater = Updater(config['token'])


def restricted(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in config['admins']:
            bot.sendMessage(update.message.chat_id, "Unauthorized access denied.")
            print("Unauthorized user, access denied.")
            return
        return func(bot, update, *args, **kwargs)
    return wrapped


def start(b, u):
    usr = u.message.from_user
    if usr.id in config['admins']:
        text = "Bella %s! \nPWD ~ %s" % (usr.first_name, pwd)
        bot.send_message(u.message.chat_id, text)
        # TODO: insert here Callback buttons if id in admin_list 
        return 
    bot.send_message(u.message.chat_id,'Ciao ' + usr.first_name+'!')
    for val in config['admins']:
        bot.sendMessage(val, "User: %s \n started ServerManager"
                        % u.message.from_user.username)


@restricted
def commands(b, u):
    """ This function handles all type of text messages incoming """ 
    m = u.message
    usr = m.from_user
    bot.send_message(m.chat_id, "executing.."
    # TODO: make the CLI do shiet 


@restricted
def ricevi_file(b, u):
    """ This function waits for a document and stores in config[pwd]"""
    d = u.message.document
    pfile = bot.getFile(d.file_id)
    pfile.download(custom_path=pwd)
    bot.sendMessage(u.message.chat_id, "File salvato")


@restricted
def send_doc(b, u, args):
    """ This function sends the file requested from command /get """ 
    m = u.message
    with open(args[0]) as figa:
        bot.sendDocument(m.chat_id, figa, caption='Is this the file requested?')


if __name__ == '__main__':
    ds = updater.dispatcher

    """ Commands Interface
         * start | menu - bot menu 
         * get - expects file_name as arg 
         * 
    """ 
    ds.add_handler(CommandHandler('start', start))
    ds.add_handler(CommandHandler('menu', start))
    ds.add_handler(CommandHandler('get', send_doc, pass_args=True))

    # Message to CLI - gets output to less and sends text
    ds.add_handler(MessageHandler(Filters.text, commands))
        
    # Incoming files [excluding supported audio or videos] are uploaded into the current pwd
    ds.add_handler(MessageHandler(Filters.document, ricevi_file))

    # Callbacks
    ds.add_handler(CallbackQueryHandler(deletedata))

    # Start Bot
    updater.start_polling()
