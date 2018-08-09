import random
from datetime import datetime, timedelta
from user.models import User

from django.db import models, transaction
from django.utils import timezone
from weixin import WeixinError, WeixinPay

from goods.models import Goods, PinTuanGoods
from order import tasks

wx_pay = WeixinPay('app_id', 'mch_id', 'mch_key', 'notify_url', '/path/to/key.pem', '/path/to/cert.pem')  # 后两个参数可选


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
        default_permissions = ('view',)

    order_type_choices = (
        (0, '普通订单'),
        (1, '团购订单')
    )
    # [TODO] 退款，运费，优惠卷
    order_status_choices = (
        (-1, '取消'),
        (0, '待支付'),
        (1, '待发货'),
        (2, '已发货'),
        (3, '已完成')
    )

    def __str__(self):
        return str(self.order_id)

    order_id = models.BigIntegerField(primary_key=True, verbose_name='订单编号')
    order_type = models.IntegerField(choices=order_type_choices, default=0, verbose_name='订单类型')
    order_status = models.IntegerField(choices=order_status_choices, default=0, verbose_name='订单状态')
    total_price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='总价')

    receive_name = models.CharField(max_length=50, verbose_name='收货人')
    receive_phone = models.CharField(max_length=50, verbose_name='收货人电话')
    receive_address = models.CharField(max_length=100, verbose_name='收货人地址')

    order_remarks = models.TextField(null=True, blank=True, verbose_name='留言/备注')
    tracking_company = models.CharField(max_length=20, blank=True, verbose_name='快递公司')
    tracking_number = models.BigIntegerField(null=True, blank=True, verbose_name='快递单号')
    transaction_id = models.CharField(max_length=32, null=True, blank=True, verbose_name='微信订单号')
    pay_time = models.DateTimeField(null=True, blank=True, verbose_name='支付时间')

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = self.gen_orderid()
        return super().save(*args, **kwargs)

    @staticmethod
    def create(user=None, is_pintuan=False, *args, **kwargs):
        tmp_order = SimpleOrder()
        if not isinstance(user, User):
            return '用户错误'
        receive_name, receive_phone, receive_address = kwargs.get('receive_name') or None, kwargs.get(
            'receive_phone') or None, kwargs.get('receive_address') or None
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
                return '商品编号错误'

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
            # 支付后在操作
            # goods.inventory -= goods_count
            # goods.goodsprofile.sale_count += goods_count
            # goods.save()
            # goods.goodsprofile.save()

            tmp_order.total_price += (goods_price * goods_count)

        try:
            with transaction.atomic():
                tmp_order.save()
                SimpleOrderDetail.objects.bulk_create(goods_detail_list)
        except Exception as e:
            return str(e)

        tasks.delete_unpay_order.apply_async((tmp_order.order_id,), countdown=60 * 15)
        return tmp_order

    def pay(self, *args, **kwargs):
        success = kwargs.get('result_code') == 'SUCCESS'
        if success:
            # [TODO]微信支付成功的相关操作：
            self.order_status = 1
            self.transaction_id = kwargs.get('transaction_id')
            self.pay_time = datetime.strptime(kwargs.get('time_end'), '%Y%m%d%H%M%S')
            self.save()
            self.sync_inventory()
        else:
            self.delete()

    def refund(self, *args, **kwargs):
        # [TODO]微信退款的相关操作：
        # wx_pay.refund(out_trade_no=self.transaction_id)
        self.order_status = -1
        self.sync_inventory(add=False)
        self.save()

    def sync_inventory(self, add=True):
        try:
            with transaction.atomic():
                for i in self.simpleorderdetail_set.all():
                    i.goods_count = i.goods_count if add else -(i.goods_count)
                    i.inventory -= i.goods_count
                    i.goodsprofile.sale_count += i.goods_count
                    i.save()
                    i.goodsprofile.save()
        except Exception as e:
            pass

    def gen_orderid(self):
        return timezone.now().strftime("%Y%m%d") + str(self.order_type) + str(self.create_user.id)[-1] + \
            str(random.randint(1000, 9999))


