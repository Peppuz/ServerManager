import telegram, logging, os
from telegram.ext import (Updater, MessageHandler, Filters, CommandHandler, CallbackQueryHandler)
from telegram import (Emoji, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup)
from telegram import ReplyKeyboardMarkup as RKM
from functools import wraps
import test
# from mwt import MWT

bot = telegram.Bot('237607855:AAG5DnCltKar7R5lMk3zo22iR8q9v44Kco0')
updater = Updater('237607855:AAG5DnCltKar7R5lMk3zo22iR8q9v44Kco0')
logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%I:%M', level=logging.DEBUG)

auth = [135605474, 59114236]
pwd = ''
online_data = []


# @MWT(timeout=60*60) # Decorator time 1hour
def check_online_data(bot, chat_id):
    if not online_data:
        return False
    for item in online_data:
        bot.deleteMessage(chat_id, item)
    return True


def restricted(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in auth:
            bot.sendMessage(update.message.chat_id, "Unauthorized access denied.")
            print("Unauthorized access denied.")
            return
        return func(bot, update, *args, **kwargs)
    return wrapped


def start(b,u):
    m = u.message
    usr	= m.from_user
    # setting user status
    bot.sendMessage(m.chat_id, text='Ciao '+ usr.first_name+'!')


@restricted
def commands(b,u):
    m = u.message
    usr	= m.from_user
    if 'cd' in m.text:
        os.chdir(m.text[3:])
        pwd = os.popen('pwd').read()
        bot.sendMessage(m.chat_id, '<b>Folder</b>:\n%s\n%s' % (pwd, os.popen('ls').read()), parse_mode='HTML')
        return

    bot.sendMessage(m.chat_id, "%s" % os.popen(m.text).read())

@restricted
def ricevi_file(b,u):
    d = u.message.document
    pfile = bot.getFile(d.file_id)
    pfile.download(custom_path=pwd)
    bot.sendMessage(u.message.chat_id, "File salvato")


@restricted
def invia_file(b,u, args):
    m = u.message
    print args
    with open(args[0]) as figa:
        loc = bot.sendDocument(m.chat_id, figa, caption='Pepuuz')
        online_data.append(loc.message_id)
    check_online_data(bot,m.chat_id)


@restricted
def deletedata(b,u):
    query = u.callback_query
    chat_id = query.message.chat_id
    usr_id = query.from_user.id
    txt = query.data  # <= trip_id
    bot.deleteMessage(chat_id, txt)
    nextm = str(int(txt) + 1)
    bot.deleteMessage(chat_id, nextm)


def oraristp_data(bot,update):

    data = test.main_search()
    msg = " Richieste Totali: %s\n\n" \
          " Analisi Dispositivi:\n" \
          "  Richieste iOS: %s\n" \
          "  Richieste Android: %s\n\n" \
          " Analisi mensile:\n" \
          "  Richieste Maggio: %s\n" \
          "  Richieste Giugno: %s\n" \
          "  Richieste Luglio: %s\n" \
          % (data['total'], data['ios'], data['android'], data['maggio'], data['giugno'], data['luglio'])
    msg += " Top 3 Partenze: %s, %s, %s" % (data['Request-partenza'][0][0], data['Request-partenza'][1][0], data['Request-partenza'][2][0])
    msg += " Top 3 Destinazioni: %s, %s, %s" % (data['Request-destinazione'][0][0], data['Request-destinazione'][1][0], data['Request-destinazione'][2][0])
    msg += " Top 5 Tratte: %s | %s | %s | %s | %s" % (data['Tratte'][0][0], data['Tratte'][1][0], data['Tratte'][2][0], data['Tratte'][3][0], data['Tratte'][4][0])
    bot.sendMessage(update.message.chat_id, msg )


if __name__ == '__main__':
    ds = updater.dispatcher

    ds.add_handler(CommandHandler('start',start))
    ds.add_handler(CommandHandler('get',invia_file, pass_args=True))
    ds.add_handler(CommandHandler('data', oraristp_data))
    ds.add_handler(CallbackQueryHandler(deletedata))
    ds.add_handler(MessageHandler(Filters.text,commands))
    ds.add_handler(MessageHandler(Filters.document, ricevi_file))

    updater.start_polling()