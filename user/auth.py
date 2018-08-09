import json

from django.conf import settings

from .models import User
from .tools import *


class WechatSdk:
    APPID = ''
    SECRET = ''

    def __init__(self, code):
        super(WechatSdk, self).__init__()
        self.code = code

    def get_openid(self):
        params = {
            'appid': self.APPID,
            'secret': self.SECRET,
            'js_code': self.code,
            'grant_type': 'authorization_code'
        }

        data = request_jscode(params)

        info = data.json()

        if 'openid' not in info:
            if settings.DEBUG:
                info = {
                    'openid': self.code,
                    'session_key': 'SESSIONKEY',
                }
            else:
                return info

        return info


class UserWrap:
    msg = ''
    token = ''

    def check(self):
        try:
            body = json.loads(self.request.body)
        except:
            self.msg = 'param error'
            return

        code = body.get('code')
        wx = WechatSdk(code=code)
        self.nick_name = body.get('nick_name', 'nick_name')
        self.avatar_url = body.get('avatar_url', 'https://demo.ava')
        self.user_info = wx.get_openid()
        if 'openid' not in self.user_info:
            self.msg = self.user_info['errmsg']

    def check_user_reg(self):
        if User.objects.filter(openid=self.user_info['openid']).exists():
            self.user = User.objects.get(openid=self.user_info['openid'])
            return True
        else:
            return False

    def reg_user(self):
        user = User(openid=self.user_info['openid'], nick_name=self.nick_name, avatar_url=self.avatar_url)
        user.save()
        return user, self.gen_token(user)

    def gen_token(self, user):
        token = get_random_string(64)
        wxapp_redis.set(':'.join(['wxapp', 'token', token]), user.openid, ex=TOKEN_EXPIRE_HOUR * 3600)
        return token

    def update_profile(self):
        self.user.nick_name = self.nick_name
        self.user.avatar_url = self.avatar_url
        self.user.save()


class CheckUserWrap:
    token = None
    user = None

    def get_current_token(self):
        self.token = self.request.META.get('HTTP_AUTHORIZATION') or self.request.COOKIES.get('token') or None
        return self.token

    def check_token(self):
        self.get_current_token()
        if not self.token:
            return False
        user = self.get_user_by_token()
        if user:
            self.user = user
            return True
        return False

    def wrap_check_token_result(self):
        result = self.check_token()
        if not result:
            self.msg = 'Token 错误或过期'
            return False
        return True

    def get_user_by_token(self):
        openid = user = None
        if wxapp_redis.exists(':'.join(['wxapp', 'token', self.token])):
            openid = wxapp_redis.get(':'.join(['wxapp', 'token', self.token])).decode('utf-8')

        if openid:
            try:
                user = User.objects.get(openid=str(openid))
            except:
                user = None

        return user
