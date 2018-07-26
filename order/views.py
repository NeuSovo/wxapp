import json
from django.http import JsonResponse, Http404
from django.views.generic import CreateView, ListView, View
from dss.Mixin import JsonResponseMixin
from dss.Serializer import serializer
from .models import *
from user.auth import CheckUserWrap

class SimpleOrderView(JsonResponseMixin, CreateView, CheckUserWrap):
    model = SimpleOrder
    exclude_attr = ('openid', 'last_login', 'reg_date', 'order', 'category_id')

    def get(self, request, *args, **kwargs) -> dict:
        if not self.wrap_check_token_result():
            return self.render_to_response({'msg': self.msg})
        try:
            order_id = kwargs.get('order_id') or 0
            order = self.model.objects.filter(order_id=order_id)
        except ValueError:
            return self.render_to_response({'msg': 'order_id 错误'})

        if not order.exists():
            return self.render_to_response({'msg': 'order_id 错误'})

        order = order.get()
        return self.render_to_response({'order_info': order, 'detail': order.simpleorderdetail_set.all()})

    def post(self, request, *args, **kwargs) -> dict:
        if not self.wrap_check_token_result():
            return self.render_to_response({'msg': self.msg})
        if not self.init_body():
            return self.render_to_response({'msg': '请求数据格式错误'})

        order = self.model.create(user=self.user, is_pintuan=False, **self.body)

        if not isinstance(order, self.model):
            return self.render_to_response({'msg': order})

        return self.render_to_response({'order_info': order, 'detail': order.simpleorderdetail_set.all()})

    def init_body(self):
        try:
            body = json.loads(self.request.body)
        except Exception as e:
            return False

        self.body = body
        return True


class PinTuanOrderView(JsonResponseMixin, CreateView, CheckUserWrap):

    def get(self, request, *args, **kwargs) -> dict:
        if not self.wrap_check_token_result():
            return self.render_to_response({'msg': self.msg})

    def post(self, request, *args, **kwargs) -> dict:
        if not self.wrap_check_token_result():
            return self.render_to_response({'msg': self.msg})

        if not self.init_body():
            return self.render_to_response({'msg': '请求数据格式错误'})
        action = kwargs.get('action')

        if action == 'new':
            goods = self.get_pintuan_goods()
            if not isinstance(goods, Goods):
                return self.render_to_response({'msg': goods})
            if goods.is_pintuan():
                order = SimpleOrder.create(user=self.user, is_pintuan=True, **self.body)
                if not isinstance(order, SimpleOrder):
                    return self.render_to_response({'msg': order})
                pintuan = PintuanOrder(pintuan_goods=goods.pintuangoods, create_user=self.user)
                pintuan.save()
                PinTuan(pintuan_order=pintuan, simple_order=order).save()
            else:
                return self.render_to_response({'msg': '商品已失效'})
            return self.render_to_response({'msg': pintuan.pintuan_id})


    def init_body(self):
        try:
            body = json.loads(self.request.body)
        except Exception as e:
            return False

        self.body = body
        return True

    def get_pintuan_goods(self):
        try:
            goods_id = self.body.get('goods_list')[0].get('goods_id')
            goods = Goods.objects.get(id=goods_id)
        except Exception as e:
            return '商品id错误 '

        return goods
