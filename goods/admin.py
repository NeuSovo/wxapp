from django.utils import timezone
from django.contrib import admin

# Register your models here.
from .models import *

class GoodsProfileAdmin(admin.StackedInline):
    model = GoodsProfile
    readonly_fields = ('sale_count', 'view_count', 'love_count')


class GoodsDetailAdmin(admin.StackedInline):
    model = GoodsDetail


@admin.register(Goods)
class GoodsAdmin(admin.ModelAdmin):
    '''
        Admin View for Goods
    '''
    list_display = ('id', 'name', 'category', 'now_price', 'top', 'goods_status')
    list_filter = ('category', 'create_time', 'goods_status')
    search_fields = ('name',)
    readonly_fields = ('create_time', 'update_time',)

    inlines = [
        GoodsDetailAdmin,
        GoodsProfileAdmin
    ]

    def save_model(self, request, obj, form, change):
        obj.save()
        if not change:
            GoodsProfile.objects.create(goods=obj)


class PinTuanStatusFilter(admin.SimpleListFilter):
    title = (u'拼团状态')
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            (0, u'未开始'),
            (1, u'拼团中'),
            (2, u'已结束'),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            if int(self.value()) == 0:
                return queryset.filter(begin_time__gt=timezone.now())
            if int(self.value()) == 1:
                return queryset.filter(begin_time__lte=timezone.now(), end_time__gte=timezone.now())
            if int(self.value()) == 2:
                return queryset.filter(end_time__lte=timezone.now())


@admin.register(PinTuanGoods)
class PinTuanGoodsAdmin(admin.ModelAdmin):
    '''
        Admin View for PinTuanGoods
    '''

    def get_pintuan_count(self, obj):
        return str(obj.pintuan_count) + '人团'

    def get_pintuan_price(self, obj):
        return str(obj.pintuan_price) + ' / ' + str(obj.goods.now_price)

    def get_pintuan_status(self, obj):
        if timezone.now() < obj.begin_time:
            return u'未开始'

        if timezone.now() >= obj.begin_time and timezone.now() <= obj.end_time:
            return u'拼团中'

        if timezone.now() > obj.end_time:
            return u'已结束'

    get_pintuan_price.short_description = u'拼团价 / 原价'
    get_pintuan_count.short_description = u'拼团人数'
    get_pintuan_status.short_description = u'拼团状态'
    list_display = ('goods', 'get_pintuan_count', 'get_pintuan_price', 'get_pintuan_status')
    list_filter = (PinTuanStatusFilter,)
    # inlines = [
    #     Inline,
    # ]
    # raw_id_fields = ('',)
    # readonly_fields = ('',)
    # search_fields = ('',)

admin.site.register(CateGory)