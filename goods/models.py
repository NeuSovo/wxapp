from django.db import models
from simditor.fields import RichTextField
# Create your models here.

class CateGory(models.Model):

    class Meta:
        verbose_name = "CateGory"
        verbose_name_plural = "CateGorys"

    def __str__(self):
        return self.category_name
    
    category_name = models.CharField(max_length=50)


# inventory 库存
class Goods(models.Model):

    class Meta:
        verbose_name = "Goods"
        verbose_name_plural = "Goodss"
        ordering = ['top','-update_time', '-create_time']

    goods_status_choices = (
        (0, '下架'),
        (1, '在售')
    )
    top_choices = (
        (0, '店长推荐'),
        (1, '荐'),
        (2, '普通')
    )

    def __str__(self):
        return self.name

    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    name = models.CharField(max_length=120, verbose_name='商品名字')
    category = models.ForeignKey(CateGory, on_delete=models.SET_NULL, null=True, verbose_name='分类')
    origin_price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='原价')
    now_price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='现价')
    goods_status = models.IntegerField(verbose_name='商品状态', choices=goods_status_choices, default=1)
    inventory = models.IntegerField(verbose_name='库存', default=0)
    top = models.IntegerField(verbose_name='置顶方案', choices=top_choices,default=2)

    pintuan = models.IntegerField(verbose_name='拼团人数', default=1, help_text='默认为1,即不参与拼团，<br>设置为几，即为几人团 。<br> 如设为3，则为三人团')
    pintuan_price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='拼团价', help_text='如果拼团人数为1 此项无效', null=True, blank=True)
    goods_desc = models.TextField(null=True, blank=True, verbose_name='简单描述')


class GoodsDetail(models.Model):

    class Meta:
        verbose_name = "GoodsDetail"
        verbose_name_plural = "GoodsDetails"

    def __str__(self):
        return str(self.goods)

    goods = models.OneToOneField(Goods, on_delete=models.CASCADE)
    detail = RichTextField(verbose_name='介绍', default='无')


class GoodsProfile(models.Model):

    class Meta:
        verbose_name = "GoodsProfile"
        verbose_name_plural = "GoodsProfiles"
        ordering = ['goods']

    def __str__(self):
        return str(self.goods)

    goods = models.OneToOneField(Goods, on_delete=models.CASCADE)
    sale_count = models.IntegerField(verbose_name='销售量', default=0)
    view_count = models.IntegerField(verbose_name='浏览量', default=0)
    love_count = models.IntegerField(verbose_name='点赞量', default=0)
