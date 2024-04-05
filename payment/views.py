# payment/views.py

import logging
from weasyprint import HTML, CSS
from django.template.loader import get_template
from django.http import HttpResponse
from .models import (
    Invoice,
    InvoiceItem
)

# Create your views here.

def invoice_pdf_generation(request, id, seq):
    invoice = Invoice.objects.get(id=id, invoice_sequence=seq)
    invoice_items = InvoiceItem.objects.filter(invoice=id)
    print(id, seq, invoice.total_cost)
    html_template = get_template('invoice.html').render()
    pdf_file = HTML(string=html_template, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'filename="MB_Fair_Invoice.pdf"'
    return response