# registration/tests/test_paymenthistory.py

from django.test import TransactionTestCase
from django.contrib.auth import get_user_model
from registration.factories import (
    UserFactory,
    RegistrationFactory,
    InvoiceFactory
)
from payment.models import (
    PaymentHistory
)

class CreateRegistrationCommentManagerTest(TransactionTestCase):

    def setUp(self):
        self.user = UserFactory()
        self.registration = RegistrationFactory()
        self.invoice = InvoiceFactory()

    def test_create_payment_history(self):
        invoice = self.invoice
        amount_to_pay = invoice.total_cost

        # Call the manager's create_comment method
        payment_history = PaymentHistory.paymenthistorymgr.create_paymenthistory(
            invoice=invoice,
            amount_to_pay=amount_to_pay,
        )

        # Check if the comment has been created correctly
        self.assertEqual(payment_history.invoice, invoice)
        self.assertEqual(payment_history.amount_to_pay, amount_to_pay)
        self.assertEqual(payment_history.payment_status,'Pending')
        self.assertEqual(payment_history.amount_paid, None)

    def tearDown(self):
        # Clean up any created objects in the database
        get_user_model().objects.all().delete()
        PaymentHistory.objects.all().delete()

