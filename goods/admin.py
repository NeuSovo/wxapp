from django.contrib import admin

# Register your models here.
from .models import *

class GoodsDetailAdmin(admin.StackedInline):
    model = GoodsDetail


@admin.register(Goods)
class GoodsAdmin(admin.ModelAdmin):
    '''
        Admin View for Goods
    '''
    list_display = ('id', 'name', 'category', 'now_price', 'top', )
    list_filter = ('category', 'top', 'create_time')
    search_fields = ('name',)
    readonly_fields = ('create_time', 'update_time',)

    inlines = [
        GoodsDetailAdmin,
    ]

    def save_model(self, request, obj, form, change):
        obj.save()
        if not change:
            GoodsProfile.objects.create(goods=obj)

admin.site.register(CateGory)
