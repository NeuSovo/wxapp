from django.utils import timezone
from celery.decorators import task

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
def test_task(self, info="test"):
    return str(timezone.now())