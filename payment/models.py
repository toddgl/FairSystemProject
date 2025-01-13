# payment/models.py

import decimal
import datetime
import logging
from django.db import models
from django.conf import settings
from django.db.models import Max, Sum, UniqueConstraint, ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django_fsm import FSMField, transition
from accounts.models import CustomUser

from fairs.models import (
    InventoryItem,
    InventoryItemFair,
    SiteAllocation
)
from registration.models import (
    StallRegistration,
    AdditionalSiteRequirement
)

# Global Variables
current_year = datetime.datetime.now().year
next_year = current_year + 1
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
        verbose_name_plural = "payment types"


class InvoiceCurrentManager(models.Manager):
    """
    Description: Methods to access current Invoices
    """

    def get_queryset(self):
        return super().get_queryset().filter(stall_registration__fair__fair_year__in=[current_year, next_year], stall_registration__fair__is_activated=True )

    def get_registration_invoices(self, registration):
        return super().get_queryset().filter(stall_registration_id=registration)

    def get_stallholder_invoices(self, stallholder):
        return super().get_queryset().filter(stallholder_id=stallholder)


class Invoice(models.Model):
    """
    Description: A model for recording invoicing for stall registrations
    """
    invoice_number = models.PositiveIntegerField(default=1)
    invoice_sequence = models.IntegerField(default=1)
    stall_registration = models.ForeignKey(StallRegistration, on_delete=models.CASCADE)
    stallholder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    total_cost = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=2)
    gst_component = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=2)
    date_created = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    invoicecurrentmgr = InvoiceCurrentManager()

    class Meta:
        UniqueConstraint(
            fields=['invoice_number', 'invoice_sequence'],
            name='unique__invoice'
        )
        verbose_name = "invoice"
        verbose_name_plural = "invoices"

    def generate_invoice_number(stallregistration_pk):
        """
        Used to Generate invoice number for a new invoice
        - if there are no invoices in the system it starts at 1
        - if there has already been an invoice created for the stall Application this number is reused
        - if there is no invoices created for the stall Application it finds the highest invoice number in the
        system and increments this by 1
        """
        if Invoice.objects.filter(stall_registration__pk=stallregistration_pk).exists():
            invoice = Invoice.objects.filter(stall_registration__pk=stallregistration_pk).last()
            invoice_num = invoice.invoice_number
        else:
            invoice_num = Invoice.objects.all().aggregate(Max("invoice_number"))["invoice_number__max"]
            while Invoice.objects.filter(invoice_number=invoice_num).exists():
                invoice_num += 1

        if not invoice_num:
            invoice_num = 1

        return invoice_num

    def generate_sequence_number(stallregistration_pk):
        sequence_num = Invoice.objects.filter(stall_registration__pk=stallregistration_pk).aggregate(Max(
            "invoice_sequence"))["invoice_sequence__max"]

        if not sequence_num:
            sequence_num = 1

        while Invoice.objects.filter(
                stall_registration__pk=stallregistration_pk, invoice_sequence=sequence_num).exists():
            sequence_num += 1
        return sequence_num


class PaymentHistoryManager(models.Manager):
    """
    Used to create a PaymentHistory object when an invoice is initially created
    Parameters:
        invoice - invoice instance
        amount_to_pay - total amount to pay from the invoice
    Output:
        the created object
    """

    def create_paymenthistory(self, invoice, amount_to_pay, amount_paid=0.00, amount_reconciled=0.00):
        obj = PaymentHistory.objects.create(
            invoice=invoice,
            amount_to_pay=amount_to_pay,
            amount_paid=amount_paid,
            amount_reconciled=amount_reconciled
        )
        return obj


