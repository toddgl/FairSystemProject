# registration/services/pricing.py

from registration.services.billing import RegistrationBillingService


def get_registration_costs(registration):
    """
    Calculate pricing for BOTH:
    - unsaved registrations (create preview)
    - saved registration (update/invoice)
    """

    print("Got to get_registration_costs in pricing.py")
    if not registration.fair:
        return 0, []
    billing = RegistrationBillingService(registration.fair)
    total, items = billing.calculate_total(registration)

    return total, items
