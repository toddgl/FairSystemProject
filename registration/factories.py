# registration/tests/factories.py

import factory
from factory.django import DjangoModelFactory
from faker import Faker
from accounts.models import CustomUser
from fairs.models import Fair
from payment.models import Invoice
from registration.models import (
    StallRegistration,
    StallCategory
)
import random

fake =Faker()
class UserFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser
        django_get_or_create = ('username',)

    username = factory.LazyAttribute(lambda _: fake.unique.email())
    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name = factory.LazyAttribute(lambda _: fake.last_name())

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

class RegistrationFactory(DjangoModelFactory):
    class Meta:
        model = StallRegistration

    fair = factory.SubFactory(FairFactory)
    stallholder = factory.SubFactory(UserFactory)
    stall_manager_name = factory.LazyAttribute(lambda _: fake.name())
    stall_category = factory.SubFactory(StallCategoryFactory)
    stall_description = factory.LazyAttribute(lambda  _: fake.text())
    products_on_site = factory.LazyAttribute(lambda  _: fake.text())
    total_charge = round(random.randint(1, 1000) * random.random(), 2)

class InvoiceFactory(DjangoModelFactory):
    class Meta:
        model = Invoice

    stall_registration = factory.SubFactory(RegistrationFactory)
    stallholder = factory.SubFactory(UserFactory)
    total_cost = round(random.randint(1, 1000) * random.random(), 2)
    gst_value =  round((total_cost * 3) / 23, 2)

