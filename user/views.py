from dss.Serializer import serializer
from dss.Mixin import (FormJsonResponseMixin, JsonResponseMixin,
                       MultipleJsonResponseMixin)

from django.shortcuts import render
from django.views.generic import (CreateView, FormView, ListView, UpdateView,
                                  View)

from .auth import WechatSdk, UserWrap
from .models import *
# Create your views here.

class LoginUserView(JsonResponseMixin, CreateView, UserWrap):
    model = User

    def post(self, request, *args, **kwargs) -> dict:
        self.check()
        if self.msg:
            return self.render_to_response({'msg': self.msg})

        if self.check_user_reg():
            token = self.gen_token(self.user)
            self.update_profile()
            user = serializer(self.user)
            return self.render_to_response({'msg': 'success', 'user_obj': user, 'token': token})
        else:
            user, token = self.reg_user()
            return self.render_to_response({'msg': 'success', 'user_obj': user, 'token': token})
