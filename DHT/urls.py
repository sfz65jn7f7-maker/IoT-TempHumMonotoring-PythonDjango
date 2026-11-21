from django.urls import path
from .views import (Dlist, Dhtviews, test, dashboard,
                    temperature_page, humidite_page, incidents_page)

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('temperature/', temperature_page, name='temperature'),
    path('humidite/', humidite_page, name='humidite'),
    path('incidents/', incidents_page, name='incidents'),
    path('test/', test, name='test'),
    path('api/get/', Dlist, name='Dlist'),
    path('api/post/', Dhtviews.as_view(), name='Dhtviews'),
]