# registration/services/registration_create.py

from registration.services.billing import RegistrationBillingService

def create_registration(form, stallholder):

    registration = form.save(commit=False)
    registration.stallholder = stallholder

    billing_service = RegistrationBillingService(
        registration.fair
    )

    billing = billing_service.calculate(registration)

    registration.total_charge = billing["total"]
    registration.save()
    form.save_m2m()

    return registration, billing