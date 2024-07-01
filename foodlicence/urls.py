# foodlicence/urls.py

from django.urls import path

from foodlicence.views import (
    generate_combined_pdf,
    add_licence_to_batch
)

app_name = 'foodlicence'  # This is the namespace, so you can reverse urls with payment:*

urlpatterns = [
    path('foodlicence/batch/<int:id>', add_licence_to_batch, name='add-to-batch'),
]
