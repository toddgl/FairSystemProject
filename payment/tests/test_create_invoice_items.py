#payment/tests/test_create_invoice_items

from django.test import TestCase
from accounts.models import CustomUser
from fairs.models import (
    Fair,
    InventoryItem,
    InventoryItemFair
)
from registration.models import (
    StallRegistration,
    StallCategory,
)
from payment.models import (
     Invoice,
     InvoiceItem
)

class TestInvoiceCreation(TestCase):
    def setUp(self):
        # Creating a sample user
        self.stallholder = CustomUser.objects.create(username='testuser')

        #Creating a fair
        self.fair = Fair.objects.create(fair_name='testfair')

        # Creating a sample StallCategory
        self.stall_category = StallCategory.objects.create(category_name='Food/drink (consumption on site)')

        # Creating InventoryItem
        self.inventory_item_trestle = InventoryItem.objects.create(item_name='Trestle Table')
        self.inventory_item_power = InventoryItem.objects.create(item_name='Power Point')

        # Create InventoryItemFair
        self.inventory_item_fair_trestle = InventoryItemFair.objects.create(fair=self.fair, inventory_item= self.inventory_item_trestle, price=50.00)
        self.inventory_item_fair_power = InventoryItemFair.objects.create(fair=self.fair, inventory_item= self.inventory_item_power, price=150.00)

        # Creating a sample StallRegistration
        self.registration = StallRegistration.objects.create(
            fair_id=self.fair.id,
            stall_category=self.stall_category,
            trestle_quantity=2,
            vehicle_length=5,
            power_required=True,
            multi_site=False,
            stallholder=self.stallholder,
            total_charge=650
            # Add other necessary fields here
        )


    def test_invoice_creation(self):
        # Ensure that an Invoice is created when the function is called
        self.assertEqual(Invoice.objects.count(), 0)  # Ensure no invoices initially

        # Call the function
        InvoiceItem.invoiceitemmgr.create_invoice_items(self.registration)

        # Check if an Invoice is created
        self.assertEqual(Invoice.objects.count(), 1)

        # Check value of total_cost
        self.invoice = Invoice.objects.all().last()
        self.assertEqual(self.invoice.total_cost, 250)

    def test_invoice_items_creation(self):
        # Ensure that no InvoiceItems exist initially
        self.assertEqual(InvoiceItem.objects.count(), 0)

        # Call the function
        InvoiceItem.invoiceitemmgr.create_invoice_items(self.registration)

        # Check if InvoiceItems are created
        self.assertEqual(InvoiceItem.objects.count(), 2)

    # Add more tests to ensure correct behavior for different scenarios
