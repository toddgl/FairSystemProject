# foodlicence/templatetags/hasfoodlicences_tags.py

from django.db.models import Q
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
    Templatetag to provide a boolean answer whether there is a need to generate a foodlicence for a stallregistration
    Used in the convener stall registration detail view
    """
    # Check to ensure that the StallRegistration is either "Complete" "Reconciled" or "Credit" and it has a foodregistration
    eligible_registration =StallRegistration.registrationcurrentmgr.filter(id=value,
                                                                           food_registration__isnull=False
                                                                           ).filter(
        Q(invoice__payment_history__payment_status__in=[
            PaymentHistory.COMPLETED,
            PaymentHistory.RECONCILED,
            PaymentHistory.CREDIT
        ])
    ).exists()
    foodlicence_exists = FoodLicence.foodlicencecurrentmgr.filter(food_registration__registration_id=value).exists()
    if eligible_registration and not foodlicence_exists:
        return True
    else:
        return False

@register.simple_tag
@register.simple_tag
def can_generate_multiple_foodlicences():
    """
    Templatetag to provide a boolean answer whether there is a need to gernerate foodlicences for stallregistrations
    Used in the convener foodlicence list view
    """
    # Find stall registrations with completed payments
    eligible_stall_registrations = StallRegistration.registrationcurrentallmgr.filter(
        food_registration__isnull=False
    ).filter(
        Q(invoice__payment_history__payment_status__in=[
            PaymentHistory.COMPLETED,
            PaymentHistory.RECONCILED,
            PaymentHistory.CREDIT
        ]
    )).distinct()

    # Filter out stall registrations that already have a FoodLicence created
    eligible_stall_registrations = eligible_stall_registrations.exclude(
        food_registration__food_licence__isnull=False
    )

    return eligible_stall_registrations.exists()

@register.simple_tag
def get_has_foodlicences():
    """
    Templatetag to provide a boolean answer whether there are any foodlicences
    Used in the convener foodlicence list
    """
    foodlicence_exists = FoodLicence.foodlicencecurrentmgr.exists()
    return foodlicence_exists

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

