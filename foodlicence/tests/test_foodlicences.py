# tests/test_foodlicence.py

import factory
import random
from faker import Faker
from django.test import TestCase
from django.utils import timezone
from foodlicence.models import (
    FoodLicence,
    FoodLicenceBatch
)
from accounts.models import (
    CustomUser
)
from fairs.models import (
    Fair
)
from registration.models import (
    FoodRegistration,
    StallRegistration,
    StallCategory
)

fake =Faker()

class FoodLicenceTestCase(TestCase):
    fixtures = ['accounts.yaml', 'authgroups.yaml', 'fairs_inventory.yaml', 'stallcategory.yaml']

    def setUp(self):
        # Create a StallRegistration Object
        total_cost = round(random.randint(1, 1000) * random.random(), 2)
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

        # Create a FoodRegistration object
        self.food_registration = FoodRegistration.objects.create(
            registration=self.registration
        )

        # Create FoodLicence objects
        self.food_licence_created = FoodLicence.objects.create(
            food_registration=self.food_registration,
            licence_status=FoodLicence.CREATED,
        )
        self.food_licence_batched = FoodLicence.objects.create(
            food_registration=self.food_registration,
            licence_status=FoodLicence.BATCHED,
        )
        self.food_licence_submitted = FoodLicence.objects.create(
            food_registration=self.food_registration,
            licence_status=FoodLicence.SUBMITTED,
        )
        self.food_licence_rejected = FoodLicence.objects.create(
            food_registration=self.food_registration,
            licence_status=FoodLicence.REJECTED,
        )
        self.food_licence_approved = FoodLicence.objects.create(
            food_registration=self.food_registration,
            licence_status=FoodLicence.APPROVED,
        )

    def test_get_created(self):
        created_licences = FoodLicence.foodlicencecurrentmgr.get_created()
        self.assertIn(self.food_licence_created, created_licences)
        self.assertNotIn(self.food_licence_batched, created_licences)

    def test_get_batched(self):
        batched_licences = FoodLicence.foodlicencecurrentmgr.get_batched()
        self.assertIn(self.food_licence_batched, batched_licences)
        self.assertNotIn(self.food_licence_created, batched_licences)

    def test_get_submitted(self):
        submitted_licences = FoodLicence.foodlicencecurrentmgr.get_submitted()
        self.assertIn(self.food_licence_submitted, submitted_licences)
        self.assertNotIn(self.food_licence_batched, submitted_licences)

    def test_get_rejected(self):
        rejected_licences = FoodLicence.foodlicencecurrentmgr.get_rejected()
        self.assertIn(self.food_licence_rejected, rejected_licences)
        self.assertNotIn(self.food_licence_submitted, rejected_licences)

    def test_get_approved(self):
        approved_licences = FoodLicence.foodlicencecurrentmgr.get_approved()
        self.assertIn(self.food_licence_approved, approved_licences)
        self.assertNotIn(self.food_licence_rejected, approved_licences)

    def test_to_licence_status_batched(self):
        self.food_licence_created.to_licence_status_batched()
        self.assertEqual(self.food_licence_created.licence_status, FoodLicence.BATCHED)

    def test_to_licence_status_submitted(self):
        self.food_licence_batched.to_licence_status_submitted()
        self.assertEqual(self.food_licence_batched.licence_status, FoodLicence.SUBMITTED)

    def test_to_licence_status_rejected(self):
        self.food_licence_submitted.to_licence_status_rejected()
        self.assertEqual(self.food_licence_submitted.licence_status, FoodLicence.REJECTED)
        self.assertIsNotNone(self.food_licence_submitted.date_completed)

    def test_to_licence_status_approved(self):
        self.food_licence_submitted.to_licence_status_approved()
        self.assertEqual(self.food_licence_submitted.licence_status, FoodLicence.APPROVED)
        self.assertIsNotNone(self.food_licence_submitted.date_completed)

class FoodLicenceBatchTestCase(TestCase):

    def setUp(self):
        # Create FoodLicenceBatch objects
        # Ensure date_created is set correctly by manipulating the date_created field
        now = timezone.now()
        self.food_licence_batch_current_year = FoodLicenceBatch.objects.create(
            recipient_email='test@example.com',
            date_sent=now,
            batch_count=1,
        )
        self.food_licence_batch_current_year.date_created = now
        self.food_licence_batch_current_year.save()

        self.food_licence_batch_next_year = FoodLicenceBatch.objects.create(
            recipient_email='test2@example.com',
            date_sent=now.replace(year=now.year + 1),
            batch_count=1,
        )
        self.food_licence_batch_next_year.date_created = now.replace(year=now.year + 1)
        self.food_licence_batch_next_year.save()

        self.food_licence_batch_previous_year = FoodLicenceBatch.objects.create(
            recipient_email='test3@example.com',
            date_sent=now.replace(year=now.year - 1),
            batch_count=1,
        )
        self.food_licence_batch_previous_year.date_created = now.replace(year=now.year - 1)
        self.food_licence_batch_previous_year.save()

    def test_get_queryset(self):
        current_batches = FoodLicenceBatch.foodlicencebatchcurrentmgr.get_queryset()
        self.assertIn(self.food_licence_batch_current_year, current_batches)
        self.assertIn(self.food_licence_batch_next_year, current_batches)
        self.assertNotIn(self.food_licence_batch_previous_year, current_batches)