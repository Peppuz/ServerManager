import test
from functools import wraps
import telegram
import logging
import os
import json
from telegram.ext import (Updater,
    MessageHandler,
    Filters,
    CommandHandler,
    CallbackQueryHandler)
from telegram import (Emoji,
    ForceReply,
    InlineKeyboardButton,
    InlineKeyboardMarkup)
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
    bot.sendMessage(u.message.chat_id,
                    text='Ciao ' + u.message.from_user.first_name+'!')
    for val in config['admins']:
        bot.sendMessage(val, "User: %s \n started ServerManager"
                        % u.message.from_user.username)


@restricted
def commands(b, u):
    m = u.message
    usr = m.from_user
    if 'cd' in m.text:
        try:
            os.chdir(m.text[3:])
        except Exception as e:
            bot.sendMessage(m.chat_id, "There was a lil prob with the command.")
        pwd = os.popen('pwd').read()
        bot.sendMessage(
            m.chat_id,
            '<b>Folder</b>:\n%s\n%s' % (pwd, os.popen('ls').read()),
            parse_mode='HTML'
        )
        return
    try:
        bot.sendMessage(m.chat_id, "%s" % os.popen(m.text).read())
    except Exception as e:
        bot.sendMessage(m.chat_id, "Command not recognized")


@restricted
def ricevi_file(b, u):
    d = u.message.document
    pfile = bot.getFile(d.file_id)
    pfile.download(custom_path=pwd)
    bot.sendMessage(u.message.chat_id, "File salvato")


@restricted
def send_doc(b, u, args):
    # Simple usagx
    m = u.message
    print args
    with open(args[0]) as figa:
        loc = bot.sendDocument(m.chat_id, figa, caption='Pepuuz')
        online_data.append(loc.message_id)
    check_online_data(bot, m.chat_id)


if __name__ == '__main__':
    ds = updater.dispatcher
    # Commands
    ds.add_handler(CommandHandler('start', start))
    ds.add_handler(CommandHandler('get', send_doc, pass_args=True))
    # Messages
    ds.add_handler(MessageHandler(Filters.text, commands))
    ds.add_handler(MessageHandler(Filters.document, ricevi_file))
    # Callbacks
    ds.add_handler(CallbackQueryHandler(deletedata))
    # Start Bot
    updater.start_polling()
