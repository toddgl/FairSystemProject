# payment/urls.py

from django.urls import path

from payment.views import (
    invoice_pdf_generation
)

app_name = 'payment'  # This is the namespace, so you can reverse urls with payment:*

urlpatterns = [
    path('payment/invoice/', invoice_pdf_generation, name='create-pdf-invoice'),
]
