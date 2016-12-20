# -*- coding: utf-8 -*-
import hashlib
import logging

import telepot


class CommandsProcessor(object):
    def __init__(self, token):
        self.TelegramBot = telepot.Bot(token)
        self.logger = logging.getLogger('telegram.bot')

    def start(self, arg, **payload):
        return 'Not yet implemented'

    def help(self, arg, **payload):
        return self.start(arg)

    def me(self, arg, **payload):
        return 'молодец'

    def md5(self, arg, **payload):
        m = hashlib.md5()
        m.update(arg)
        return m.hexdigest()

    def say(self, arg, **payload):
        parts = arg.split(None, 1)
        if len(parts) != 2:
            return None
        self.TelegramBot.sendMessage(parts[0], parts[1], parse_mode='Markdown')
        return None

    def bad_request(self, arg, **payload):
        if 'message' in payload and 'chat' in payload['message'] and \
           'type' in payload['message']['chat'] and \
           payload['message']['chat']['type'] == 'private':
            return 'Bad request'
        return None

    def dispatch(self, **payload):
        self.logger.info(payload)

        chat_id = payload['message']['chat']['id']
        text = payload['message'].get('text')  # command

        parts = text.split(None, 1)

        command = parts[0].strip('/').split("@")[0]
        arg = parts[1] if len(parts) > 1 else ''
        handler = getattr(self, command.lower(), self.bad_request)
        response = handler(arg, **payload)
        if response:
            self.TelegramBot.sendMessage(chat_id, response, parse_mode='Markdown')
