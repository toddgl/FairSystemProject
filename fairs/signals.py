# fairs/signals.py

from django.db.models.signals import pre_save, pre_delete, post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import Fair, SiteAllocation, EventSite

@receiver(pre_save, sender=Fair)
def archive_event_sites_on_deactivate(sender, instance, **kwargs):
    if instance.pk:
        previous_fair = Fair.objects.get(pk=instance.pk)
        if previous_fair.is_activated and not instance.is_activated:
            # The fair is being deactivated
            event_sites = EventSite.objects.filter(event__fair=previous_fair)
            with transaction.atomic():
                event_sites.update(site_status=EventSite.ARCHIVED)

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
