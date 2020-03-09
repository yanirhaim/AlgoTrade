from django.urls import path
from .views import index, about, my_stocks, delete, stock, stock_s

urlpatterns = [
    path('', index, name='home'),
    path('about/', about, name='about'),
    path('my_stocks/', my_stocks, name='my_stocks'),
    path('delete/<stock_id>', delete, name='delete'),
    path('stock/<str:stock_id>/', stock, name='stock'),
    path(r'^stock/$', stock_s, name='search'),
]
