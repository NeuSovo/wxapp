import random

from django.db import models
from django.utils import timezone

from user.models import User
from goods.models import PinTuanGoods

class BaseOrder(models.Model):

    class Meta:
        abstract = True

    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    create_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='创建用户')
    done_time = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')


class SimpleOrder(BaseOrder):
    class Meta:
        verbose_name = "普通订单"
        verbose_name_plural = "普通订单"

    order_type_choices = (
        (0, '普通订单'),
        (1, '团购订单')
    )
        # [todo] 
    # 退款，运费，优惠卷
    order_status_choices = (
        (-1, '取消'),
        (1, '待发货'),
        (2, '已发货'),
        (3, '已完成')
    )

    def __str__(self):
        return str(self.order_id)

    order_id = models.BigIntegerField(primary_key=True, verbose_name='订单id')
    order_type = models.IntegerField(choices=order_type_choices ,default=0,verbose_name='订单类型') 
    order_status = models.IntegerField(choices=order_status_choices, default=1, verbose_name='订单状态')
    total_price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='总价')

    receive_name  = models.CharField(max_length=50, verbose_name='收货人')
    receive_phone  = models.CharField(max_length=50, verbose_name='收货人电话')
    receive_address  = models.CharField(max_length=100, verbose_name='收货人地址')

    order_remarks = models.TextField(null=True, blank=True, verbose_name='留言/备注')
    tracking_number = models.BigIntegerField(null=True, blank=True, verbose_name='快递单号')

    def save(self, *args, **kwargs):
        if self.order_id == None:
            self.order_id = timezone.now().strftime("%Y%m%d") + str(self.order_type) + str(self.create_user.id)[-1] + \
                str(random.randint(1000, 9999))
        return super().save(*args, **kwargs)


class PintuanOrder(BaseOrder):

    class Meta:
        verbose_name = "拼团订单"
        verbose_name_plural = "拼团订单"

    def __str__(self):
        return self.pintuan_id

    pintuan_id = models.BigIntegerField(primary_key=True, verbose_name='拼团id')
    pintuan_goods = models.ForeignKey(PinTuanGoods, on_delete=models.SET_NULL, null=True, verbose_name='拼团商品')


class PinTuan(models.Model):
    class Meta:
        verbose_name = "拼团单"
        verbose_name_plural = "拼团单"
    
    pintuan_order = models.ForeignKey(PintuanOrder, on_delete=models.CASCADE)
    order = models.ForeignKey(SimpleOrder, on_delete=models.CASCADE)


class SimpleOrderDetail(models.Model):

    class Meta:
        verbose_name = "订单详细"
        verbose_name_plural = "订单详细s"

    def __str__(self):
        pass

    order = models.ForeignKey(SimpleOrder, on_delete=models.CASCADE)
    goods = models.ForeignKey(goods, on_delete=models.SET_NULL, null=True)
    goods_count = models.IntegerField(default=1, verbose_name='下单数量')
    goods_price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='下单价')
