import json
import logging

from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .commands import CommandsProcessor


class HeartBeatView(View):
    def handle(self, request, *args, **kwargs):
        return JsonResponse({"ok": True}, status=200)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() in ['get', 'post', 'head']:
            return self.handle(request, *args, **kwargs)
        return JsonResponse({"ok": False,
                             "description": "Method not allowed",
                             "error_code": 405}, status=405)


class CommandReceiveView(View):
    def __init__(self):
        super(CommandReceiveView, self).__init__()
        self.logger = logging.getLogger('telegram.bot')
        self.cp = None

    def post(self, request, bot_token):
        raw = request.body.decode('utf-8')
        self.logger.info(raw)

        if self.cp is None:
            self.cp = CommandsProcessor(bot_token)

        try:
            payload = json.loads(raw)
        except ValueError:
            return JsonResponse({"ok": False,
                                 "description": "Bad request",
                                 "error_code": 400}, status=400)
        else:
            chat_id = payload['message']['chat']['id']
            cmd = payload['message'].get('text')  # command
            self.cp.dispatch(cmd, chat_id)

        return JsonResponse({"ok": True}, status=200)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() == 'post':
            return self.post(request, *args, **kwargs)
        return JsonResponse({"ok": False,
                             "description": "Method not allowed",
                             "error_code": 405}, status=405)
