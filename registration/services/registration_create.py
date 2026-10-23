# registration/services/registration_create.py

from django.db import transaction

from registration.services.billing import RegistrationBillingService
from registration.services.power_connections import sync_power_connections


@transaction.atomic
def create_registration(form, stallholder):
    registration = form.save(commit=False)
    registration.stallholder = stallholder

    billing_service = RegistrationBillingService(registration.fair)
    billing = billing_service.calculate(registration)

    registration.total_charge = billing["total"]
    registration.save()
    form.save_m2m()

    sync_power_connections(registration)

    return registration, billing
