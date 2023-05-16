# registration/urls.py
from django.urls import path, include

from registration.views import (
    FoodPrepEquipmentListView,
    FoodPrepEquipmentCreateView,
    FoodPrepEquipmentDetailUpdateView,
    FoodSaleTypeListView,
    FoodSaleTypeCreateView,
    FoodSaleTypeDetailUpdateView,
    StallCategoryListView,
    StallCategoryCreateView,
    StallCategoryDetailUpdateView,
    stall_registration_listview,
    stall_registration_create,
    stall_registration_update_view,
    food_registration_create,
    display_food_equipment,
    equipment_list,
    add_equipment,
    remove_equipment,
    edit_equipment,
    myfair_dashboard_view,
    archive_comments,
    comments_view_add,
)

app_name = 'registration'

urlpatterns = [
    path('',
         include('django.contrib.auth.urls')),  # v1
    path('stallregistration/list/', stall_registration_listview, name='stallregistration-list'),
    path('foodprepequipment/', FoodPrepEquipmentListView.as_view(), name='foodprepequipment-list'),
    path('foodprepequipment/,<int:pk>', FoodPrepEquipmentDetailUpdateView.as_view(), name='foodprepequipment-detail'),
    path('foodprepequipment/actionUrl/', FoodPrepEquipmentCreateView.as_view(), name='actionUrl'),
    path('foodsaletype/', FoodSaleTypeListView.as_view(), name='foodsaletype-list'),
    path('foodsaletype/,<int:pk>', FoodSaleTypeDetailUpdateView.as_view(), name='foodsaletype-detail'),
    path('foodsaletype/actionUrl/', FoodSaleTypeCreateView.as_view(), name='actionUrl'),
    path('stallcategory/', StallCategoryListView.as_view(), name='stallcategory-list'),
    path('stallcategory/,<int:pk>', StallCategoryDetailUpdateView.as_view(), name='stallcategory-detail'),
    path('stallcategory/actionUrl/', StallCategoryCreateView.as_view(), name='actionUrl'),
    path('stallregistration/create/', stall_registration_create, name='stallregistration-create'),
    path('stallregistration/create/comments/', comments_view_add, name='stallregistration-comments'),
    path('stallregistration/,<int:pk>/', stall_registration_update_view, name='stallregistration-detail'),
    path('myfair/', myfair_dashboard_view, name='stallregistration-dashboard'),
    path('myfair/comments/', comments_view_add, name='stallregistration-comments'),
    path('foodregistration/,<int:pk>/',food_registration_create, name='food-registration'),
    path('foodequipment/', display_food_equipment, name='food-equipment'),
    path('foodequipment/list', equipment_list, name='equipment-list'),
    path('foodequipment/add', add_equipment, name='add-equipment'),
    path('foodequipment/<int:pk>/remove', remove_equipment, name='remove_equipment'),
    path('foodequipment/<int:pk>/edit', edit_equipment, name='edit_equipment'),
    path('registration/comment/<int:pk>/',  archive_comments, name='archive'),
]
