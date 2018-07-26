from django.contrib import admin

# Register your models here.
from .models import *


@admin.register(SimpleOrder)
class SimpleOrderAdmin(admin.ModelAdmin):
    '''
        Admin View for SimpleOrder
    '''
    list_display = ('order_id', 'order_type', 'order_status', 'create_time', 'create_user')
    list_filter = ('order_type', 'order_status', 'create_time')
    # inlines = [
    #     Inline,
    # ]
    # raw_id_fields = ('',)
    readonly_fields = ('order_id', 'done_time', 'create_time')
    # search_fields = ('',)

@admin.register(PintuanOrder)
class PintuanOrderAdmin(admin.ModelAdmin):
    '''
        Admin View for PintuanOrder
    '''
    list_display = ('pintuan_id', 'pintuan_goods')
    # list_filter = ('',)
    # inlines = [
    #     Inline,
    # ]
    # raw_id_fields = ('',)
    readonly_fields = ('pintuan_id',)
    # search_fields = ('',)

admin.site.register(PinTuan)