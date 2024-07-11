# registration/tests/test_paymenthistory.py

import factory
import random
from faker import Faker
from django.test import TransactionTestCase
from django.contrib.auth import get_user_model

from accounts.models import (
    CustomUser
)
from fairs.models import (
    Fair
)
from registration.models import (
    StallRegistration,
    StallCategory
)
from payment.models import (
    Invoice,
    PaymentHistory
)
fake =Faker()

class CreatePaymentHistoryManagerTest(TransactionTestCase):
    fixtures = ['accounts.yaml', 'authgroups.yaml', 'fairs_inventory.yaml', 'stallcategory.yaml', 'payments.yaml']

    def setUp(self):
        total_cost = round(random.randint(1, 1000) * random.random(), 2)
        gst_component =round((total_cost * 3) / 23, 2)

        current_fair = Fair.currentfairmgr.last()

        self.registration = StallRegistration(
            fair=current_fair,
            stallholder=CustomUser.objects.all().get(email='thehungrymonkey.wellington@gmail.com'),
            stall_manager_name=factory.LazyAttribute(lambda _: fake.name()),
            stall_category=StallCategory.objects.all().get(category_name='Hats'),
            stall_description=factory.LazyAttribute(lambda _: fake.text()),
            products_on_site=factory.LazyAttribute(lambda _: fake.text()),
            total_charge=total_cost
        )
        self.registration.save()

        self.invoice = Invoice(
            stall_registration=self.registration,
            stallholder=CustomUser.objects.all().get(email='thehungrymonkey.wellington@gmail.com'),
            total_cost=total_cost,
            gst_component=gst_component
        )
        self.invoice.save()


    def test_create_payment_history(self):
        invoice = self.invoice
        amount_to_pay = invoice.total_cost

        # Call the manager's create_payment history method
        payment_history = PaymentHistory.paymenthistorymgr.create_paymenthistory(
            invoice=invoice,
            amount_to_pay=amount_to_pay,
        )

        # Check if the payment history has been created correctly
        self.assertEqual(payment_history.invoice, invoice)
        self.assertEqual(payment_history.amount_to_pay, amount_to_pay)
        self.assertEqual(payment_history.payment_status,'Pending')
        self.assertEqual(payment_history.amount_paid, 0.0)

    def tearDown(self):
        # Clean up any created objects in the database
        get_user_model().objects.all().delete()

