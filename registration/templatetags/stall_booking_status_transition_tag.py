# registration/templatetags/stall_booking_status_transition_tag.py
from django import template
from django.urls import reverse
from registration.models import StallRegistration

register = template.Library()

@register.simple_tag
def get_transition_targets_with_urls(stall_registration_id):
    try:
        stall_registration = StallRegistration.objects.get(id=stall_registration_id)
        transitions = stall_registration.get_available_booking_status_transitions()

        # Assuming you have a URL pattern named 'transition_booking_status'
        # that accepts 'stall_registration_id' and 'target_status' as arguments
        targets_with_urls = [
            {
                'target': transition.target,
                'url': reverse('registration:transition_booking_status', kwargs={
                    'stall_registration_id': stall_registration_id,
                    'target_status': transition.target
                })
            }
            for transition in transitions
        ]
        return targets_with_urls
    except StallRegistration.DoesNotExist:
        return []

