# payment/admin.py
from django.contrib import admin
from .models import (
    Invoice,
    InvoiceItem,
    PaymentHistory,
    PaymentType
)
# Register your models here.
myModels = [ Invoice, InvoiceItem, PaymentHistory, PaymentType ]
# iterable list
admin.site.register(myModels)
