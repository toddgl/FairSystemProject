# foodlicence/urls.py

from django.urls import path

from foodlicence.views import (
    generate_combined_pdf,
    add_licence_to_batch,
    foodlicence_listview,
    foodlicence_batch_listview,
    foodlicence_batch_update,
    mark_licence_as_complete,
    mark_licence_as_rejected,
    foodlicence_dashboard_view
)

app_name = 'foodlicence'  # This is the namespace, so you can reverse urls with payment:*

urlpatterns = [
    path('foodlicence/batch/<int:id>', add_licence_to_batch, name='add-to-batch'),
    path('foodlicence/completed/<int:id>', mark_licence_as_complete, name='mark-as-complete'),
    path('foodlicence/rejected/<int:id>', mark_licence_as_rejected, name='mark-as-rejected'),
    path('foodlicence/list/', foodlicence_listview, name='foodlicence-list'),
    path('foodlicencebatch/list/', foodlicence_batch_listview, name='foodlicence-batch-list'),
    path('foodlicence/batch/', generate_combined_pdf, name='licence-batch-generate'),
    path('foodlicence/batch/<int:id>', foodlicence_batch_update, name='licence-batch-update'),
    path('dashboard/foodlicences/', foodlicence_dashboard_view, name='foodlicence-dashboard'),
]
