import json
import redis
import random
import requests
from tenacity import *
from hashlib import sha256

from django.conf import settings

from .models import User

try:
    random = random.SystemRandom()
    using_sysrandom = True
except NotImplementedError:
    using_sysrandom = False

redis_session = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
TOKEN_EXPIRE_HOUR = 72

def get_random_string(length=12,
                      allowed_chars='abcdefghijklmnopqrstuvwxyz'
                                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-/+'):
    """
    Return a securely generated random string.

    The default length of 12 with the a-z, A-Z, 0-9 character set returns
    a 71-bit value. log_2((26+26+10)^12) =~ 71 bits
    """
    if not using_sysrandom:
        # This is ugly, and a hack, but it makes things better than
        # the alternative of predictability. This re-seeds the PRNG
        # using a value that is hard for an attacker to predict, every
        # time a random string is required. This may change the
        # properties of the chosen random sequence slightly, but this
        # is better than absolute predictability.
        random.seed(
            sha256(
                ('%s%s%s' % (random.getstate(), time.time(), settings.SECRET_KEY)).encode()
            ).digest()
        )
    return ''.join(random.choice(allowed_chars) for i in range(length))

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

        data = self.request_jscode(params)

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

    @retry(retry=retry_if_exception_type(requests.exceptions.ConnectionError), stop=(stop_after_attempt(3) | stop_after_delay(3)))
    def request_jscode(self, params):
        try:
            data = requests.get(
                'https://api.weixin.qq.com/sns/jscode2session', params=params)
        except requests.exceptions.ConnectionError as e:
            raise requests.exceptions.ConnectionError

        return data


class UserWrap:
    msg = ''
    token = ''

    def check(self):
        try:
            body = json.loads(self.request.body)
        except:
            self.msg = 'param error'
            return

        code =body.get('code')
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
        redis_session.set(':'.join(['wxapp','token', token]), user.openid, ex=TOKEN_EXPIRE_HOUR * 3600)
        return token

    def update_profile(self):
        self.user.nick_name=self.nick_name
        self.user.avatar_url=self.avatar_url
        self.user.save()


class CheckUserWrap:
    token = None
    user = None

    def get_current_token(self):
        self.token = self.request.META.get('HTTP_AUTHORIZATION') or self.request.COOKIES.get('token') or None
        return self.token

    def check_token(self):
        self.get_current_token()
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
        openid = None
        if redis_session.exists(':'.join(['wxapp','token', self.token])):
            openid = redis_session.get(':'.join(['wxapp','token', self.token])).decode('utf-8')

        if openid:
            try:
                user = User.objects.get(openid=str(openid))
            except:
                user = None

        return user