class PaymentHistoryCurrentManager(models.Manager):
    """
    Description: Methods to get current payments
    """

    def get_queryset(self):
        return super().get_queryset().filter(invoice__stall_registration__fair__fair_year__in=[current_year, next_year], invoice__stall_registration__fair__is_activated=True )

    def get_registration_payment_history(self, registration):
        return super().get_queryset().filter(invoice__stall_registration=registration).last()

    def get_all_except_superceded(self):
        return super().get_queryset().all().exclude(payment_status="Superceded")

    def get_stallholder_payment_history(self, stallholder):
        return self.get_queryset().filter(invoice__stallholder=stallholder)

    def get_pending(self):
        return self.get_queryset().filter(payment_status="Pending")

    def get_cancelled(self):
        return self.get_queryset().filter(payment_status="Cancelled")

    def get_completed(self):
        return self.get_queryset().filter(payment_status="Completed")

    def get_credit(self):
        return self.get_queryset().filter(payment_status="Credit")

    def has_credit_amount(self, invoice_id):
        return self.get_queryset().filter(invoice_id=invoice_id, amount_credited__gt=0).exists()

    def get_failed(self):
        return super().get_queryset().filter(payment_status="Failed")

    def get_reconciled(self):
        return super().get_queryset().filter(payment_status="Reconciled")


