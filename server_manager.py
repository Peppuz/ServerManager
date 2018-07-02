import telegram
import logging
import os
import json
import subprocess 
from functools import wraps
from telegram import (
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
        text = "~ Bella %s!~ " % usr.first_name
        bot.send_message(u.message.chat_id, text, reply_markup=switch('home'))


@restricted
def commands(b, u):
    """ This function handles all type of text messages incoming """ 
    m = u.message
    usr = m.from_user
    bot.send_message(m.chat_id, "executing..")
    # TODO: make the CLI do shiet 
    # os. 


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


@restricted
def callbacks(b, update):
    query = update.callback_query
    chat = query.message.chat.id
    msg_id = query.message.message_id
    text = str(query.data) + " Menu"

    if query.data == 'pumper':
        k = subprocess.Popen('pwd')
	bot.sendMessage(chat, str(k), reply_markup=switch('home'))
    elif query.data == 'website':
        pass
    elif query.data == 'ig_peppuz':
        pass 

    bot.edit_message_reply_markup(chat, msg_id, reply_markup=switch(query.data))


def switch(x):
    return {
      'processes': InlineKeyboardMarkup([
	[InlineKeyboardButton('Pumper',callback_data='pumper')],
	[InlineKeyboardButton('Menu', callback_data='home')]]),
      'home': InlineKeyboardMarkup([
        [InlineKeyboardButton('Processes', callback_data='processes')],
        [InlineKeyboardButton('Navigator', callback_data='navigator')]])
      #'':  
    }.get(x, None) 



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
    ds.add_handler(CallbackQueryHandler(callbacks))

    # Start Bot
    updater.start_polling()
