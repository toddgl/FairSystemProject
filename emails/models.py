import datetime
from django.db import models
from django.conf import settings  # new
from django.utils.translation import gettext_lazy as _
from fairs.models import (
    Fair
)
from registration.models import (
    CommentType
)


class EmailHistoryCurrentManager(models.Manager):
    """
    Description: Methods to get current emails
    """

    def get_queryset(self):
        current_year = datetime.datetime.now().year
        next_year = current_year + 1
        return super().get_queryset().filter(
            fair__fair_year__in=[current_year, next_year]
        )

class Email(models.Model):

    """Model to store outgoing email information"""

    stallholder = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # new
        null=True,
        on_delete=models.CASCADE,
        related_name='emails'
    )
    fair = models.ForeignKey(
        Fair,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='fair',
        related_name='emails_fair'
    )
    subject_type = models.ForeignKey(
        CommentType,
        on_delete=models.CASCADE,
        null=True,
        related_name='subject_types'
    )
    from_email = models.TextField(_("from email"))
    recipient = models.TextField(_("recipient"))
    subject = models.TextField(_("subject"))
    body = models.TextField(_("body"))
    ok = models.BooleanField(_("ok"), default=False, db_index=True)
    date_sent = models.DateTimeField(_("date sent"), auto_now_add=True, db_index=True)

    objects = models.Manager()
    emailhistorycurrentmgr = EmailHistoryCurrentManager()

    def __str__(self):
        return "{s.recipient}: {s.subject}".format(s=self)

    class Meta:
        verbose_name = _("email")
        verbose_name_plural = _("emails")
        ordering = ("-date_sent",)
