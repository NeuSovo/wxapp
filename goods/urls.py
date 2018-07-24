from django.urls import path
from .views import  *

urlpatterns = [
    path('', GoodsListView.as_view()),
    path('<str:id>', GoodsDetailView.as_view())
]