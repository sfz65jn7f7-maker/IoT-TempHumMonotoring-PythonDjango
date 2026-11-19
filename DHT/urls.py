from django.urls import path
from .views import Dlist, Dhtviews, test, dashboard

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('test/', test, name='test'),
    path('api/get/', Dlist, name='Dlist'),
    path('api/post/', Dhtviews.as_view(), name='Dhtviews'),
]