from collections import defaultdict

from django.db import transaction
from django.db.models import Count, Max

from fairs.models import (
    Event,
    EventSite,
    InventoryItem,
    SiteAllocation,
    SiteHistory,
)

import logging

logger = logging.getLogger(__name__)

SYSTEM_USER_ID = 3


class SiteAllocationService:
    """
    Automatically allocate sites to existing stallholders based on
    up to four years of historical site usage.

    Allocation priority:

    1. Number of years occupying the site.
    2. Most recent occupancy.
    """

    @classmethod
    def allocate_sites(cls):

        events = list(
            Event.currenteventfiltermgr.all()
        )

        if not events:
            logger.error(
                "Site allocation aborted: no current events found."
            )
            return

        existing_allocations = cls._get_existing_allocations()

        site_preferences = cls._get_site_preferences()

        if not site_preferences:
            logger.error(
                "Site allocation aborted: no historical site data found."
            )
            return

        for minimum_years in range(4, 0, -1):

            cls._process_priority_group(
                minimum_years=minimum_years,
                site_preferences=site_preferences,
                events=events,
                existing_allocations=existing_allocations,
            )

        logger.info(
            "Historical site allocation completed successfully."
        )

    @staticmethod
    def _get_existing_allocations():
        """
        Cache existing allocations to eliminate repeated
        EXISTS queries.
        """

        return {
            (
                allocation.stallholder_id,
                allocation.event_site.event_id,
            )
            for allocation in SiteAllocation.objects.select_related(
                "event_site"
            )
        }

    @staticmethod
    def _get_site_preferences():
        """
        Returns historical site rankings.

        Example:

        {
            stallholder_id: [
                {
                    'site_id': 123,
                    'year_count': 4,
                    'latest_year': '2025'
                },
                ...
            ]
        }
        """

        queryset = (
            SiteHistory.fouryearhistorymgr
            .filter(
                stallholder__is_active=True
            )
            .values(
                "stallholder_id",
                "site_id",
            )
            .annotate(
                year_count=Count(
                    "year",
                    distinct=True,
                ),
                latest_year=Max("year"),
            )
            .order_by(
                "-year_count",
                "-latest_year",
            )
        )

        preferences = defaultdict(list)

        for row in queryset:

            preferences[
                row["stallholder_id"]
            ].append(
                {
                    "site_id": row["site_id"],
                    "year_count": row["year_count"],
                    "latest_year": row["latest_year"],
                }
            )

        return preferences

    @classmethod
    def _process_priority_group(
        cls,
        *,
        minimum_years,
        site_preferences,
        events,
        existing_allocations,
    ):
        """
        Process stallholders with at least
        minimum_years occupancy.
        """

        ranked_stallholders = []

        for stallholder_id, sites in site_preferences.items():

            qualifying_sites = [
                site
                for site in sites
                if (
                    site["year_count"] >= minimum_years
                    if minimum_years > 1
                    else site["year_count"] == 1
                )
            ]

            if not qualifying_sites:
                continue

            preferred_site = qualifying_sites[0]

            ranked_stallholders.append(
                (
                    stallholder_id,
                    preferred_site["year_count"],
                    preferred_site["latest_year"],
                    preferred_site["site_id"],
                )
            )

        ranked_stallholders.sort(
            key=lambda row: (
                row[1],
                row[2],
            ),
            reverse=True,
        )

        for (
            stallholder_id,
            _year_count,
            _latest_year,
            site_id,
        ) in ranked_stallholders:

            cls._allocate_site(
                stallholder_id=stallholder_id,
                site_id=site_id,
                events=events,
                existing_allocations=existing_allocations,
            )

    @classmethod
    def _allocate_site(
        cls,
        *,
        stallholder_id,
        site_id,
        events,
        existing_allocations,
    ):

        for event in events:

            if (
                stallholder_id,
                event.id,
            ) in existing_allocations:
                continue

            try:

                event_site = (
                    EventSite.objects
                    .select_related(
                        "site",
                        "event",
                        "site__site_size",
                    )
                    .get(
                        event_id=event.id,
                        site_id=site_id,
                        site__site_size__item_type=InventoryItem.FAIRSITE,
                    )
                )

            except EventSite.DoesNotExist:
                continue

            if event_site.site_status != 1:
                continue

            allocation_created = cls._create_allocation(
                stallholder_id=stallholder_id,
                event_site=event_site,
            )

            if allocation_created:

                existing_allocations.add(
                    (
                        stallholder_id,
                        event.id,
                    )
                )

    @staticmethod
    @transaction.atomic
    def _create_allocation(
        *,
        stallholder_id,
        event_site,
    ):
        """
        Atomic allocation.

        Returns:
            True if allocation created.
            False otherwise.
        """

        rows_updated = (
            EventSite.objects
            .filter(
                pk=event_site.pk,
                site_status=1,
            )
            .update(
                site_status=2
            )
        )

        if rows_updated == 0:
            return False

        SiteAllocation.objects.create(
            stallholder_id=stallholder_id,
            event_site=event_site,
            created_by_id=SYSTEM_USER_ID,
        )

        return True