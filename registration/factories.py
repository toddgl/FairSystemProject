# registration/tests/factories.py

import factory
from factory.django import DjangoModelFactory
from faker import Faker
from accounts.models import CustomUser

fake =Faker()
class UserFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name = factory.LazyAttribute(lambda _: fake.last_name())
    email = factory.LazyAttribute(lambda _: fake.unique.email())