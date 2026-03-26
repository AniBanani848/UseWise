from django.urls import path
from .views import add_item, item_list, item_detail

urlpatterns = [
    path('add/', add_item, name='add_item'),
    path('', item_list, name='item_list'),
    path('<int:item_id>/', item_detail, name='item_detail'),
]