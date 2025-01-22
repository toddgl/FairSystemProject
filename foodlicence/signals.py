from django.db.models.signals import post_save
from django.dispatch import receiver
from django_fsm.signals import post_transition
from .models import FoodLicence
from registration.models import StallRegistration

@receiver(post_transition, sender=FoodLicence)
def update_stall_registration_on_licence_approval(instance, name, source, target, **kwargs):
    """
    Updates the StallRegistration booking_status to "Payment Completed" when
    the FoodLicence is approved.
    """

    if target == FoodLicence.APPROVED:  # Check if the target status is "Approved"
        stall_registration = instance.food_registration.registration
        if stall_registration:
            stall_registration.booking_status = StallRegistration.BOOKED
            stall_registration.save()
