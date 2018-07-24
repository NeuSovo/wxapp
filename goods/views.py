from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import DetailView, FormView, ListView
from dss.Mixin import (FormJsonResponseMixin, JsonResponseMixin,
                       MultipleJsonResponseMixin)
from dss.Serializer import serializer

from .models import *
# Create your views here.


class GoodsListView(MultipleJsonResponseMixin, ListView):
    model = GoodsProfile
    paginate_by = 15
    foreign = True

    exclude_attr = ('id',)

    def get_queryset(self):
        kwargs = {
        }
        
        category = self.request.GET.get('category', None)
        pintuan = True if int(self.request.GET.get('pintuan') or 0) else False
        search = self.request.GET.get('search', None)
        ordering = self.request.GET.get('order', None) # view, sale, love
        ordertype = int(self.request.GET.get('ordertype') or 0) # 0  desc 1 or other asc

        if category:
            kwargs['goods__category_id'] = category
        if pintuan:
            kwargs['goods__pintuan__gte'] = 2
        if search:
            kwargs['goods__name__contains'] = search

        queryset = super(GoodsListView, self).get_queryset().filter(goods__goods_status=1, **kwargs)
        ordering = self.get_order_param(ordering)
        if ordering:
            ordering = ordering if ordertype else '-' + ordering
            queryset = queryset.order_by(ordering)
            print (queryset.query)
        return queryset

    def get_order_param(self, ordering):
        if ordering in ['view', 'sale', 'love']:
            return '{}_count'.format(ordering)
        elif ordering in ['create_time', 'now_price', 'pintuan_price']:
            return 'goods__' + ordering

        return None


class GoodsDetailView(JsonResponseMixin, DetailView):
    model = GoodsDetail
    foreign = True
    many = True
    datetime_type = 'string'
    pk_url_kwarg = 'id'
    exclude_attr = ('id',)

    def get_context_data(self, **kwargs):
        context = super(GoodsDetailView, self).get_context_data(**kwargs)
        context['count'] = {
            'sale_count': self.object.goods.goodsprofile.sale_count,
            'view_count': self.object.goods.goodsprofile.view_count,
            'love_count': self.object.goods.goodsprofile.love_count
        }
        return context


def all_category_view(request):
    all_cate = CateGory.objects.all()
    return JsonResponse({'lists': serializer(all_cate)})
