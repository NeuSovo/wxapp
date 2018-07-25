import time
import redis
import random
import requests
from tenacity import *
from hashlib import sha256
from django.conf import settings

try:
    random = random.SystemRandom()
    using_sysrandom = True
except NotImplementedError:
    using_sysrandom = False

wxapp_redis = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
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



@retry(retry=retry_if_exception_type(requests.exceptions.ConnectionError), stop=(stop_after_attempt(3) | stop_after_delay(3)))
def request_jscode(params):
    try:
        data = requests.get(
            'https://api.weixin.qq.com/sns/jscode2session', params=params)
    except requests.exceptions.ConnectionError as e:
        raise requests.exceptions.ConnectionError

    return data