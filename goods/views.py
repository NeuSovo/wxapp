from django.shortcuts import render
from django.views.generic import DetailView, FormView, ListView
from dss.Mixin import (FormJsonResponseMixin, JsonResponseMixin,
                       MultipleJsonResponseMixin)

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
        if category:
            kwargs['goods__category_id'] =category
        if pintuan:
            kwargs['goods__pintuan__gte'] = 2
        if search:
            kwargs['goods__name__contains'] = search

        queryset = super(GoodsListView, self).get_queryset().filter(goods__goods_status=1)
        queryset = queryset.filter(**kwargs)
        return queryset


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

