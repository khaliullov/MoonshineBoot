# -*- coding: utf-8 -*-
import hashlib
import logging
import urllib
import json
import re

import telepot
import xmltodict
from django.conf import settings


class CommandsProcessor(object):
    def __init__(self, token):
        self.TelegramBot = telepot.Bot(token)
        self.logger = logging.getLogger('telegram.bot')

    def start(self, arg, **payload):
        return """*Поддерживаемые команды*:
`weather` - погода в Симбирске
`anecdote` - случайные анекдоты от anekdot.ru
`md5 [text]` - посчитать md5 от текста
`translate {direction} {text}` - перевести текст
`say {@channel} {text}` - сказать от имени бота в указанный канал

в привате можно слать комманды без начального слеша, например:
`md5 test`
Если бот не реагирует на команды в канале, попробуйте указать команду с его именем, например:
`/md5@moonshine_bot test`
"""

    def help(self, arg, **payload):
        return self.start(arg, **payload)

    def translate(self, arg, **payload):
        parts = arg.split(None, 1)
        if len(parts) != 2:
            return """*Яндекс.Переводчик*
`/translate {direction} {text}`, где:
`{direction}` - направление перевода, например, ru-en или en-ru;
`{text}` - текст для перевода
"""
        api_url = 'https://translate.yandex.net/api/v1.5/tr.json/translate'
        query = {
            'key': settings.YANDEX_TRANSLATE_KEY,
            'lang': parts[0],
            'text': parts[1]
        }
        query_string = urllib.urlencode(query)
        content = urllib.urlopen('{}?{}'.format(api_url, query_string)).read()
        data = json.loads(content)
        if int(data['code']) == 200:
            return data['text'][0]
        return 'Яндекс.Перевод ошибка: {}'.format(data['code'])

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
        return '*' + data['feed']['title']['#text'] + "*\n_" + \
            data['feed']['entry']['title']['#text'] + "_\n" + \
            data['feed']['entry']['summary']['#text'] + "\n[Подробнее ...](" + \
            data['feed']['entry']['link']['@href'] + ")"

    def say(self, arg, **payload):
        parts = arg.split(None, 1)
        if len(parts) != 2:
            return None
        try:
            self.TelegramBot.sendMessage(parts[0], parts[1], parse_mode='Markdown')
        except telepot.exception.TelegramError as exception:
            chat_id = payload['message']['chat']['id']
            self.TelegramBot.sendMessage(chat_id, exception.description, parse_mode='Markdown',
                                         reply_to_message_id=payload['message']['message_id'])
        return None

    def bad_request(self, arg, **payload):
        if 'message' in payload and 'chat' in payload['message'] and \
           'type' in payload['message']['chat'] and \
           payload['message']['chat']['type'] == 'private':
            return 'Bad request. Use `help` to list supported commands.'
        return None

    def dispatch(self, **payload):
        self.logger.info(payload)

        if 'message' not in payload:
            return None
        chat_id = payload['message']['chat']['id']
        text = payload['message'].get('text')  # command
        if not text:
            return None

        parts = text.split(None, 1)

        command = parts[0].strip('/').split("@")[0]
        arg = parts[1] if len(parts) > 1 else ''
        handler = getattr(self, command.lower(), self.bad_request)
        response = handler(arg, **payload)
        if response:
            self.TelegramBot.sendMessage(chat_id, response, parse_mode='Markdown',
                                         disable_web_page_preview=False,
                                         reply_to_message_id=payload['message']['message_id'])
