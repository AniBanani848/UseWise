from django.urls import path

from .views import add_item, add_review, item_detail, item_list

urlpatterns = [
    path('add/', add_item, name='add_item'),
    path('', item_list, name='item_list'),
    path('<int:item_id>/review/', add_review, name='add_review'),
    path('<int:item_id>/', item_detail, name='item_detail'),
]
