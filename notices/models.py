# notices/models.py

from django.db import models
from django.db.models import F, ExpressionWrapper, DateTimeField

# Create your models here.
class ActiveNoticeManager(models.Manager):
    """
    Manager that returns the current Notices, ordered by the newer of date_created and date_updated from
    the latest to the oldest instances accessed by calling Notice.activenoticemgr.all()
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True).annotate(
            latest_update=ExpressionWrapper(
                models.functions.Greatest(F('date_created'), F('date_updated')),
                output_field=DateTimeField()
            )
        ).order_by('-latest_update')


class Notice(models.Model):
    """
    Description: Store for notices that will be displayed on the home page
    """
    notice_title = models.TextField()
    notice_content = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()
    activenoticemgr = ActiveNoticeManager()

    def __str__(self):
        return self.notice_content

    class Meta:
        verbose_name_plural = "Notices"
