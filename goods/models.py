from django.db import models
from django.utils import timezone
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
        verbose_name = "商品"
        verbose_name_plural = "商品"
        ordering = ['-top', '-update_time', '-create_time']

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
    goods_cover = models.ImageField(upload_to="goodscover", verbose_name='商品封面', default='none')
    category = models.ForeignKey(CateGory, on_delete=models.SET_NULL, null=True, verbose_name='分类')
    origin_price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='原价')
    now_price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='现价')
    goods_status = models.IntegerField(verbose_name='商品状态', choices=goods_status_choices, default=1)
    inventory = models.IntegerField(verbose_name='库存', default=0)
    top = models.IntegerField(verbose_name='置顶方案', default=0, help_text='数字越大商品越靠前')
    goods_desc = models.TextField(null=True, blank=True, verbose_name='简单描述')

    def is_pintuan(self):
        pintuan = PinTuanGoods.objects.filter(goods=self)
        if pintuan.exists():
            pintuan = pintuan.get()
            return timezone.now() >= pintuan.begin_time and timezone.now() <= pintuan.end_time
        return False


class GoodsDetail(models.Model):

    class Meta:
        verbose_name = "GoodsDetail"
        verbose_name_plural = "GoodsDetails"

    def __str__(self):
        return str(self.goods)

    goods = models.OneToOneField(Goods, on_delete=models.CASCADE, primary_key=True)
    detail = RichTextField(verbose_name='介绍', default='无')


class GoodsProfile(models.Model):

    class Meta:
        verbose_name = "GoodsProfile"
        verbose_name_plural = "GoodsProfiles"
        ordering = ['goods']

    def __str__(self):
        return str(self.goods)

    goods = models.OneToOneField(Goods, on_delete=models.CASCADE, primary_key=True)
    sale_count = models.IntegerField(verbose_name='销售量', default=0)
    view_count = models.IntegerField(verbose_name='浏览量', default=0)
    love_count = models.IntegerField(verbose_name='点赞量', default=0)


class PinTuanGoods(models.Model):

    class Meta:
        verbose_name = "拼团商品"
        verbose_name_plural = "拼团商品"

    def __str__(self):
        return str(self.goods)

    goods = models.OneToOneField(Goods, verbose_name='商品', on_delete=models.CASCADE, primary_key=True, limit_choices_to={
                                 'goods_status': 1}, help_text='<h4>如果对于已经失效的拼团商品你想重新发起，<br>请直接调整失效拼团商品的开始时间和结束时间即可</h4>')
    pintuan_count = models.IntegerField(verbose_name='拼团人数', default=2)
    pintuan_price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='拼团价')
    effective = models.IntegerField(default=24, verbose_name='成团有效时间', help_text='单位是小时，成团必须在有效时间内达成拼团，否则拼团失败')
    begin_time = models.DateTimeField(default=timezone.now, verbose_name='开始时间')
    end_time = models.DateTimeField(default=timezone.now, verbose_name='结束时间')
    limit = models.IntegerField(verbose_name='限制购买数量', default=1, help_text='限制用户对此拼团商品的购买数量, 如果为0, 或者其他负数,则不限制')
