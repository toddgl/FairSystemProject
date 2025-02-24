# payment/admin.py
from django.contrib import admin
from stripe import Discount

from .models import (
    Invoice,
    InvoiceItem,
    PaymentHistory,
    PaymentType, DiscountItem
)
# Register your models here.
myModels = [ DiscountItem, InvoiceItem, PaymentHistory, PaymentType ]
# iterable list
admin.site.register(myModels)
