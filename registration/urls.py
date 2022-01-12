# registration/urls.py
from django.urls import path, include
from django.views.generic.base import TemplateView  # v1

from registration.views import (
    FoodPrepEquipmentListView,
    FoodPrepEquipmentCreateView,
    FoodPrepEquipmentDetailUpdateView,
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

]
