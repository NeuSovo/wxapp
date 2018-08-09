from django.urls import path

from .views import *

urlpatterns = [
    path('reg', RegUserView.as_view()),
    path('login', LoginUserView.as_view()),
    path('order', UserOrderView.as_view()),
    path('pt', PinTuanOrderView.as_view())
]
