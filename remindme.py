#!/usr/bin/env python
import time
import random
import re
import threading

import telepot

from secret import TELEGRAM_TOKEN as TOKEN

import reminders


# handle chat messages
def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    text = msg['text']
    if content_type == 'text' and '!remindme' in text.lower():
        reminders.add_reminder(bot, chat_id, msg)


# main function
def main():
    t2 = threading.Thread(target=reminders.main, args=[bot], daemon=True)
    t2.start()

    bot.message_loop({'chat': on_chat_message})
    print('\n\nListening ...')

    # Keep the program running
    while 1:
        time.sleep(3)


bot = telepot.Bot(TOKEN)

if __name__ == "__main__":
    main()
