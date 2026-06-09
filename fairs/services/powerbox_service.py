import math

from django.db.models import (
    Count,
    Sum,
    F,
    Value,
)
from django.db.models.functions import Coalesce

from registration.models import StallRegistration, FoodPrepEquipReq


class PowerboxReportService:
    """
    Service class for Powerbox reporting.

    Provides:
        - Aggregated powerbox statistics
        - Detailed stall registration data
        - Filtering
    """

    @staticmethod
    def apply_filters(data, filters):
        """
        Apply saved filter selections to report data.
        """

        if filters.get("eventid"):
            event_id = int(filters["eventid"])
            data = [
                item
                for item in data
                if item["site_allocation__event_site__event__id"] == event_id
            ]

        if filters.get("powerboxid"):
            powerbox_id = int(filters["powerboxid"])
            data = [
                item
                for item in data
                if item["site_allocation__event_site__site__powerbox__id"]
                == powerbox_id
            ]

        if filters.get("stallholderid"):
            stallholder_id = int(filters["stallholderid"])
            data = [
                item
                for item in data
                if item["stallholderid"] == stallholder_id
            ]

        return data

    @staticmethod
    def get_aggregated_powerboxes():
        """
        Returns powerbox totals grouped by event/powerbox.
        """

        return (
            StallRegistration.registrationcurrentmgr
            .fair_power()
            .filter(
                site_allocation__event_site__site__powerbox__isnull=False
            )
            .values(
                "site_allocation__event_site__site__powerbox__id",
                "site_allocation__event_site__event__id",
                "site_allocation__event_site__event__event_name",
                "site_allocation__event_site__site__powerbox__power_box_name",
                "site_allocation__event_site__site__powerbox__socket_count",
                "site_allocation__event_site__site__powerbox__caravan_socket_16a",
                "site_allocation__event_site__site__powerbox__three_pin_15a",
            )
            .annotate(
                used_caravan=Coalesce(
                    Sum("caravan_socket_16a"),
                    Value(0)
                ),
                used_three_pin=Coalesce(
                    Sum("three_pin_15a"),
                    Value(0)
                ),
                connected_sites=Count("id"),
            )
            .annotate(
                free_caravan=
                F(
                    "site_allocation__event_site__site__powerbox__caravan_socket_16a"
                )
                - F("used_caravan"),

                free_three_pin=
                F(
                    "site_allocation__event_site__site__powerbox__three_pin_15a"
                )
                - F("used_three_pin"),

                free_sockets=
                F(
                    "site_allocation__event_site__site__powerbox__socket_count"
                )
                - Count("id"),
            )
            .order_by(
                "site_allocation__event_site__site__powerbox__power_box_name"
            )
        )

    @staticmethod
    def get_detailed_stallregistrations():
        """
        Base detail rows.
        """

        return (
            StallRegistration.registrationcurrentmgr
            .fair_power()
            .filter(
                site_allocation__event_site__site__powerbox__isnull=False
            )
            .annotate(
                power_box_name=F(
                    "site_allocation__event_site__site__powerbox__power_box_name"
                ),
                event_name=F(
                    "site_allocation__event_site__event__event_name"
                ),
                allocated_site_name=F(
                    "site_allocation__event_site__site__site_name"
                ),
                stallholderid=F("stallholder__id"),
            )
            .values(
                "id",
                "stallholderid",
                "allocated_site_name",
                "power_box_name",
                "event_name",
                "site_allocation__event_site__event__id",
                "site_allocation__event_site__site__powerbox__id",
            )
        )

    @staticmethod
    def get_report_data():
        """
        Returns fully merged report data.
        """

        aggregated = PowerboxReportService.get_aggregated_powerboxes()

        agg_lookup = {
            (
                row[
                    "site_allocation__event_site__site__powerbox__id"
                ],
                row[
                    "site_allocation__event_site__event__id"
                ],
            ): row
            for row in aggregated
        }

        detailed = (
            PowerboxReportService
            .get_detailed_stallregistrations()
        )

        results = []

        for sr in detailed:

            key = (
                sr[
                    "site_allocation__event_site__site__powerbox__id"
                ],
                sr[
                    "site_allocation__event_site__event__id"
                ],
            )

            agg = agg_lookup.get(key, {})

            total_power_load_amps = (
                FoodPrepEquipReq.objects.filter(
                    food_registration__registration__site_allocation__event_site__event_id=
                    sr[
                        "site_allocation__event_site__event__id"
                    ],
                    food_registration__registration__site_allocation__event_site__site__powerbox__id=
                    sr[
                        "site_allocation__event_site__site__powerbox__id"
                    ],
                    food_registration__registration__stallholder_id=
                    sr["stallholderid"],
                )
                .aggregate(
                    total_amps=Sum(
                        F("equipment_quantity")
                        * F(
                            "food_prep_equipment__power_load_amps"
                        )
                    )
                )["total_amps"]
                or 0
            )

            results.append(
                {
                    **sr,
                    "connected_sites": agg.get(
                        "connected_sites",
                        0,
                    ),
                    "free_sockets": agg.get(
                        "free_sockets",
                        0,
                    ),
                    "used_caravan": agg.get(
                        "used_caravan",
                        0,
                    ),
                    "used_three_pin": agg.get(
                        "used_three_pin",
                        0,
                    ),
                    "free_caravan": agg.get(
                        "free_caravan",
                        0,
                    ),
                    "free_three_pin": agg.get(
                        "free_three_pin",
                        0,
                    ),
                    "total_power_load_amps": math.ceil(
                        total_power_load_amps
                    ),
                }
            )

        return results