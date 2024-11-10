# payment/urls.py

from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from payment.views import (
    invoice_pdf_generation,
    payment_cancelled,
    payment_successful,
    stripe_payment,
    stripe_webhook,
    payment_dashboard_view,
    paymenthistory_listview,
    mark_payment_as_cancelled,
    mark_payment_as_reconciled,
    load_update_form,
    update_payment_history
)

app_name = 'payment'  # This is the namespace, so you can reverse urls with payment:*

urlpatterns = [
    path('payment/invoice/<int:id>/<int:seq>/', invoice_pdf_generation, name='create-pdf-invoice'),
    path('payment/cancelled/<int:id>', mark_payment_as_cancelled, name='mark-as-cancelled'),
    path('payment/rejected/<int:id>', mark_payment_as_reconciled, name='mark-as-reconciled'),
    path('payment/payment_successful/',payment_successful, name='payment-successful'),
    path('payment/payment_cancelled/', payment_cancelled, name='payment-cancelled'),
    path('payment/list/', paymenthistory_listview, name='payment-list'),
    path('payment/stripe_payment/<int:id>/', stripe_payment, name='stripe-payment'),
    path('payment/stripe_webhook/', csrf_exempt(stripe_webhook), name='stripe-webhook'),
    path('dashboard/payments/', payment_dashboard_view, name='payment-dashboard'),
    path('payment/payment_update/<int:id>', update_payment_history, name='payment-update'),
    path('payment/load_update_form/<int:id>/', load_update_form, name='load-update-form')
]
