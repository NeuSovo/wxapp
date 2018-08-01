import json
from datetime import timedelta
from dss.Mixin import JsonResponseMixin
from dss.Serializer import serializer

from django.http import JsonResponse, Http404
from django.views.generic import CreateView, ListView, View
from django.utils import timezone

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
            return self.render_to_response({'msg': '订单编号:{}错误'.format(order_id)})

        if not order.exists():
            return self.render_to_response({'msg': '订单编号:{}错误'.format(order_id)})

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
    model = PintuanOrder
    datetime_format = 'string'

    def get(self, request, *args, **kwargs) -> dict:
        if not self.user:
            if not self.wrap_check_token_result():
                return self.render_to_response({'msg': self.msg})

        info = {}
        try:
            pintuan_id = kwargs.get('action') or 0
            pintuan = self.model.objects.filter(pintuan_id=pintuan_id)
        except ValueError:
            return self.render_to_response({'msg': '拼团编号:{} 错误'.format(pintuan_id)})

        if not pintuan.exists():
            return self.render_to_response({'msg': '拼团编号:{} 错误'.format(pintuan_id)})

        pintuan = pintuan.get()
        # 参与的用户 [TODO] 排序
        join_order = pintuan.pintuan_set.all()
        join_user = []
        is_join = False
        join_user_order = {}
        for i in join_order:
            user = i.simple_order.create_user
            if self.user == user:
                is_join = True
                join_user_order = i.simple_order
            join_user.append(serializer(user, exclude_attr=('reg_date', 'last_login', 'openid')))
        
        pintaun_goods = pintuan.pintuan_goods
        # 拼团的基本信息
        pintuan_info = serializer(pintuan, exclude_attr=('pintuan_goods', 'pintuan_goods_id', 'create_user_id', 
                    'reg_date', 'last_login', 'openid'), datetime_format=self.datetime_format)
        pintuan_info['join_count'] = len(join_user)
        pintuan_info['is_join'] = is_join
        pintuan_info['pintuan_count'] = pintaun_goods.pintuan_count
        pintuan_info['can_join'] = pintuan_info['join_count'] < pintuan_info['pintuan_count'] and timezone.now() < pintuan.expire_time if not is_join else False

        # 参与拼团的基本商品信息
        pintuan_goods_info = serializer(pintaun_goods, exclude_attr=('pintuan_count', 'effective'), datetime_format=self.datetime_format)

        info['pintuan_info'] = pintuan_info
        info['pintuan_goods_info'] = pintuan_goods_info
        info['join_user_info'] = join_user
        info['order_info'] = join_user_order

        return self.render_to_response(info)

    def post(self, request, *args, **kwargs) -> dict:
        if not self.wrap_check_token_result():
            return self.render_to_response({'msg': self.msg})

        if not self.init_body():
            return self.render_to_response({'msg': '请求数据格式错误'})

        action = kwargs.get('action')
        # 新团
        if action == 'new':
            pintuan = self.model.create(user=self.user, is_new=True, **self.body)
            if not isinstance(pintuan, self.model):
                return self.render_to_response({'msg': pintuan})

            kwargs['action'] = pintuan.pintuan_id
            # [TODO] 设置参数 避免重复验证用户
            return self.get(request, *args, **kwargs)
        # 参团
        if 'PT' in action:
            pintuan = self.model.create(user=self.user, is_new=False, pintuan_id=action, **self.body)
            if not isinstance(pintuan, self.model):
                return self.render_to_response({'msg': pintuan})
            kwargs['action'] = pintuan.pintuan_id
            return self.get(request, *args, **kwargs)

        return self.render_to_response({'msg': '参数错误'})

    def init_body(self):
        try:
            body = json.loads(self.request.body)
        except Exception as e:
            return False

        self.body = body
        return True


# 微信异步支付消息通知
def pay_notify(request):
    """
    微信异步通知
    """
    data = wx_pay.to_dict(request.data)
    if not wx_pay.check(data):
        return wx_pay.reply("签名验证失败", False)

    try:
        order = SimpleOrder.objects.get(order_id=date.get('out_trade_no'))
    except Exception as e:
        return wx_pay.reply("商家订单号错误", False)

    if order.order_status == 0:
        if order.order_type == 1:
            order.pintuan.pintuan_order.pay(**body)
        order.pay(**body)

    return wx_pay.reply("OK", True)
