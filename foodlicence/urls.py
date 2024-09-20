# foodlicence/urls.py

from django.urls import path

from foodlicence.views import (
    generate_combined_pdf,
    foodlicence_listview,
    foodlicence_batch_listview,
    mark_licence_as_staged,
    mark_licence_as_batched,
    mark_licence_as_submitted,
    mark_licence_as_approved,
    mark_licence_as_rejected,
    foodlicence_dashboard_view,
    create_food_licence_from_stallregistration,
    create_food_licence_if_eligible
)

app_name = 'foodlicence'  # This is the namespace, so you can reverse urls with payment:*

urlpatterns = [
    path('foodlicence/batch/<int:id>', mark_licence_as_staged, name='mark-as-staged'),
    path('foodlicence/batch/<int:id>', mark_licence_as_batched, name='mark-as-batched'),
    path('foodlicence/batch/<int:id>', mark_licence_as_submitted, name='mark-as-submitted'),
    path('foodlicence/completed/<int:id>', mark_licence_as_approved, name='mark-as-approved'),
    path('foodlicence/rejected/<int:id>', mark_licence_as_rejected, name='mark-as-rejected'),
    path('foodlicence/list/', foodlicence_listview, name='foodlicence-list'),
    path('foodlicencebatch/list/', foodlicence_batch_listview, name='foodlicence-batch-list'),
    path('foodlicence/batch/', generate_combined_pdf, name='licence-batch-generate'),
    path('dashboard/foodlicences/', foodlicence_dashboard_view, name='foodlicence-dashboard'),
    path('foodlicence/create/<int:stallregistration_id>/', create_food_licence_from_stallregistration,
         name='foodlicence-create'),
    path('foodlicence/create/', create_food_licence_if_eligible,
         name='foodlicence-mass-create'),
]
