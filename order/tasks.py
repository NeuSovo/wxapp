from django.utils import timezone
from celery.decorators import task

from .models import *

"""
异步定时任务，来处理过期无效拼团订单
example:
    test_task.apply_async((args,), eta=datetime.now() + timedelta(days=1))
    test_task.apply_async((args,), expires=datetime.now() + timedelta(days=1))
设计：
    每生成一个团购订单，将其id作为参数，注册任务，
    检测出是否过期，并且是否失效。
    注册另一个task，并且更新订单状态，通知用户，等一系列操作，

[TODO]: RETRY , Error handle
"""

@task
def update_order_status(order_id):
    try:
        order = SimpleOrder.objects.get(order_id=order_id)
    except Exception as e:
        raise ValueError

    order.order_status = -1 
    # [TODO] 退款，发通知，等
    # do something

    order.save()


@task
def expire_pt_task(pt_id = None):
    try:
        pt = PintuanOrder.objects.get(pintuan_id=pt_id)
    except Exception as e:
        return {'msg': 'error', 'id': pt_id}

    if timezone.now() >= pt.expire_time and pt.done_time == None:
        for i in pt.pintuan_set.all():
            update_order_status.delay(order_id=i.simple_order_id)
        return {'msg': 'ok', 'id': pt_id}
