from celery.decorators import task
from django.utils import timezone

from order import models


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
        order = models.SimpleOrder.objects.get(order_id=order_id)
    except Exception as e:
        raise ValueError
    if order.order_status != -1:
        order.refund()
    return order_id


@task
def expire_pt_task(pt_id=None):
    try:
        pt = models.PintuanOrder.objects.get(pintuan_id=pt_id)
    except Exception as e:
        return {'msg': 'error', 'id': pt_id, "info": str(e)}

    if timezone.now() >= pt.expire_time and pt.done_time == None:
        for i in pt.pintuan_set.all():
            update_order_status.delay(order_id=i.simple_order_id)
        return {'msg': 'ok', 'id': pt_id}


@task
def delete_unpay_order(order_id=None):
    # 如果15分钟内未收到微信通知，则[删除]此笔未支付订单
    #
    delete = {}
    try:
        order = models.SimpleOrder.objects.get(order_id=order_id)
    except Exception as e:
        raise {'msg': 'order not exists', 'order_id': order_id}

    if order.order_status != 0:
        return
    if order.order_type == 1:
        # 测试，如果是拼团的删除拼团单
        if order.pintuan.pintuan_order.create_user_id == order.create_user_id:
            order.pintuan.pintuan_order.delete()

    delete = order.delete()
    return {'msg': 'ok', 'delete': delete}
