from django.db import models

from fairs.models import PowerBox, ZoneMap

class PasspackQuerySet(models.QuerySet):

    def base_passpack_rows(self, stall_registration_id):

        from fairs.models import SiteAllocation

        return (
            SiteAllocation.objects
            .filter(stall_registration_id=stall_registration_id)
            .select_related(
                "event_site__event",
                "event_site__site__zone",
                "event_site__site__powerbox",
            )
            .values(
                "event_site__event__id",
                "event_site__event__event_name",
                "event_site__event__original_event_date",

                "event_site__site__site_name",
                "event_site__site__site_size__site_size",

                "event_site__site__zone__id",
                "event_site__site__zone__zone_name",
                "event_site__site__zone__trestle_source",

                "event_site__site__powerbox__power_box_description",
            )
            .order_by("event_site__event__original_event_date")
        )

def build_zone_logistics(zone_ids, fair_year):

    zone_maps = (
        ZoneMap.objects
        .filter(zone_id__in=zone_ids, year=str(fair_year))
        .values("zone_id", "map_pdf")
    )

    powerboxes = (
        PowerBox.objects
        .filter(site_powerbox__zone_id__in=zone_ids)
        .values(
            "site_powerbox__zone_id",
            "power_box_description"
        )
    )

    zone_map_lookup = {
        z["zone_id"]: z["map_pdf"]
        for z in zone_maps
    }

    power_lookup = {
        p["site_powerbox__zone_id"]: p["power_box_description"]
        for p in powerboxes
    }

    return zone_map_lookup, power_lookup


class PasspackManager(models.Manager):

    def get_queryset(self):
        return PasspackQuerySet(self.model, using=self._db)

    def build_passpack(self, stall_registration_id, current_fair):

        rows = list(
            self.get_queryset()
            .base_passpack_rows(stall_registration_id)
        )

        zone_ids = {
            r["event_site__site__zone__id"]
            for r in rows
        }

        zone_maps, powerboxes = build_zone_logistics(
            zone_ids,
            current_fair.fair_year,
        )

        result = []

        for r in rows:

            zone_id = r["event_site__site__zone__id"]

            result.append({
                "allocated_event_name":
                    r["event_site__event__event_name"],

                "allocated_site_name":
                    r["event_site__site__site_name"],

                "allocated_site_size":
                    r["event_site__site__site_size__site_size"],

                "allocated_site_location":
                    r["event_site__site__zone__zone_name"],

                "trestle_source":
                    r["event_site__site__zone__trestle_source"],

                "zone_map_path":
                    zone_maps.get(zone_id),

                "powerbox_description":
                    r["event_site__site__powerbox__power_box_description"],
            })

        return result

