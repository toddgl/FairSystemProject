# utils/find_missing_power_connections.py


"""
Find current stall registrations that request fair-supplied power
but have no associated PowerConnection records.

Read-only utility: does not modify the database.

Run from the Django project root with venv activated:
    python manage.py shell < utils/find_missing_power_connections.py
"""

from registration.models import StallRegistration


def find_missing_power_connections():
    """
    Report registrations with power_source='fair' and no related
    PowerConnection records.
    """

    registrations = (
        StallRegistration.objects
        .filter(power_source="fair")
        .filter(power_connections__isnull=True)
        .select_related("stallholder")
        .order_by("id")
        .distinct()
    )

    print("\nRegistrations requesting fair power without connections")
    print("=" * 75)

    count = 0

    for registration in registrations.iterator():
        stallholder = registration.stallholder

        first_name = stallholder.first_name or ""
        last_name = stallholder.last_name or ""

        print(
            f"Registration ID: {registration.id:<8} "
            f"Stallholder: {first_name} {last_name}".rstrip()
        )

        count += 1

    print("=" * 75)
    print(f"Total registrations missing power connections: {count}")


find_missing_power_connections()