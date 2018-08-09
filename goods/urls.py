from django.urls import path

from .views import *

urlpatterns = [
    path('', GoodsListView.as_view()),
    path('<int:goods_id>', GoodsDetailView.as_view()),
    path('love/<int:goods_id>', LoveGoodsView.as_view()),
    path('category', all_category_view)
]
