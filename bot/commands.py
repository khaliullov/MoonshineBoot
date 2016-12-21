# -*- coding: utf-8 -*-
import hashlib
import logging
import urllib
import json
import re

import telepot
import xmltodict


class CommandsProcessor(object):
    def __init__(self, token):
        self.TelegramBot = telepot.Bot(token)
        self.logger = logging.getLogger('telegram.bot')

    def start(self, arg, **payload):
        return 'Not yet implemented'

    def help(self, arg, **payload):
        return self.start(arg, **payload)

    def me(self, arg, **payload):
        return 'молодец'

    def md5(self, arg, **payload):
        m = hashlib.md5()
        m.update(arg)
        return m.hexdigest()

    def anecdote(self, arg, **payload):
        content = urllib.urlopen('http://www.anekdot.ru/rss/randomu.html').read()
        m = re.search(r'anekdot_texts = (.*);\n', content)
        if m:
            try:
                data = json.loads(m.group(1).replace('<br>', '\n').replace('"', '\\"').replace('\'', '"'), strict=False)
            except ValueError:
                return 'Failed to parse JavaScript'
            result = "*Анекдоты из России*"
            separator = "\n"
            for joke in data:
                result += separator + joke + "\n"
                separator = "\n\\* \\* \\*\n"
            return result
        return 'Protocol has been changed'

    def weather(self, arg, **payload):
        data = xmltodict.parse(urllib.urlopen('http://rp5.ru/rss/507958/ru'))
        return '*' + data['feed']['title']['#text'] + "*\n__" + \
            data['feed']['entry']['title']['#text'] + "__\n" + \
            data['feed']['entry']['summary']['#text'] + "\n[Подробнее ...](" + \
            data['feed']['entry']['link']['@href'] + ")"

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

        if 'message' not in payload:
            return None
        chat_id = payload['message']['chat']['id']
        text = payload['message'].get('text')  # command

        parts = text.split(None, 1)

        command = parts[0].strip('/').split("@")[0]
        arg = parts[1] if len(parts) > 1 else ''
        handler = getattr(self, command.lower(), self.bad_request)
        response = handler(arg, **payload)
        if response:
            self.TelegramBot.sendMessage(chat_id, response, parse_mode='Markdown')
