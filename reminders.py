import time
import datetime
import re
from pytz import timezone

import pyrebase

from secret import FIREBASE_KEY, FIREBASE_PASSWORD
from config import FIREBASE_POLLING_TIME


def update_token(now, start_time):
    global __user
    if now - start_time > 3500:
        print('refreshing token')
        __user = __auth.refresh(__user['refreshToken'])
        return now
    return start_time


def main(bot):
    start_time = datetime.datetime.now().replace(second=0, microsecond=0).timestamp()
    while 1:
        now = datetime.datetime.now().replace(second=0, microsecond=0).timestamp()

        start_time = update_token(now, start_time)
        reminders = __db.child('reminders').order_by_child('reminder_time').equal_to(f"{now}").get(__user['idToken'])

        for reminder in reminders.each():
            r = reminder.val()
            bot.sendMessage(
                r['chat_id'],
                f'[@{r["user"]["name"]}]({r["user"]["id"]}) you asked me to remind you this.',
                reply_to_message_id=r['reply_id'],
                parse_mode='Markdown')
            __db.child('reminders').child(reminder.key()).remove(__user['idToken'])

        time.sleep(FIREBASE_POLLING_TIME)


def add_reminder(bot, chat_id, msg):
    if 'reply_to_message' not in msg:
        return

    user_id = msg['from']['id']
    user_name = msg['from']['username']
    reply_id = msg['reply_to_message']['message_id']
    msg_text = msg['text']
    msg_time = datetime.datetime.fromtimestamp(int(msg['date']))

    time_list = re.findall(r'[0-9]+?[d|h|m]', msg_text)
    time_str = ""

    if not time_list:
        return

    reminder_time = msg_time.replace(second=0, microsecond=0)
    for index, time_item in enumerate(time_list):
        type = None
        if 'd' in time_item:
            t = int(time_item.replace('d', ''))
            reminder_time = reminder_time + datetime.timedelta(days=t)
            type = 'day'
        if 'h' in time_item:
            t = int(time_item.replace('h', ''))
            reminder_time = reminder_time + datetime.timedelta(hours=t)
            type = 'hour'
        if 'm' in time_item:
            t = int(time_item.replace('m', ''))
            reminder_time = reminder_time + datetime.timedelta(minutes=t)
            type = 'minute'
             
        time_str = f'{time_str}{t} {type}s' if t > 1 else f'{time_str}{t} {type}'
        time_str = f'{time_str}, ' if index < len(time_list) - 1 else f'{time_str}.'

    data = {
        'chat_id': chat_id,
        'user': {
            'id': user_id,
            'name': user_name
        },
        'reminder_time': f'{reminder_time.timestamp()}',
        'reply_id': reply_id
    }

    __db.child('reminders').push(data, __user['idToken'])

    bot.sendMessage(
        chat_id,
        f'[@{user_name}](tg://user?id={user_id}) i will remind you this in {time_str}',
        reply_to_message_id=reply_id,
        parse_mode='Markdown')


firebase_config = {
  "apiKey": FIREBASE_KEY,
  "authDomain": "giorginoteck-bot-1529002203876.firebaseapp.com",
  "databaseURL": "https://giorginoteck-bot-1529002203876.firebaseio.com/",
  "storageBucket": "giorginoteck-bot-1529002203876.appspot.com"
}

__firebase = pyrebase.initialize_app(firebase_config)
__auth = __firebase.auth()
__user = __auth.sign_in_with_email_and_password('fabio.sangregorio@gmail.com', FIREBASE_PASSWORD)
__db = __firebase.database()
