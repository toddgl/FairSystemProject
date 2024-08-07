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
    stall_registration_cancel_view,
    stall_registration_update_view,
    food_registration_create_view,
    convener_stall_registration_detail_view,
    stallholder_stall_registration_detail_view,
    display_food_equipment,
    equipment_list,
    add_food_prep_equipment,
    remove_equipment,
    add_site_requirement,
    remove_site_requirement,
    myfair_dashboard_view,
    archive_comments,
    comments_view_add,
    submit_stall_registration,
    invoice_stall_registration,
    reinvoice_stall_registration,
    transition_booking_status,
)

app_name = 'registration'

urlpatterns = [
    path('',
         include('django.contrib.auth.urls')),  # v1
    path('stallregistration/list/', stall_registration_listview, name='stallregistration-list'),
    path('stallregistration/convener/details/,<int:id>', convener_stall_registration_detail_view, name='convener-stall-food-registration-detail'),
    path('stallregistration/stallholder/details/,<int:id>', stallholder_stall_registration_detail_view, name='stallholder-stall-food-registration-detail'),
    path('stallregistration/cancel/.<int:pk>', stall_registration_cancel_view, name='stallregistration-cancel'),
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
    path('stallregistration/create/comments/<int:stallholder_id>/', comments_view_add, name='stallregistration-comments'),
    path('stallregistration/,<int:pk>/', stall_registration_update_view, name='stallregistration-detail'),
    path('stallregistration/submit/<int:id>/', submit_stall_registration, name='stallregistration-submit'),
    path('stallregistration/invoice/<int:id>/', invoice_stall_registration, name='stallregistration-invoice'),
    path('stallregistration/reinvoice/<int:id>/', reinvoice_stall_registration, name='stallregistration-reinvoice'),
    path('siterequirement/add/,<int:pk>', add_site_requirement, name='add-site-requirement'),
    path('stallregistration/remove/<int:parent_id>/<int:id>/', remove_site_requirement, name='remove-site'),
    path('myfair/', myfair_dashboard_view, name='stallregistration-dashboard'),
    path('myfair/comments/', comments_view_add, name='stallregistration-comments'),
    path('foodregistration/,<int:pk>/',food_registration_create_view, name='food-registration'),
    path('foodequipment/', display_food_equipment, name='food-equipment'),
    path('foodequipment/list', equipment_list, name='equipment-list'),
    path('foodequipment/add', add_food_prep_equipment, name='add-food-prep-equipment'),
    path('foodequipment/remove/<int:parent_id>/<int:id>/', remove_equipment, name='remove-equipment'),
    path('registration/comment/<int:pk>/',  archive_comments, name='archive'),
    path('stall/transition/<int:stall_registration_id>/<str:target_status>/', transition_booking_status, name='transition_booking_status'),
]
