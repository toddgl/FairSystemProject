# fairs/services/message_dashboard_service.py

from dataclasses import dataclass
from registration.models import (
    RegistrationComment,
)


@dataclass
class MessageFilters:
    """
    Holds all filter information required by the messages dashboard
     view.
    """
    queryset_filters: dict
    selected_stallholder: int | None
    selected_fair: object | None
    comment_type: str | None
    is_active: bool | False
    is_done: bool | False
    is_archived: bool | False
    alert_message: str
    filter_message: str

class MessageDashboardService:
    """
    Business logic for the Message Dashboard view.
    """

    @classmethod
    def get_filters(
            cls,
            *,
            fair,
            stallholder_id,
            comment_type,
            is_active,
            is_done,
            is_archived,
            current_fair,

    ):
        """
        Build the queryset filters.

        Parameters are plain Python values rather than
        Django requests or forms.
        """

        queryset_filters = {}
        filter_message = "Showing current messages of the current fair"

        #
        # Fair
        #
        if fair:
            queryset_filters["fair"] = fair
            selected_fair = fair.pk
            filter_message = f"Showing active messages for fair {fair}"
        else:
            selected_fair = None

        #
        # Stallholder
        #
        if stallholder_id is not None:
            queryset_filters["stallholder_id"] = stallholder_id

        #
        # Comment Type
        #
        if comment_type:
            queryset_filters["comment_type"] = comment_type
            alert_message = (
                "There are no messages matching "
                "the selected comment type."
            )
            filter_message += f", comment type {comment_type}"
        else:
            alert_message = "There are no messages created yet."

        if is_active:
            queryset_filters['is_active'] = True
            queryset_filters['is_archived'] = False
            filter_message += ", under action"

        if is_done:
            queryset_filters['is_done'] = True
            queryset_filters['is_archived'] = False
            filter_message += ", resolved"

        if is_archived:
            queryset_filters['is_archived'] = True
            filter_message += ", archived"

        #
        # Default Fair
        #
        if not queryset_filters:
            queryset_filters["fair"] = current_fair
            queryset_filters["is_active"] = True
            queryset_filters["is_archived"] = False

        return MessageFilters(
            queryset_filters=queryset_filters,
            selected_fair=selected_fair,
            selected_stallholder=stallholder_id,
            comment_type=comment_type,
            is_active=is_active,
            is_done=is_done,
            is_archived=is_archived,
            alert_message=alert_message,
            filter_message=filter_message,
        )

    @classmethod
    def get_queryset(cls, filters):
        """
        Return the filtered Email queryset.
        """

        return (
            RegistrationComment.objects
            .filter(**filters.queryset_filters)
            .order_by("-date_created")
        )