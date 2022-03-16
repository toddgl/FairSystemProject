# registration/urls.py
from django.urls import path, include
from django.views.generic.base import TemplateView  # v1

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
    stall_registration_view,
    find_second_eventsite,
    food_registration,
    display_food_equipment,
    equipment_list,
    add_equipment,
    remove_equipment,
    edit_equipment,
)

app_name = 'registration'

urlpatterns = [
    path('',
         include('django.contrib.auth.urls')),  # v1
    path('',
         TemplateView.as_view(template_name='registration/registration.html'),
         name='registration'),  # v1
    path('foodprepequipment/', FoodPrepEquipmentListView.as_view(), name='foodprepequipment-list'),
    path('foodprepequipment/,<int:pk>', FoodPrepEquipmentDetailUpdateView.as_view(), name='foodprepequipment-detail'),
    path('foodprepequipment/actionUrl/', FoodPrepEquipmentCreateView.as_view(), name='actionUrl'),
    path('foodsaletype/', FoodSaleTypeListView.as_view(), name='foodsaletype-list'),
    path('foodsaletype/,<int:pk>', FoodSaleTypeDetailUpdateView.as_view(), name='foodsaletype-detail'),
    path('foodsaletype/actionUrl/', FoodSaleTypeCreateView.as_view(), name='actionUrl'),
    path('stallcategory/', StallCategoryListView.as_view(), name='stallcategory-list'),
    path('stallcategory/,<int:pk>', StallCategoryDetailUpdateView.as_view(), name='stallcategory-detail'),
    path('stallcategory/actionUrl/', StallCategoryCreateView.as_view(), name='actionUrl'),
    path('stallregistration/', stall_registration_view, name='stallregistration-detail'),
    path('foodregistration',food_registration, name='food_registration'),
    path('foodequipment/', display_food_equipment, name='food-equipment'),
    path('foodequipment/list', equipment_list, name='equipment-list'),
    path('foodequipment/add', add_equipment, name='add-equipment'),
    path('foodequipment/<int:pk>/remove', remove_equipment, name='remove_equipment'),
    path('foodequipment/<int:pk>/edit', edit_equipment, name='edit_equipment'),
]

htmx_views = [
    path('stallregistration/find-second-eventsite/', find_second_eventsite, name='find-second-eventsite'),
]

urlpatterns += htmx_views
