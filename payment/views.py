from django.shortcuts import render
from payment.models import (
    Invoice,
)

# Create your views here.

def calc_total_cost(request, id):

    return total_cost
def create_invoice(request, id, stallholder_id):
    invoice, created = Invoice.objects.update_or_create(
        registration = id,
        stallholder = stallholder_id,
        defaults = {
            "total_cost" : calc_total_cost,

        }

    )