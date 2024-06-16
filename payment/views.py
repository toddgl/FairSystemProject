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
    DiscountItem
)

# Create your views here.

def invoice_pdf_generation(request, id, seq):
    invoice = get_object_or_404(Invoice, id=id, invoice_sequence=seq)
    invoice_items = InvoiceItem.objects.filter(invoice=id)
    profile = get_object_or_404(Profile, user=invoice.stallholder)
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
        'total_discount': total_discount,
        'profile': profile
    }
    html_template = get_template('invoice.html').render(context)
    pdf_file = HTML(string=html_template, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'filename="MB_Fair_Invoice.pdf"'
    return response