class PaymentHistory(models.Model):
    """
    Description: A model that records stallholder payment history includes credits as well as payment
    """
    PENDING = "Pending"
    SUPERCEDED = "Superceded"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"
    CREDIT = "Credit"
    FAILED = "Failed"
    RECONCILED = "Reconciled"


    PAYMENT_STATUS_CHOICES = [
        (PENDING, _("pending")),
        (SUPERCEDED, _("superceded")),
        (CANCELLED, _("cancelled")),
        (COMPLETED, _("completed")),
        (CREDIT, _("credit")),
        (FAILED, _("failed")),
        (RECONCILED, _("reconciled")),
    ]
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='payment_history'
    )
    amount_to_pay = models.DecimalField(default=0.00, max_digits=8, decimal_places=2)
    amount_paid = models.DecimalField(null=True, blank=True, max_digits=8, decimal_places=2)
    webhook_amount= models.DecimalField(null=True, blank=True, max_digits=8, decimal_places=2)
    amount_reconciled = models.DecimalField(null=True, blank=True, max_digits=8, decimal_places=2)
    amount_credited= models.DecimalField(null=True, blank=True, max_digits=8, decimal_places=2)
    payment_status = FSMField(
        default=PENDING,
        verbose_name='Payment State',
        choices=PAYMENT_STATUS_CHOICES,
        protected=False,
    )
    payment_type = models.ForeignKey(
        PaymentType,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    stripe_checkout_id = models.CharField(
        blank=True,
        null=True
    )
    objects = models.Manager()
    paymenthistorymgr = PaymentHistoryManager()
    paymenthistorycurrentmgr = PaymentHistoryCurrentManager()

    class Meta:
        verbose_name = "payment"
        verbose_name_plural = "payments"

    def total_paid(stall_registration):
        paid_total = PaymentHistory.objects.filter(invoice__stall_registration=stall_registration).aggregate(TOTAL=Sum(
            'amount_paid'))['TOTAL']
        return paid_total

    def total_reconciled(stall_registration):
        reconciled_total = \
        PaymentHistory.objects.filter(invoice__stall_registration=stall_registration).aggregate(TOTAL=Sum(
            'amount_reconciled'))['TOTAL']
        return reconciled_total

    @transition(field=payment_status, source=["Pending","Completed","Reconciled","Failed"], target="Superceded")
    def to_payment_status_superceded(self):
        pass

    @transition(field=payment_status, source="Pending", target="Cancelled")
    def to_payment_status_cancelled(self):
        pass

    @transition(field=payment_status, source="Pending", target="Failed")
    def to_payment_status_failed(self):
        pass

    @transition(field=payment_status, source="Pending", target="Completed")
    def to_payment_status_completed(self):
        pass

    @transition(field=payment_status, source=["Pending", "Completed"], target="Credit")
    def to_payment_status_credit(self):
        pass

    @transition(field=payment_status, source="Completed", target="Reconciled")
    def to_payment_status_reconciled(self):
        pass

    def update_payment(self, amount_paid):
        self.amount_paid += amount_paid
        self.amount_to_pay -= amount_paid
        self.save()
        if self.amount_to_pay <= 0:
            self.to_payment_status_completed()

class InvoiceItemManager(models.Manager):

    def create_invoice_items(self, registration):
        """
        Cycle through the billable items on the stall Application instance and create an invoice and invoice item
        for each of teh billable items on the stall Application record

        Parameters:
        - Application: The instance of the StallRegistration.
        - field_list: A list of field names to iterate through.
        - action: A function representing the action to be performed on each field.
        """
        fields_to_check = ['stall_category', 'trestle_quantity', 'vehicle_length', 'power_required', 'multi_site']
        invoice = Invoice.objects.create(
            invoice_number=Invoice.generate_invoice_number(registration.id),
            invoice_sequence=Invoice.generate_sequence_number(registration.id),
            stall_registration=registration,
            stallholder=registration.stallholder,
        )
        total_cost = decimal.Decimal(0.00)
        # Determine if there are any discounts, if so sum them and record them as a negative amount against totle cost
        discounts = DiscountItem.objects.filter(stall_registration=registration)
        if discounts:
            total_cost = total_cost - sum(discounts.values_list('discount_amount', flat=True))

        existing_payment_history = PaymentHistory.paymenthistorycurrentmgr.get_registration_payment_history(registration)
        if existing_payment_history:
            existing_payment = existing_payment_history.amount_paid
        else:
            existing_payment = decimal.Decimal(0.00)
        try:
            site_allocation = SiteAllocation.currentallocationsmgr.filter(stallholder=registration.stallholder,
                                                                          stall_registration=registration).first()
            if site_allocation:
                site_size = site_allocation.event_site.site.site_size
                site_price = InventoryItemFair.objects.get(fair=registration.fair.id,
                                                           inventory_item=site_size).price
                price_rate = InventoryItemFair.objects.get(fair=registration.fair.id,
                                                           inventory_item=site_size).price_rate
                site_cost = price_rate * site_price
                print('Site Size', site_price, price_rate, site_cost)
                total_cost = total_cost + site_cost
        except ObjectDoesNotExist as e:
            db_logger.error('For Stall Registration ID ' + str(
                registration.id) + ' there was an error in determining site size costs.' + str(e),
                            extra={'custom_category': 'Invoicing'})

        try:
            InvoiceItem.objects.create(invoice=invoice,
                                       inventory_item=site_size,
                                       item_quantity=1,
                                       item_cost=site_cost
                                       )
        except Exception as e:  # It will catch other errors related to the cost determination.
            db_logger.error('For Stall Registration ID ' + str(
                registration.id) + 'there was an error in determining site size costs.' + str(e),
                            extra={'custom_category': 'Invoicing'})

        for field_name in fields_to_check:
            field_value = getattr(registration, field_name, None)
            if field_value is not None:
                print(registration, field_name, field_value)
                if field_name == 'stall_category':
                    if field_value.has_inventory_item:
                        category_price = InventoryItemFair.objects.get(fair=registration.fair.id,
                                                                       inventory_item_id=field_value.inventory_item.id).price
                        price_rate = InventoryItemFair.objects.get(fair=registration.fair.id,
                                                                   inventory_item_id=field_value.inventory_item.id).price_rate
                        category_cost = category_price * price_rate
                        print('Category', category_price, price_rate, category_cost)
                        total_cost = total_cost + category_cost
                        try:
                            InvoiceItem.objects.create(invoice=invoice,
                                                       inventory_item=field_value.inventory_item,
                                                       item_quantity=1,
                                                       item_cost=category_cost
                                                       )
                        except Exception as e:  # It will catch other errors related to the cost determination.
                            db_logger.error('For Stall Registration ID ' + str(
                                registration.id) + 'there was an error in determining) stall category costs. ' + str(e),
                                            extra={'custom_category': 'Invoicing'})
                    else:
                        category_cost = decimal.Decimal(0.00)
                        print('Category', category_cost)

                if field_name == 'trestle_quantity':
                    if field_value > 0:
                        inventory_item = InventoryItem.objects.get(item_name='Trestle Table')
                        trestle_price = InventoryItemFair.objects.get(fair=registration.fair.id,
                                                                      inventory_item__item_name='Trestle Table').price
                        price_rate = InventoryItemFair.objects.get(fair=registration.fair.id,
                                                                   inventory_item__item_name='Trestle Table').price_rate
                        total_trestle_cost = price_rate * trestle_price * decimal.Decimal(field_value)
                        print("Trestle", total_trestle_cost)
                        total_cost = total_cost + total_trestle_cost
                        try:
                            InvoiceItem.objects.create(invoice=invoice,
                                                       inventory_item=inventory_item,
                                                       item_quantity=field_value,
                                                       item_cost=total_trestle_cost
                                                       )
                        except Exception as e:  # It will catch other errors related to the cost determination.
                            db_logger.error('For Stall Application ID ' + str(
                                registration.id) + 'there was an error in determining trestle costs.' + str(e),
                                            extra={'custom_category': 'Invoicing'})
                    else:
                        total_trestle_cost = decimal.Decimal(0.00)
                        print("No Trestles", total_trestle_cost)

                if field_name == 'vehicle_length':
                    if field_value is not None and field_value > 6:
                        inventory_item = InventoryItem.objects.get(item_name='Over 6m vehicle on site')
                        vehicle_price = InventoryItemFair.objects.get(fair=registration.fair.id,
                                                                      inventory_item__item_name='Over 6m vehicle on site').price
                        price_rate = InventoryItemFair.objects.get(fair=registration.fair.id,
                                                                   inventory_item__item_name='Over 6m vehicle on site').price_rate
                        total_vehicle_cost = price_rate * vehicle_price
                        print("Vehicle", total_vehicle_cost)
                        total_cost = total_cost + total_vehicle_cost
                        try:
                            InvoiceItem.objects.create(invoice=invoice,
                                                       inventory_item=inventory_item,
                                                       item_quantity=1,
                                                       item_cost=total_vehicle_cost
                                                       )
                        except Exception as e:  # It will catch other errors related to the cost determination.
                            db_logger.error('For Stall Application ID ' + str(
                                registration.id) + 'there was an error in determining vehicle length costs.' + str(e),
                                            extra={'custom_category': 'Invoicing'})
                    else:
                        total_vehicle_cost = decimal.Decimal(0.00)
                        print("No Vehicle", total_vehicle_cost)

                if field_name == 'power_required':
                    if field_value:
                        try:
                            inventory_item = InventoryItem.objects.get(item_name='Power Point')
                            power_price = InventoryItemFair.objects.get(fair=registration.fair.id,
                                                                        inventory_item__item_name='Power Point').price
                            price_rate = InventoryItemFair.objects.get(fair=registration.fair.id,
                                                                       inventory_item__item_name='Power Point').price_rate
                            power_cost = price_rate * power_price
                            print('Power', power_price, price_rate, power_cost)
                            total_cost = total_cost + power_cost
                            InvoiceItem.objects.create(invoice=invoice,
                                                       inventory_item=inventory_item,
                                                       item_quantity=1,
                                                       item_cost=power_cost
                                                       )
                        except Exception as e:  # It will catch other errors related to the cost determination.
                            db_logger.error('For Stall Application ID ' + str(
                                registration.id) + 'there was an error in determining vehicle length costs.' + str(e),
                                            extra={'custom_category': 'Invoicing'})
                    else:
                        power_cost = decimal.Decimal(0.00)
                        print('No Power', power_cost)

                if field_name == 'multi_site':
                    total_additional_site_costs = decimal.Decimal(0.00)
                    if AdditionalSiteRequirement.objects.filter(stall_registration=registration).exists():
                        try:
                            additional_site_list = AdditionalSiteRequirement.objects.filter(stall_registration=registration)
                            for additional_site in additional_site_list:
                                site_price = InventoryItemFair.objects.get(fair=registration.fair.id,
                                                                           inventory_item__id=additional_site.site_size.id).price
                                price_rate = InventoryItemFair.objects.get(fair=registration.fair.id,
                                                                           inventory_item__id=additional_site.site_size.id).price_rate
                                additional_site_costs = price_rate * site_price * additional_site.site_quantity
                                print('Additional Sites', additional_site.site_size, site_price, price_rate,
                                      additional_site.site_quantity)
                                total_additional_site_costs = total_additional_site_costs + additional_site_costs
                                InvoiceItem.objects.create(invoice=invoice,
                                                           inventory_item=additional_site.site_size,
                                                           item_quantity= additional_site.site_quantity,
                                                           item_cost=additional_site_costs
                                                           )
                            print("Total Additional Site Costs", total_additional_site_costs)
                            total_cost = total_cost + total_additional_site_costs
                        except Exception as e:  # It will catch other errors related to the cost determination.
                            db_logger.error('For Stall Application ID ' + str(
                                registration.id) + 'there was an error in determining multi-site costs.' + str(e),
                                            extra={'custom_category': 'Invoicing'})
        gst_component = round((total_cost * 3) / 23, 2)
        invoice.total_cost = total_cost
        invoice.gst_component = gst_component
        try:
            invoice.save()
        except Exception as e:  # It will catch other errors related to the create call
            db_logger.error('There was an error in creating the invoice.' + str(e),
                            extra={'custom_category': 'Application Invoice'})
        try:
            registration.is_invoiced = True
            registration.save(update_fields=["is_invoiced"])
        except Exception as e:  # It will catch other errors related to the create call
            db_logger.error('There was an error in updating the Application - ' + str(registration.id) + str(e),
                            extra={'custom_category': 'Application Invoice'})
        # create a payment history instance if there was a previous one transfer payment and reconciliation amounts
        try:
            if existing_payment_history:
                amount_to_pay = total_cost - existing_payment_history.amount_paid
                PaymentHistory.paymenthistorymgr.create_paymenthistory(invoice, amount_to_pay,
                                                                       existing_payment_history.amount_paid,
                                                                       existing_payment_history.amount_reconciled)
                existing_payment_history.to_payment_status_superceded()
                existing_payment_history.save()
            else:
                PaymentHistory.paymenthistorymgr.create_paymenthistory(invoice, total_cost)
        except Exception as e:  # It will catch other errors related to the create call
            db_logger.error('There was an error in creating the payment history.' + str(e),
                            extra={'custom_category': 'Payment History'})


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


class DiscountItemManager(models.Manager):
    """
    Description: Methods to access discount items
    """

    def get_queryset(self):
        return super().get_queryset().filter(stall_registration__fair__fair_year__in=[current_year, next_year])

    def get_registration_discount(self, registration):
        return super().get_queryset().filter(stall_registration=registration)

    def get_stallholder_discounts(self, stallholder):
        return super().get_queryset().filter(stall_registration__stallholder_id=stallholder)


class DiscountItem(models.Model):
    """
    Description: A model used to record a discount amount that the convener can apply to a registration cost
    """
    stall_registration = models.ForeignKey(StallRegistration, on_delete=models.CASCADE)
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2)
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, related_name='discount_created_by', on_delete=models.SET_NULL,
                                   blank=True, null=True)
    objects = models.Manager()
    discountitemmgr = DiscountItemManager()


class Meta:
    verbose_name = "discountitem"
    verbose_name_plural = "discountitems"
