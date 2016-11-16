# -*- coding: utf-8 -*-
import hashlib
import logging

import telepot


class CommandsProcessor(object):
    def __init__(self, token):
        self.TelegramBot = telepot.Bot(token)
        self.logger = logging.getLogger('telegram.bot')

    def start(self, arg):
        return 'Not yet implemented'

    def help(self, arg):
        return self.start(arg)

    def me(self, arg):
        return 'молодец'

    def md5(self, arg):
        m = hashlib.md5()
        m.update(arg)
        return m.hexdigest()

    def bad_request(self, arg):
        return 'Bad request'

    def dispatch(self, text, chat_id):
        parts = text.split(None, 1)

        command = parts[0].strip('/')
        arg = parts[1] if len(parts) > 1 else ''
        handler = getattr(self, command.lower(), self.bad_request)
        self.TelegramBot.sendMessage(chat_id, handler(arg), parse_mode='Markdown')
