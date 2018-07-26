from django.db import models

# Create your models here.
from user.models import User


class BaseOrder(models.Model):

    class Meta:
        abstract = True

    # [todo] 退款
    order_status_choices = (
        (-1, '取消'),
        (1, '待发货'),
        (2, '已发货'),
        (3, '已完成')
    )

    order_id = models.BigIntegerField(primary_key=True)
    create_time = models.DateTimeField(auto_now_add=True)
    create_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    order_status = models.IntegerField(choices=order_status_choices, default=1)

    total_price = models.DecimalField(max_digits=6, decimal_places=2)

    receive_name  = models.CharField(max_length=50)
    receive_phone  = models.CharField(max_length=50)
    receive_address  = models.CharField(max_length=100)

    order_remarks = models.TextField(null=True, blank=True)
    tracking_number = models.BigIntegerField(null=True, blank=True)
    done_time = models.DateTimeField(null=True, blank=True)


class SimpleOrder(BaseOrder):
    pass


class PinTuanOrder(BaseOrder):
    pass