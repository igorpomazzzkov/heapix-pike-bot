import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, PollAnswerHandler, CallbackQueryHandler

import order

TOKEN = order.read_data_from_file()['token']
scheduler = BackgroundScheduler()
scheduler.start()


def pike(update: Update, context: CallbackContext):
    command = 'pike'
    msg = update.message.text.strip().split(' ')
    try:
        msg = update.message.text.strip().split(' ')[1]
        if check_time_and_chat_data(update, context, command):
            timeout = set_timeout()
            options = ['Тейсти', 'Острый', 'Грибной']
            question = 'Кто-нибудь хочет заказать пайк?\nОтветы будут валидны в течении 20 минут'
            message = create_poll(question, options, timeout, command, update, context)
            payload = {
                message.poll.id: {
                    "question": question,
                    "options": options,
                    "message_id": message.message_id,
                    "chat_id": update.effective_chat.id,
                    "answers": {},
                    "command": command
                }
            }
            context.bot_data.update(payload)
    except IndexError:
        context.bot.sendMessage(update.message.chat_id, 'Введи номер телефона')



def create_poll(question: str, options: list, timeout, command: str, update: Update, context: CallbackContext):
    cron = CronTrigger(hour=timeout.hour, minute=timeout.minute, second=timeout.second, timezone='Europe/Minsk')
    trigger = OrTrigger([cron])
    scheduler.add_job(close_polling, args=[update, context, command], trigger=trigger)
    message = context.bot.sendPoll(update.effective_chat.id, question, options,
                                   is_anonymous=False,
                                   allows_multiple_answers=False)
    return message


def set_timeout():
    target_time = datetime.datetime.now(tz=timezone('Europe/Minsk'))
    close_time = target_time + datetime.timedelta(seconds=10)
    return close_time


def check_time_and_chat_data(update: Update, context: CallbackContext, command: str):
    data = context.bot_data
    if not data:
        return True
    elif data is not {}:
        polls = data.values()
        for poll in polls:
            if poll['command'] == command:
                update.message.reply_text('Голосуй здесь', reply_to_message_id=poll['message_id'], quote=True)
                return False
        return True


def close_polling(update: Update, context: CallbackContext, command: str):
    data = context.bot_data
    taste = []
    spicy = []
    mushrooms = []
    for key, value in data.items():
        if value is not None and value['command'] == command:
            data = context.bot_data[key]['answers']
            for index, pike in data.items():
                if pike == 'Острый':
                    spicy.append(index)
                if pike == 'Тейсти':
                    taste.append(index)
                if pike == 'Грибной':
                    mushrooms.append(index)
            msg_taste = f'Тейсти: '
            msg_spicy = f'\nОстрый: '
            mst_mushroom = f'\nГрибной: '
            for item in taste:
                msg_taste += '@' + item + ' '
            for item in spicy:
                msg_spicy += '@' + item + ' '
            for item in mushrooms:
                mst_mushroom += '@' + item + ' '
            msg = msg_taste + msg_spicy + mst_mushroom
            order_btn = InlineKeyboardButton('order', callback_data=key)
            reply_markup = InlineKeyboardMarkup([[order_btn]])
            update.message.reply_text(msg, reply_markup=reply_markup)


def receive_poll_pike(update: Update, context: CallbackContext):
    answer = update.poll_answer
    poll_id = answer.poll_id
    try:
        options = context.bot_data[poll_id]["options"]
    except KeyError:
        return
    selected_options = answer.option_ids
    answer_result = dict()
    for option_id in selected_options:
        answer_result[update.effective_user.username] = ""
        if option_id != selected_options[-1]:
            answer_result[update.effective_user.username] += options[option_id]
        else:
            answer_result[update.effective_user.username] += options[option_id]
    context.bot_data[poll_id]["answers"].update(answer_result)
    if len(context.bot_data[poll_id]["answers"]) >= 50:
        context.bot.stop_poll(
            context.bot_data[poll_id]["chat_id"], context.bot_data[poll_id]["message_id"]
        )


def order_btn_handler(update: Update, context: CallbackContext):
    data = context.bot_data
    key = update.callback_query
    order.order(data)
    del context.bot_data[key['data']]


if __name__ == '__main__':
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('pike', pike))
    dispatcher.add_handler(CallbackQueryHandler(order_btn_handler))
    dispatcher.add_handler(PollAnswerHandler(receive_poll_pike))
    updater.start_polling()
    updater.idle()
