# registration/services/billing.py

from decimal import Decimal
from dataclasses import dataclass

from fairs.models import InventoryItem, InventoryItemFair, SiteAllocation
from registration.models import AdditionalSiteRequirement


@dataclass
class BillableItem:
    inventory_item: InventoryItem
    quantity: Decimal
    unit_cost: Decimal

    @property
    def total(self):
        return self.quantity * self.unit_cost


class RegistrationBillingService:

    def __init__(self, fair):
        self.fair = fair

    # -----------------------------
    # helpers
    # -----------------------------

    def _is_persisted(self, registration):
        return registration.pk is not None

    def _price(self, inventory_item):
        item = InventoryItemFair.objects.get(
            fair=self.fair,
            inventory_item=inventory_item,
        )
        return item.price * item.price_rate

    def _price_by_name(self, name):
        inventory_item = InventoryItem.objects.get(item_name=name)
        return inventory_item, self._price(inventory_item)

    # -----------------------------
    # site size helper
    # -----------------------------

    def _get_site_size(self, registration):
        """
        Determine site size for billing.

        Priority:
        1. Allocated site (persisted registrations only)
        2. Requested site_size on registration
        """

        # ---- allocated site (update flow only)
        if self._is_persisted(registration):
            allocation = (
                SiteAllocation.currentallocationsmgr.filter(stall_registration=registration)
            )
            if not allocation.exists():
                # ---- requested site (create flow)
                return getattr(registration, "site_size", None)

            allocation = allocation.first()
            return allocation.inventory_item

    # -----------------------------
    # main builder
    # -----------------------------

    def build_items(self, registration):
        items = []

        # ---------------- SITE ----------------
        site_size = self._get_site_size(registration)
        if site_size:
            site_item = site_size

            items.append(
                BillableItem(
                    inventory_item=site_item,
                    quantity=Decimal(1),
                    unit_cost=self._price(site_item),
                )
            )

        # ---------------- CATEGORY ----------------
        category = registration.stall_category
        if category and category.has_inventory_item:
            items.append(
                BillableItem(
                    inventory_item=category.inventory_item,
                    quantity=Decimal(1),
                    unit_cost=self._price(category.inventory_item),
                )
            )

        # ---------------- TRESTLES ----------------
        if registration.trestle_quantity > 0:
            item, price = self._price_by_name("Trestle Table")

            items.append(
                BillableItem(
                    inventory_item=item,
                    quantity=Decimal(registration.trestle_quantity),
                    unit_cost=price,
                )
            )

        # ---------------- VEHICLE ----------------
        if registration.vehicle_length and registration.vehicle_length > 6:
            item, price = self._price_by_name("Over 6m vehicle on site")

            items.append(
                BillableItem(
                    inventory_item=item,
                    quantity=Decimal(1),
                    unit_cost=price,
                )
            )

        # ---------------- POWER (NEW MODEL) ----------------
        power_qty = 0

        if self._is_persisted(registration):
            power_qty = registration.power_connections.count()
        else:
            # create-form preview calculation
            if (
                registration.uses_electrical_equipment
                and registration.power_source == "fair"
            ):
                power_qty = (
                    (registration.caravan_socket_16a or 0)
                    + (registration.three_pin_15a or 0)
                )

        if power_qty:
            item, price = self._price_by_name("Power Point")

            items.append(
                BillableItem(
                    inventory_item=item,
                    quantity=Decimal(power_qty),
                    unit_cost=price,
                )
            )

        # ---------------- ADDITIONAL SITES ----------------
        additional_sites = []

        if self._is_persisted(registration):
            additional_sites = AdditionalSiteRequirement.objects.filter(
                stall_registration=registration
        )

        for extra in additional_sites:
            items.append(
                BillableItem(
                    inventory_item=extra.site_size,
                    quantity=Decimal(extra.site_quantity),
                    unit_cost=self._price(extra.site_size),
                )
            )

        return items

    # -----------------------------
    # total calculator
    # -----------------------------

    def calculate_total(self, registration):

        if registration.pk:
            items = self.build_items_from_db(registration)
        else:
            items = self.build_items_from_form(registration)

        return self.sum_items(items)


    # -----------------------------
    # main builder
    # -----------------------------

    def build_items(self, registration):
        items = []

        # ---------------- SITE ----------------
        site_size = self._get_site_size(registration)
        if site_size:
            site_item = site_size

            items.append(
                BillableItem(
                    inventory_item=site_item,
                    quantity=Decimal(1),
                    unit_cost=self._price(site_item),
                )
            )

        # ---------------- CATEGORY ----------------
        category = registration.stall_category
        if category and category.has_inventory_item:
            items.append(
                BillableItem(
                    inventory_item=category.inventory_item,
                    quantity=Decimal(1),
                    unit_cost=self._price(category.inventory_item),
                )
            )

        # ---------------- TRESTLES ----------------
        if registration.trestle_quantity > 0:
            item, price = self._price_by_name("Trestle Table")

            items.append(
                BillableItem(
                    inventory_item=item,
                    quantity=Decimal(registration.trestle_quantity),
                    unit_cost=price,
                )
            )

        # ---------------- VEHICLE ----------------
        if registration.vehicle_length and registration.vehicle_length > 6:
            item, price = self._price_by_name("Over 6m vehicle on site")

            items.append(
                BillableItem(
                    inventory_item=item,
                    quantity=Decimal(1),
                    unit_cost=price,
                )
            )

        # ---------------- POWER ----------------
        power_qty = 0

        if self._is_persisted(registration):
            power_qty = registration.power_connections.count()
            print("Registration Power Point qty", power_qty)
        else:
            # create-form preview calculation
            if (
                    registration.uses_electrical_equipment
                    and registration.power_source == "fair"
            ):
                power_qty = (
                        (registration.caravan_socket_16a or 0)
                        + (registration.three_pin_15a or 0)
                )
            print("Form  Power Point qty", power_qty)

        print("Power Point Qty", power_qty)

        if power_qty:
            item, price = self._price_by_name("Power Point")

            print("Power item and price", item, price)

            items.append(
                BillableItem(
                    inventory_item=item,
                    quantity=Decimal(power_qty),
                    unit_cost=price,
                )
            )

        # ---------------- ADDITIONAL SITES ----------------
        additional_sites = []

        if self._is_persisted(registration):
            additional_sites = AdditionalSiteRequirement.objects.filter(
                stall_registration=registration
        )

        for extra in additional_sites:
            items.append(
                BillableItem(
                    inventory_item=extra.site_size,
                    quantity=Decimal(extra.site_quantity),
                    unit_cost=self._price(extra.site_size),
                )
            )

        return items

    # -----------------------------
    # total calculator
    # -----------------------------

    def calculate_total(self, registration):
        items = self.build_items(registration)
        return sum(i.total for i in items), items