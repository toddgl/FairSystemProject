#payment/models.py

import decimal
import logging
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django_fsm import FSMField, transition

from fairs.models import (
    InventoryItem,
    InventoryItemFair
)
from registration.models import (
    StallRegistration,
    AdditionalSiteRequirement
)

db_logger = logging.getLogger('db')

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

class InvoiceManager(models.Manager):

    def get_invoices(self, registration_id):
        return super().get_queryset().filter(registration=registration_id)

class Invoice(models.Model):
    """
    Description: A model for recording invoicing for stall registrations
    """
    stall_registration = models.ForeignKey(StallRegistration, on_delete=models.CASCADE)
    stallholder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    total_cost = models.DecimalField(blank=True, null=True,max_digits=8, decimal_places=2)
    gst_value = models.DecimalField(blank=True, null=True,max_digits=8, decimal_places=2)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "invoice"
        verbose_name_plural = "invoices"

class PaymentHistoryManager(models.Manager):
    """
    Used to create a PaymentHistory object when an invoice is initially created
    Parameters:
        invoice - invoive instance
        amount_to_pay - tatal amoun topay from the invoice
    Output:
        the created object
    """
    def create_paymenthistory(self, invoice, amount_to_pay):
        obj = PaymentHistory.objects.create(invoice=invoice, amount_to_pay=amount_to_pay)
        return obj


