from django.db.models import Count, Max

from fairs.models import (
    SiteAllocation,
    SiteHistory,
)


class SiteAllocationAuditService:
    """
    Produces a report showing sites that have changed hands
    compared with the most recent historical occupant.

    One row per site.
    """

    @classmethod
    def get_changed_allocations(cls):

        rows = []

        allocations = (
            SiteAllocation.currentallocationsmgr
            .select_related(
                "stallholder",
                "event_site__site__zone",
                "event_site__site__site_size",
            )
            .order_by(
                "event_site__site__zone__zone_name",
                "event_site__site__site_name",
            )
        )

        #
        # Build lookup tables
        #
        latest_history_lookup = cls._build_latest_history_lookup()
        years_held_lookup = cls._build_years_held_lookup()
        last_occupied_lookup = cls._build_last_occupied_lookup()

        #
        # Prevent duplicate rows caused by multiple events
        #
        processed_sites = set()

        for allocation in allocations:

            site = allocation.event_site.site

            if site.id in processed_sites:
                continue

            processed_sites.add(site.id)

            previous_history = latest_history_lookup.get(site.id)

            if previous_history is None:
                continue

            current_holder_last_year = (
                last_occupied_lookup.get(
                    (
                        site.id,
                        allocation.stallholder_id,
                    )
                )
            )

            if previous_history.stallholder_id == allocation.stallholder_id:
                continue

            years_held = years_held_lookup.get(
                (site.id, allocation.stallholder_id),
                0,
            )

            rows.append(
                {
                    "zone_name": (
                        site.zone.zone_name
                        if site.zone
                        else "No Zone"
                    ),
                    "site_name": site.site_name,
                    "site_size": (
                        site.site_size.item_name
                        if site.site_size
                        else ""
                    ),
                    "current_stallholder_id": allocation.stallholder_id,
                    "last_year_occupied": current_holder_last_year,
                    "count_years_occupied": years_held,
                    "previous_stallholder_id": previous_history.stallholder_id,
                }
            )

        return rows

    @staticmethod
    def _build_latest_history_lookup():
        """
        Returns:

        {
            site_id: SiteHistory
        }

        containing only the most recent SiteHistory
        record for each site.
        """

        latest_years = (
            SiteHistory.objects
            .values("site_id")
            .annotate(
                latest_year=Max("year")
            )
        )

        latest_lookup = {}

        #
        # Build quick lookup:
        # {site_id: latest_year}
        #
        site_year_lookup = {
            row["site_id"]: row["latest_year"]
            for row in latest_years
        }

        histories = (
            SiteHistory.objects
            .select_related(
                "stallholder",
                "site",
            )
        )

        for history in histories:

            if (
                site_year_lookup.get(history.site_id)
                == history.year
            ):
                latest_lookup[history.site_id] = history

        return latest_lookup

    @staticmethod
    def _build_years_held_lookup():
        """
        Returns:

        {
            (site_id, stallholder_id): years_held
        }

        Years held is based on distinct years rather than
        SiteHistory records, since there may be multiple
        events per year.
        """

        history_counts = (
            SiteHistory.objects
            .values(
                "site_id",
                "stallholder_id",
            )
            .annotate(
                year_count=Count(
                    "year",
                    distinct=True,
                )
            )
        )

        return {
            (
                row["site_id"],
                row["stallholder_id"],
            ): row["year_count"]
            for row in history_counts
        }


    @staticmethod
    def _build_last_occupied_lookup():
        """
        Returns:

        {
            (site_id, stallholder_id): latest_year
        }
        """

        records = (
            SiteHistory.objects
            .values(
                "site_id",
                "stallholder_id",
            )
            .annotate(
                last_year=Max("year")
            )
        )

        return {
            (
                row["site_id"],
                row["stallholder_id"],
            ): row["last_year"]
            for row in records
        }