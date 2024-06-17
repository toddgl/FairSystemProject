# payment/views.py

import logging
import decimal
from weasyprint import HTML, CSS
from django.template.loader import get_template
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from accounts.models import Profile
from .models import (
    Invoice,
    InvoiceItem,
    DiscountItem,
    PaymentHistory,
)

# Create your views here.

def invoice_pdf_generation(request, id, seq):
    invoice = get_object_or_404(Invoice, id=id, invoice_sequence=seq)
    invoice_items = InvoiceItem.objects.filter(invoice=id)
    profile = get_object_or_404(Profile, user=invoice.stallholder)
    payments = PaymentHistory.paymenthistorycurrentmgr.get_registration_payment_history(invoice.stall_registration)
    # Determine if there are any payments, if so sum them and add it to the context
    if payments:
        total_payments = payments.amount_paid
    else:
        total_payments = decimal.Decimal(0.00)
    # Determine if there are any discounts, if so sum them and add it to the context
    discounts = DiscountItem.objects.filter(stall_registration=invoice.stall_registration)
    if discounts:
        total_discount = sum(discounts.values_list('discount_amount', flat=True))
    else:
        total_discount =  decimal.Decimal(0.00)
    # Render the template with the context
    context = {
        'invoice': invoice,
        'invoice_items': invoice_items,
        'total_payments': total_payments,
        'total_discount': total_discount,
        'profile': profile
    }
    html_template = get_template('invoice.html').render(context)
    pdf_file = HTML(string=html_template, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'filename="MB_Fair_Invoice.pdf"'
    return response