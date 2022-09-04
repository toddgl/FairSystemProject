# fairs/signals.py

from django.db.models.signals import pre_delete, post_save, post_delete
from django.dispatch import receiver
from .models import SiteAllocation, EventSite


@receiver(post_save, sender=SiteAllocation)
def set_allocation_status(sender, instance, **kwargs):
    eventsite_item = EventSite.objects.get(id=instance.event_site.id)
    eventsite_item.site_status = 2
    eventsite_item.save()


@receiver(post_delete, sender=SiteAllocation)
def unset_allocation_status(sender, instance, **kwargs):
    eventsite_item = EventSite.objects.get(id=instance.event_site.id)
    eventsite_item.site_status = 1
    eventsite_item.save()


@receiver(pre_delete, sender=SiteAllocation)
def allow_siteallocation_delete_if_not_booked(sender, instance, **kwargs):
    eventsite = EventSite.objects.get(id=instance.event_site.id)
    if eventsite.site_status > 2:
        raise Exception("This event site status is beyond allocated.")
