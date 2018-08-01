from django.contrib import admin

# Register your models here.
from .models import *


class SimpleOrderDetail(admin.TabularInline):
    model = SimpleOrderDetail
    extra = 2
    can_delete = False

    def get_max_num(self, request, obj=None, **kwargs):
        """Hook for customizing the max number of extra inline forms."""
        if obj:
            if obj.order_type == 1:
                return 1
        return self.max_num

class PinTuanDetail(admin.StackedInline):
    model = PinTuan
    extra = 2
    can_delete = False

    def get_extra(self, request, obj=None, **kwargs):
        """Hook for customizing the number of extra inline forms."""
        if obj:
            return obj.pintuan_goods.pintuan_count - obj.pintuan_set.count()
        return self.extra

    def get_max_num(self, request, obj=None, **kwargs):
        """Hook for customizing the max number of extra inline forms."""
        if obj:
            return obj.pintuan_goods.pintuan_count


@admin.register(SimpleOrder)
class SimpleOrderAdmin(admin.ModelAdmin):
    '''
        Admin View for SimpleOrder
    '''
    list_display = ('order_id', 'order_type', 'order_status', 'create_time', 'create_user')
    list_filter = ('order_type', 'order_status', 'create_time')
    inlines = [
        SimpleOrderDetail,
    ]
    # raw_id_fields = ('',)
    readonly_fields = ('order_id', 'done_time', 'create_time', 'transaction_id', 'pay_time')
    # search_fields = ('',)

@admin.register(PintuanOrder)
class PintuanOrderAdmin(admin.ModelAdmin):
    '''
        Admin View for PintuanOrder
    '''

    def get_pintuan_status(self, obj):
        status, msg = obj.is_effective()
        return msg
    get_pintuan_status.short_description = '拼团状态'

    list_display = ('pintuan_id', 'pintuan_goods', 'get_pintuan_status')
    list_filter = ('pintuan_goods', )
    inlines = [
        PinTuanDetail,
    ]
    # raw_id_fields = ('',)
    readonly_fields = ('pintuan_id', 'create_time', 'done_time', 'expire_time')
    # search_fields = ('',)
