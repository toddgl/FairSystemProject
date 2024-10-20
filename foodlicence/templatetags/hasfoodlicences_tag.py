# foodlicence/templatetags/hasfoodlicences_tags.py

from django import template
from foodlicence.models import (
    FoodLicence,
    FoodLicenceBatch
)
from payment.models import (
    PaymentHistory
)
from registration.models import (
    StallRegistration
)

register = template.Library()

@register.simple_tag
def can_generate_foodlicence(value):
    """
    Templatetag to provide a boolean answer whether there is a need to gernerate a foodlicence for a stallregistration
    Used in the convener stall registration detail view
    """
    # Check to ensure that the StallRegistration is "Complete" and it has a FoodRegistration
    eligible_registration = StallRegistration.objects.filter(id=value,
                                            invoice__payment_history__payment_status=PaymentHistory.COMPLETED,
                                        food_registration__isnull=False ).exists()
    foodlicence_exists = FoodLicence.foodlicencecurrentmgr.filter(food_registration__registration_id=value).exists()
    if eligible_registration and not foodlicence_exists:
        return True
    else:
        return False

@register.simple_tag
@register.simple_tag
def can_generate_multiple_foodlicencs():
    """
    Templatetag to provide a boolean answer whether there is a need to gernerate foodlicences for stallregistrations
    Used in the convener foodlicence list view
    """
    # Find stall registrations with completed payments
    eligible_stall_registrations = StallRegistration.objects.filter(
        invoice__payment_history__payment_status=PaymentHistory.COMPLETED,
        food_registration__isnull=False  # Ensures that a FoodRegistration exists
    ).distinct()

    # Filter out stall registrations that already have a FoodLicence created
    eligible_stall_registrations = eligible_stall_registrations.exclude(
        food_registration__food_licence__isnull=False
    )

    if eligible_stall_registrations.exists():
        return True
    else:
        return False

@register.simple_tag
def get_has_foodlicences():
    """
    Templatetag to provide a boolean answer whether there are any foodlicences
    Used in the convener foodlicence list
    """
    foodlicence_exists = FoodLicence.foodlicencecurrentmgr.exists()
    if foodlicence_exists:
        return True
    else:
        return False

@register.simple_tag
def get_number_staged_foodlicences():
    """
    Templatetag to give a count of batched food licences used in the convener foodlicence list
    """
    staged_foodlicence_count = FoodLicence.foodlicencecurrentmgr.filter(licence_status='Staged').count()
    return staged_foodlicence_count

@register.simple_tag
def get_has_foodlicence_batches():
    """
    Templatetag to provide a boolean answer whether there are any foodlicence batches
    Used in the convener foodlicence batch list
    """
    foodlicence_batch_exists = FoodLicenceBatch.foodlicencebatchcurrentmgr.exists()
    if foodlicence_batch_exists:
        return True
    else:
        return False

