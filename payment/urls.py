# payment/urls.py

from django.urls import path

from payment.views import (
    invoice_pdf_generation,
    payment_cancelled,
    payment_successful,
    stripe_payment,
    stripe_webhook
)

app_name = 'payment'  # This is the namespace, so you can reverse urls with payment:*

urlpatterns = [
    path('payment/invoice/<int:id>/<int:seq>/', invoice_pdf_generation, name='create-pdf-invoice'),
    path('payment/payment_successful/',payment_successful, name='payment-successful'),
    path('payment/payment_cancelled/', payment_cancelled, name='payment-cancelled'),
    path('payment/stripe_payment/<int:id>/', stripe_payment, name='stripe-payment'),
    path('payment/stripe_webhook/', stripe_webhook, name='stripe-webhook')
]
