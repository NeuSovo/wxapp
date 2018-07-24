from django.urls import path
from .views import  *

urlpatterns = [
    path('', GoodsListView.as_view()),
    path('<int:id>', GoodsDetailView.as_view()),
    path('category', all_category_view)
]