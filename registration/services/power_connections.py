
# registration/services/power_connections.py


from django.db import transaction

from registration.models import (
    StallRegistration,
    PowerConnection,
    PowerConnectionType,
    GeneratorApprovalStatus,
    PowerSource,
)


@transaction.atomic
def sync_power_connections(registration):
    """
    Synchronise a saved StallRegistration's power selections with its
    PowerConnection records.

    Existing generator approval status is preserved when the generator
    request remains active.
    """

    # Lock the registration while synchronising its power connections.
    registration = (
        StallRegistration.objects
        .select_for_update()
        .get(pk=registration.pk)
    )

    desired = {}

    if registration.uses_electrical_equipment:
        if registration.power_source == PowerSource.FAIR:
            if registration.caravan_socket_16a:
                desired[PowerConnectionType.FAIR_16A] = (
                    registration.caravan_socket_16a
                )

            if registration.three_pin_15a:
                desired[PowerConnectionType.FAIR_15A] = (
                    registration.three_pin_15a
                )

        elif registration.power_source == PowerSource.BATTERY:
            desired[PowerConnectionType.SOLID_STATE] = 1

        elif registration.power_source == PowerSource.GENERATOR:
            desired[PowerConnectionType.GENERATOR_REQUEST] = 1

    existing_connections = list(
        PowerConnection.objects
        .filter(registration=registration)
        .order_by("pk")
    )

    # Index existing connections by type. Normally there should be only
    # one record of each type for a registration.
    existing = {}

    for connection in existing_connections:
        if connection.connection_type not in existing:
            existing[connection.connection_type] = connection
        else:
            # Remove duplicate records of the same type.
            # Consider reviewing any existing duplicate generator records
            # manually before enabling this behaviour in production.
            raise ValueError(
                f"Duplicate power connections found for registration "
                f"{registration.pk}: {connection.connection_type}"
            )

    # Remove connections no longer selected by the registration.
    obsolete_types = set(existing) - set(desired)

    if obsolete_types:
        PowerConnection.objects.filter(
            registration=registration,
            connection_type__in=obsolete_types,
        ).delete()

    # Create missing records or update their quantities.
    for connection_type, quantity in desired.items():
        connection = existing.get(connection_type)

        if connection is None:
            PowerConnection.objects.create(
                registration=registration,
                connection_type=connection_type,
                quantity=quantity,
                generator_status=(
                    GeneratorApprovalStatus.PENDING
                    if connection_type
                    == PowerConnectionType.GENERATOR_REQUEST
                    else GeneratorApprovalStatus.NOT_REQUIRED
                ),
            )

        elif connection.quantity != quantity:
            connection.quantity = quantity
            connection.save(update_fields=["quantity"])
