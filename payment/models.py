#payment/models.py

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from fairs.models import (
    InventoryItem
)
from registration.models import (
    StallRegistration
)


# Create your models here.

class PaymentType(models.Model):
    """
    Description: a reference table for storing the different payment types which will be referenced in payment history
    """
    payment_type_name = models.CharField(max_length=40)

    def __str__(self):
        return self.payment_type_name

    class Meta:
        verbose_name_plural = "paymenttypenames"

class Invoice(models.Model):
    """
    Description: A model for recording invoicing for stall registrations
    """
    stall_registration = models.ForeignKey(StallRegistration, on_delete=models.CASCADE)
    stallholder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    total_cost = models.DecimalField(max_digits=8, decimal_places=2)
    gst_value = models.DecimalField(max_digits=8, decimal_places=2)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "invoice"
        verbose_name_plural = "invoices"

class PaymentHistory (models.Model):
    """
    Description: A model that records stallholder payment history includes credits as well as payment
    """
    PENDING = "P"
    COMPLETED = "C"
    FAILED = "F"

    STATUS_CHOICES = (
        (PENDING, _("pending")),
        (COMPLETED, _("completed")),
        (FAILED, _("failed")),
    )
    invoice_number = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2)
    payment_status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default=PENDING
    )
    payment_type = models.ForeignKey(PaymentType, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "payment"
        verbose_name_plural = "payments"


class IvoiceItem(models.Model):
    """
    Description: A model that provides the detail of the items that make up  each invoice
    """
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    item_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(9999), ], )
    item_cost = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        verbose_name = "invoiceitem"
        verbose_name_plural = "invoiceitems"