class PaymentHistory (models.Model):
    """
    Description: A model that records stallholder payment history includes credits as well as payment
    """
    PENDING = "Pending"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"
    FAILED = "Failed"
    RECONCILED = "Reconciled"

    PAYMENT_STATUS_CHOICES = [
        (PENDING, _("pending")),
        (CANCELLED, _("cancelled")),
        (COMPLETED, _("completed")),
        (FAILED, _("failed")),
        (RECONCILED, _("reconciled")),
    ]
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    amount_to_pay = models.DecimalField(default=0.00, max_digits=8, decimal_places=2)
    amount_paid = models.DecimalField(null=True, blank=True, max_digits=8, decimal_places=2)
    payment_status = FSMField(
        default=PENDING,
        verbose_name='Payment State',
        choices=PAYMENT_STATUS_CHOICES,
        protected=False,
    )
    payment_type = models.ForeignKey(
        PaymentType,
        on_delete=models.CASCADE,
        null=True
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    paymenthistorymgr = PaymentHistoryManager()


    class Meta:
        verbose_name = "payment"
        verbose_name_plural = "payments"

    @transition(field=payment_status, source="Pending", target="Cancelled")
    def to_payment_status_cancelled(self):
        pass

    @transition(field=payment_status, source="Pending", target="Failed")
    def to_payment_status_failed(self):
        pass

    @transition(field=payment_status, source="Pending", target="Completed")
    def to_payment_status_completed(self):
        pass

    @transition(field=payment_status, source="Completed", target="Reconciled")
    def to_payment_status_reconciled(self):
        pass


class InvoiceItemManager(models.Manager):

    def create_invoice_items(self, registration ):
        """
        Cycle through the billable items on the stall registration instance and create an invoice and invoice item
        for each of teh billable items on the stall registration record

        Parameters:
        - registration: The instance of the StallRegistration.
        - field_list: A list of field names to iterate through.
        - action: A function representing the action to be performed on each field.
        """
        fields_to_check = ['stall_category','site_size','trestle_quantity', 'vehicle_length', 'power_required', 'multi_site' ]
        invoice = Invoice.objects.get_or_create(
            stall_registration = registration,
            stallholder_id = registration.stallholder.id,
        )
        total_cost = decimal.Decimal(0.00)
        for field_name in fields_to_check:
            field_value = getattr(registration, field_name, None)
            if field_value is not None:
                print(registration, field_name, field_value)
                if(field_name == 'stall_category'):
                    if field_value.has_inventory_item:
                        try:
                            category_price = InventoryItemFair.objects.get(fair=registration.fair.id,
                                                                           inventory_item_id=field_value.inventory_item.id).price
                            price_rate = InventoryItemFair.objects.get(fair=registration.fair.id,
                                                                       inventory_item_id=field_value.inventory_item.id).price_rate
                            category_cost = category_price * price_rate
                            print('Category', category_price, price_rate, category_cost)
                            total_cost = category_cost
                            obj, created = InvoiceItem.objects.update_or_create(invoice=invoice,
                                                                        inventory_item_id=field_value.inventory_item.id,
                                                                        item_quanity= 1,
                                                                        item_cost=category_cost
                                                                        )
                        except Exception as e:  # It will catch other errors related to the cost determination.
                            db_logger.error('There was an error in determining stall category costs.' + e,
                                        extra={'custom_category': 'Invoicing'})
                    else:
                        category_cost = decimal.Decimal(0.00)
                        print('Category', category_cost)

                if field_name == 'site_size':
                    try:
                        site_price = InventoryItemFair.objects.get(fair=registration.fair.id,
                                                               inventory_item__id=int(field_value.id)).price
                        price_rate = InventoryItemFair.objects.get(fair=registration.fair.id,
                                                               inventory_item__id=int(field_value.id)).price_rate
                        site_cost = price_rate * site_price
                        print('Site Size',site_price, price_rate, site_cost)
                        total_cost = total_cost + site_cost
                        obj, created = InvoiceItem.objects.update_or_create(invoice=invoice,
                                                                            inventory_item_id=field_value.inventory_item.id,
                                                                            item_quanity=1,
                                                                            item_cost=site_cost
                                                                            )
                    except Exception as e:  # It will catch other errors related to the cost determination.
                        db_logger.error('There was an error in determining site size costs.' + e,
                                extra={'custom_category': 'Invoicing'})

                if field_name == ('trestle_quantity'):
                    if field_value > 0:
                        try:
                            trestle_price = InventoryItemFair.objects.get(fair=registration.fair.id,
                                                                          inventory_item__item_name='Trestle Table').price
                            price_rate = InventoryItemFair.objects.get(fair=registration.fair.id,
                                                                       inventory_item__item_name='Trestle Table').price_rate
                            total_trestle_cost = price_rate * trestle_price * decimal.Decimal(field_value)
                            print("Trestle", total_trestle_cost)
                            total_cost =total_cost + total_trestle_cost
                            obj, created = InvoiceItem.objects.update_or_create(invoice=invoice,
                                                                                inventory_item_id=field_value.inventory_item.id,
                                                                                item_quanity= field_value,
                                                                                item_cost=total_trestle_cost
                                                                                )
                        except Exception as e:  # It will catch other errors related to the cost determination.
                            db_logger.error('There was an error in determining trestle costs.' + e,
                                        extra={'custom_category': 'Invoicing'})
                    else:
                        total_trestle_cost = decimal.Decimal(0.00)
                        print("No Trestles", total_trestle_cost)

                if field_name == ('vehicle_length'):
                    if field_value > 6:
                        try:
                            vehicle_price = InventoryItemFair.objects.get(fair=registration.fair.id, inventory_item__item_name='Over 6m vehicle on site').price
                            price_rate = InventoryItemFair.objects.get(fair=registration.fair.id, inventory_item__item_name='Over 6m vehicle on site').price_rate
                            total_vehicle_cost = price_rate * vehicle_price
                            print("Vehicle", total_vehicle_cost)
                            total_cost =total_cost + total_vehicle_cost
                            obj, created = InvoiceItem.objects.update_or_create(invoice=invoice,
                                                                                inventory_item_id=field_value.inventory_item.id,
                                                                                item_quanity= 1,
                                                                                item_cost=total_vehicle_cost
                                                                                )
                        except Exception as e:  # It will catch other errors related to the cost determination.
                            db_logger.error('There was an error in determining vehicle length costs.' + e,
                                        extra={'custom_category': 'Invoicing'})
                    else:
                        total_vehicle_cost = decimal.Decimal(0.00)
                        print("No Vehicle", total_vehicle_cost)

                if field_name == 'power_required':
                    if field_value:
                        try:
                            power_price = InventoryItemFair.objects.get(fair=registration.fair.id,
                                                                        inventory_item__item_name='Power Point').price
                            price_rate = InventoryItemFair.objects.get(fair=registration.fair.id,
                                                                       inventory_item__item_name='Power Point').price_rate
                            power_cost = price_rate * power_price
                            print('Power', power_price, price_rate, power_cost)
                            total_cost = total_cost + power_cost
                            obj, created = InvoiceItem.objects.update_or_create(invoice=invoice,
                                                                                inventory_item_id=field_value.inventory_item.id,
                                                                                item_quanity= 1,
                                                                                item_cost=power_cost
                                                                                )
                        except Exception as e:  # It will catch other errors related to the cost determination.
                            db_logger.error('There was an error in determining vehicle length costs.' + e,
                                        extra={'custom_category': 'Invoicing'})
                    else:
                        power_cost = decimal.Decimal(0.00)
                        print('No Power', power_cost)

                if field_name == 'multi_site':
                    total_additional_site_costs = decimal.Decimal(0.00)
                    if AdditionalSiteRequirement.objects.filter(stall_registration=registration).exists():
                        try:
                            additional_site_list = AdditionalSiteRequirement.objects.filter( stall_registration=registration)
                            for additional_site in additional_site_list:
                                site_price = InventoryItemFair.objects.get(fair=registration.fair.id,
                                                                           inventory_item__id=additional_site.site_size.id).price
                                price_rate = InventoryItemFair.objects.get(fair=registration.fair.id,
                                                                           inventory_item__id=additional_site.site_size.id).price_rate
                                additional_site_costs = price_rate * site_price * additional_site.site_quantity
                                print('Additional Sites', additional_site.site_size, site_price, price_rate, additional_site.site_quantity )
                                total_additional_site_costs = total_additional_site_costs + additional_site_costs
                                obj, created = InvoiceItem.objects.update_or_create(invoice=invoice,
                                                                                inventory_item_id=field_value.inventory_item.id,
                                                                                item_quanity= additional_site.site_quantity,
                                                                                item_cost=additional_site_costs
                                                                                )
                            print("Total Additional Site Costs", total_additional_site_costs)
                            total_cost = total_cost + total_additional_site_costs
                        except Exception as e:  # It will catch other errors related to the cost determination.
                            db_logger.error('There was an error in determining multi-site costs.' + e,
                                        extra={'custom_category': 'Invoicing'})
        gst_component = round((total_cost * 3) / 23, 2)
        print('Total Cost', total_cost, 'GST Component', gst_component)


class InvoiceItem(models.Model):
    """
    Description: A model that provides the detail of the items that make up  each invoice
    """
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    item_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(9999), ], )
    item_cost = models.DecimalField(max_digits=8, decimal_places=2)

    objects = models.Manager()
    invoiceitemmgr = InvoiceItemManager()


class Meta:
        verbose_name = "invoiceitem"
        verbose_name_plural = "invoiceitems"
        unique_together = ('invoice', 'inventory_item')