class PintuanOrder(BaseOrder):
    # [TODO] 拼团失效的订单进行退款 和设置订单状态
    # 过滤条件
    #

    class Meta:
        verbose_name = "拼团订单"
        verbose_name_plural = "拼团订单"
        ordering = ('-create_time', )

    def __str__(self):
        return self.pintuan_id

    pintuan_id = models.CharField(max_length=20, primary_key=True, verbose_name='拼团编号')
    expire_time = models.DateTimeField(verbose_name='过期时间')
    pintuan_goods = models.ForeignKey(PinTuanGoods, on_delete=models.SET_NULL, null=True, verbose_name='拼团商品')

    def gen_pintuan_id(self):
        return 'PT' + str(timezone.now().strftime("%Y%m%d")) + str(self.pintuan_goods.goods.id) + str(random.randint(1000, 9999))

    def save(self, *args, **kwargs):
        if not self.pintuan_id:
            self.pintuan_id = self.gen_pintuan_id()
            self.expire_time = timezone.now() + timedelta(hours=int(self.pintuan_goods.effective))
        return super().save(*args, **kwargs)

    def is_effective(self):
        """
        根据当前时间 是否在于 拼团创建时间 + 拼团商品设定的有效小时之内 
        并且拼团人数self.pintuan_set.count() < self.pintuan_goods.pintuan_count
        来决定是否可以继续参与拼团

        对于已经发起平团还未拼团成功的，但是拼团商品结束时间已到，用户仍然可以继续参与拼团
        """
        is_expire = timezone.now() > self.expire_time
        is_full = self.pintuan_set.count() == self.pintuan_goods.pintuan_count
        if is_expire and not is_full:
            return False, '该团已失效'

        if is_full:
            return False, '该团已拼团成功'

        if not is_full and not is_expire:
            return True, '正在拼团'

    @staticmethod
    def create(user=None, is_new=False, pintuan_id=None, *args, **kwargs):
        if not isinstance(user, User):
            return False, '用户错误'

        try:
            goods_id = kwargs.get('goods_list')[0].get('goods_id')
            goods = Goods.objects.get(id=goods_id)
            goods.pintuangoods
        except Exception as e:
            if is_new:
                return '商品编号错误'

        # 限制购买措施，订单类型为拼团，同一用户，同一商品，状态>=0，都算为一个有效订单
        # 商品设置限制数小于等于0 则不限制用户购买数量
        t_limit = SimpleOrderDetail.objects.filter(
            order__order_type=1, order__create_user=user, goods=goods, order__order_status__gte=0).count()
        if goods.pintuangoods.limit > 0:
            if t_limit > goods.pintuangoods.limit:
                return '超过限制数量'

        # 新团
        # 创建拼团单,并创建开团人订单
        if is_new:
            if goods.is_pintuan():
                order = SimpleOrder.create(user=user, is_pintuan=True, **kwargs)
                if not isinstance(order, SimpleOrder):
                    return order
                pintuan = PintuanOrder(pintuan_goods=goods.pintuangoods, create_user=user)
                # [TODO] with transaction.atomic():
                pintuan.save()
                PinTuan(pintuan_order=pintuan, simple_order=order).save()
                return pintuan
            else:
                return '商品已失效'

        # 用户参团,只创建订单
        try:
            pintuan = PintuanOrder.objects.get(pintuan_id=pintuan_id)
        except Exception as e:
            return '拼团编号错误'

        # 拼团编号与商品编号不对应
        if pintuan.pintuan_goods != goods.pintuangoods:
            return '拼团编号与商品编号不对应'

        # 查看该团是否能够加入
        status, msg = pintuan.is_effective()
        if not status:
            return msg

        # 确保用户没有重复参与
        if pintuan.pintuan_set.filter(simple_order__create_user=user).exists():
            return '重复参团'

        # 创建普通订单
        order = SimpleOrder.create(user=user, is_pintuan=True, **kwargs)
        if not isinstance(order, SimpleOrder):
            return order

        PinTuan(pintuan_order=pintuan, simple_order=order).save()

        # 如果参团完成,设置完成时间
        # 支付后在操作
        # if pintuan.pintuan_set.count() == pintuan.pintuan_goods.pintuan_count:
        #     pintuan.done_time = timezone.now()
        #     pintuan.save()
        return pintuan

    def pay(self, *args, **kwargs):
        success = kwargs.get('result_code') == 'SUCCESS'
        user = User.objects.get(openid=kwargs.get('openid'))
        if success:
            if self.pintuan_set.count() == self.pintuan_goods.pintuan_count:
                self.done_time = timezone.now()
                self.save()
            if self.create_user == user:
                tasks.expire_pt_task.apply_async((self.pintuan_id, ), eta=datetime.utcnow() +
                                                 timedelta(hours=int(self.pintuan_goods.effective)))
        else:
            if self.create_user == user:
                self.delete()


class PinTuan(models.Model):
    """
    [TODO] 拼团参与人数增加
    """
    class Meta:
        verbose_name = "参团订单"
        verbose_name_plural = "参团订单"

    pintuan_order = models.ForeignKey(PintuanOrder, on_delete=models.CASCADE)
    simple_order = models.OneToOneField(SimpleOrder, on_delete=models.CASCADE, verbose_name='订单')

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
