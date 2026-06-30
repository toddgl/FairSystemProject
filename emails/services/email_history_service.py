# emails/services/emai_history_service.py

from dataclasses import dataclass
from emails.models import Email


@dataclass
class EmailHistoryFilters:
    """
    Holds all filter information required by the
    Email History view.
    """
    queryset_filters: dict
    selected_stallholder: int | None
    selected_fair: object | None
    subject_type: str | None
    alert_message: str

class EmailHistoryService:
    """
    Business logic for the Email History report.
    """

    @classmethod
    def get_filters(
            cls,
            *,
            fair,
            stallholder_id,
            subject_type,
            current_fair,
    ):
        """
        Build the queryset filters.

        Parameters are plain Python values rather than
        Django requests or forms.
        """

        queryset_filters = {}

        #
        # Fair
        #
        if fair:
            queryset_filters["fair"] = fair
            selected_fair = fair.pk
        else:
            selected_fair = None

        #
        # Stallholder
        #
        if stallholder_id is not None:
            queryset_filters["stallholder_id"] = stallholder_id

        if stallholder_id:
            queryset_filters["stallholder_id"] = stallholder_id

        #
        # Subject Type
        #
        if subject_type:
            queryset_filters["subject_type_id"] = subject_type
            alert_message = (
                "There are no email messages matching "
                "the selected subject type."
            )
        else:
            alert_message = "There are no emails created yet."

        #
        # Default Fair
        #
        if not queryset_filters:
            queryset_filters["fair"] = current_fair
            selected_fair = current_fair.pk

        return EmailHistoryFilters(
            queryset_filters=queryset_filters,
            selected_fair=selected_fair,
            selected_stallholder=stallholder_id,
            subject_type=subject_type,
            alert_message=alert_message,
        )

    @classmethod
    def get_queryset(cls, filters):
        """
        Return the filtered Email queryset.
        """

        return (
            Email.objects
            .filter(**filters.queryset_filters)
            .order_by("-date_sent")
        )