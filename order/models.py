import random

from django.db import models
from django.utils import timezone

from user.models import User
from goods.models import PinTuanGoods, Goods

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
            self.order_id = self.gen_orderid()
        return super().save(*args, **kwargs)

    @staticmethod
    def create(user=None, is_pintuan=False, *args, **kwargs):
        tmp_order = SimpleOrder()
        if not isinstance(user, User):
            return '用户错误'
        receive_name, receive_phone, receive_address = kwargs.get('receive_name') or None, kwargs.get('receive_phone') or None , kwargs.get('receive_address') or None
        if not (receive_name != None and receive_phone != None and receive_address != None):
            return '收件人信息为空'

        tmp_order.create_user = user
        tmp_order.receive_name = receive_name
        tmp_order.receive_phone = receive_phone
        tmp_order.receive_address = receive_address
        tmp_order.order_type = 1 if is_pintuan else 0
        tmp_order.order_remarks = kwargs.get('order_remarks') or ''
        tmp_order.total_price = 0
        tmp_order.order_id = tmp_order.gen_orderid()

        goods_list = kwargs.get('goods_list') or []
        if not len(goods_list):
            return '下单商品为空'

        if len(goods_list) != 1 and is_pintuan:
            return '只能参与拼团一个商品'

        goods_detail_list = []
        tmp_goods_id = []
        for i in goods_list:
            try:
                goods = Goods.objects.get(id=i.get('goods_id', 0))
                if goods.id in tmp_goods_id:
                    return '重复提交商品id'
            except Exception as e:
                return '商品id错误'

            tmp_goods_id.append(goods.id)

            # 如果是拼团 则以拼团价为准
            # 这里不做拼团活动是否到期，以及拼团人数是否已满
            goods_price = goods.pintuangoods.pintuan_price if is_pintuan else goods.now_price

            # 拼团数量只能为1
            goods_count = int(i.get('goods_count') or 1)
            if goods_count != 1 and is_pintuan:
                return '拼团只能拼一件'

            # 查库存
            if goods.inventory < goods_count or goods_count == 0:
                return '数量错误，或库存不足'

            # 批量创建订单详细
            goods_detail_list.append(SimpleOrderDetail(order=tmp_order, goods=goods, 
                    goods_count=goods_count, goods_price=goods_price))

            # 减库存,加销量
            # [TODO] 加入Task任务队列
            goods.inventory -= goods_count
            goods.goodsprofile.sale_count += goods_count
            goods.save()
            goods.goodsprofile.save()

            tmp_order.total_price += (goods_price * goods_count)

        try:
            tmp_order.save()
            SimpleOrderDetail.objects.bulk_create(goods_detail_list)
        except Exception as e:
            return str(e)

        return tmp_order

    def gen_orderid(self):
        return timezone.now().strftime("%Y%m%d") + str(self.order_type) + str(self.create_user.id)[-1] + \
                str(random.randint(1000, 9999))


class PintuanOrder(BaseOrder):

    class Meta:
        verbose_name = "拼团订单"
        verbose_name_plural = "拼团订单"

    def __str__(self):
        return self.pintuan_id

    pintuan_id = models.CharField(max_length=20, primary_key=True, verbose_name='拼团id')
    pintuan_goods = models.ForeignKey(PinTuanGoods, on_delete=models.SET_NULL, null=True, verbose_name='拼团商品')

    def gen_pintuan_id(self):
        return 'PT' + str(timezone.now().strftime("%Y%m%d")) + str(self.pintuan_goods.id) + str(random.randint(1000, 9999))

    def save(self, *args, **kwargs):
        if not self.pintuan_id:
            self.pintuan_id = self.gen_pintuan_id()
        return super().save(*args, **kwargs)

    def is_effective(self):
        """
        根据当前时间 是否在于 拼团创建时间 + 拼团商品设定的有效小时之内 
        并且拼团人数self.pintuan_set.count() < self.pintuan_goods.pintuan_count
        来决定是否可以继续参与拼团

        对于已经发起平团还未拼团成功的，但是拼团商品结束时间已到，用户仍然可以继续参与拼团
        """
        pass


class PinTuan(models.Model):
    """
    [todo]
        拼团参与人数增加
    """
    class Meta:
        verbose_name = "拼团单"
        verbose_name_plural = "拼团单"
    
    pintuan_order = models.ForeignKey(PintuanOrder, on_delete=models.CASCADE)
    simple_order = models.ForeignKey(SimpleOrder, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super().save()


class SimpleOrderDetail(models.Model):

    class Meta:
        verbose_name = "订单详细"
        verbose_name_plural = "订单详细"
        # unique_together = ('order', 'goods')

    def __str__(self):
        return str(self.order)

    order = models.ForeignKey(SimpleOrder, on_delete=models.CASCADE)
    goods = models.ForeignKey(Goods, on_delete=models.SET_NULL, null=True, verbose_name='商品')
    goods_count = models.IntegerField(default=1, verbose_name='下单数量')
    goods_price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='下单价')
