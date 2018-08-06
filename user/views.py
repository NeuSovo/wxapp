from dss.Serializer import serializer
from dss.Mixin import (FormJsonResponseMixin, JsonResponseMixin,
                       MultipleJsonResponseMixin)

from django.shortcuts import render
from django.utils import timezone
from django.views.generic import (CreateView, FormView, ListView, UpdateView,
                                  View)

from .auth import WechatSdk, UserWrap, CheckUserWrap
from .models import *
from order.models import SimpleOrder, PintuanOrder
# Create your views here.


class RegUserView(JsonResponseMixin, CreateView, UserWrap):
    model = User

    def post(self, request, *args, **kwargs) -> dict:
        self.check()
        if self.msg:
            return self.render_to_response({'msg': self.msg})

        if self.check_user_reg():
            token = self.gen_token(self.user)
            self.update_profile()
            # user = serializer(self.user)
            return self.render_to_response({'msg': 'success', 'user_obj': self.user, 'token': token})
        else:
            user, token = self.reg_user()
            return self.render_to_response({'msg': 'success', 'user_obj': user, 'token': token})


class LoginUserView(JsonResponseMixin, View, CheckUserWrap):

    def post(self, request, *args, **kwargs):
        if not self.wrap_check_token_result():
            return self.render_to_response({'msg': self.msg})

        return self.render_to_response({'msg': 'success', 'user_obj': self.user})


class UserOrderView(MultipleJsonResponseMixin, ListView, CheckUserWrap):
    model = SimpleOrder
    paginate_by = 15
    exclude_attr = ('create_user')

    def get_queryset(self):
        if not self.wrap_check_token_result():
            return [{'msg': self.msg}]

        kwargs = {}
        try:
            order_status = int(self.request.GET.get('order_status') or 1)
        except:
            return []

        if order_status:
            kwargs['order_status'] = order_status

        queryset = super(UserOrderView, self).get_queryset()
        queryset = queryset.filter(create_user=self.user, **kwargs)

        return queryset


class PinTuanOrderView(MultipleJsonResponseMixin, ListView, CheckUserWrap):
    model = PintuanOrder
    paginate_by = 15
    exclude_attr = ('create_user', 'category_id','goods_id')

    def get_queryset(self):
        if not self.wrap_check_token_result():
            return [{'msg': self.msg}]
        kwargs = {}
        try:
            # 1 待拼成, 2已成功, 3 失效
            pintuan_status = int(self.request.GET.get('pintuan_status') or 1)
        except:
            return []
        if pintuan_status == 1:
            kwargs['done_time__isnull'] = True
            kwargs['expire_time__gte'] = timezone.now()

        if pintuan_status == 2:
            kwargs['done_time__isnull'] = False

        if pintuan_status == 3:
            kwargs['done_time__isnull'] = True
            kwargs['expire_time__lte'] = timezone.now()

        print (kwargs)
        queryset = super(PinTuanOrderView, self).get_queryset()

        queryset = queryset.filter(pintuan__simple_order__create_user=self.user, **kwargs)
        return queryset