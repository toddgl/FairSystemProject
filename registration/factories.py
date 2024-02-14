# registration/tests/factories.py

import factory
from factory.django import DjangoModelFactory
from faker import Faker
from accounts.models import CustomUser
from fairs.models import (
    Fair,
    InventoryItem,
    InventoryItemFair
)
from payment.models import (
    Invoice,
    InventoryItem,
    PaymentType,
    PaymentHistory
)
from registration.models import (
    StallRegistration,
    StallCategory
)
import random

fake =Faker()
class UserFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

class FairFactory(DjangoModelFactory):

    class Meta:
        model = Fair
        django_get_or_create = ('fair_name',)

    fair_name = "Test Fair"
    fair_description = factory.LazyAttribute(lambda  _: fake.text())

class StallCategoryFactory(DjangoModelFactory):

    class Meta:
        model = StallCategory

    category_name = "Test Category"

class InventoryItemFactory(DjangoModelFactory):

    class Meta:
        model = InventoryItem

    item_description = "Test Inventory Item"

class InventoryItemFairFactory(DjangoModelFactory):

    class Mets:
        model = InventoryItemFair


class RegistrationFactory(DjangoModelFactory):
    class Meta:
        model = StallRegistration


class InvoiceFactory(DjangoModelFactory):
    class Meta:
        model = Invoice


class PaymentTypeFactory(DjangoModelFactory):
    class Meta:
        model = PaymentType

class PaymentHistoryFactory(DjangoModelFactory):
    class Meta:
        model = PaymentHistory

