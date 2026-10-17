# utils/create_generator_power_connections.py

"""
Create missing pending generator PowerConnection records for the 2027 fair.

Run from the Django project root:

    python utils/create_generator_power_connections.py --dry-run
    python utils/create_generator_power_connections.py
"""

import os
import sys
import argparse

import django
from django.db import transaction

# Ensure the Django project root is on the Python path.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# IMPORTANT: Replace "your_project.settings" with your actual settings module.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from registration.models import (  # noqa: E402
    StallRegistration,
    PowerConnection,
    PowerConnectionType,
    GeneratorApprovalStatus,
    PowerSource,
)


def create_generator_connections(year=2027, dry_run=False):
    """
    Find registrations for the specified fair year that selected GENERATOR
    and create a missing pending generator PowerConnection.

    Existing generator connections are never overwritten.
    """

    # Assumes Fair has a numeric `year` field.
    registrations = StallRegistration.objects.filter(
        fair__fair_year=year,
        uses_electrical_equipment=True,
        power_source=PowerSource.GENERATOR,
    ).order_by("pk")

    total = registrations.count()
    created = 0
    existing = 0

    print(f"Fair year: {year}")
    print(f"Generator applications found: {total}")
    print(f"Mode: {'DRY RUN - no database changes' if dry_run else 'LIVE'}")
    print("-" * 60)

    for registration in registrations.iterator():
        # Check only the generator connection for this registration.
        connection_exists = PowerConnection.objects.filter(
            registration=registration,
            connection_type=PowerConnectionType.GENERATOR_REQUEST,
        ).exists()

        if connection_exists:
            existing += 1
            print(
                f"SKIP registration {registration.pk}: "
                "generator connection already exists"
            )
            continue

        print(
            f"{'WOULD CREATE' if dry_run else 'CREATE'} "
            f"registration {registration.pk}: pending generator approval"
        )

        if not dry_run:
            with transaction.atomic():
                # Recheck inside the transaction to reduce the risk of
                # creating duplicates if another process runs concurrently.
                connection, was_created = PowerConnection.objects.get_or_create(
                    registration=registration,
                    connection_type=PowerConnectionType.GENERATOR_REQUEST,
                    defaults={
                        "quantity": 1,
                        "generator_status": GeneratorApprovalStatus.PENDING,
                    },
                )

            if was_created:
                created += 1
            else:
                existing += 1
                print(
                    f"  SKIP: connection {connection.pk} "
                    "was created by another process"
                )
        else:
            created += 1

    print("-" * 60)
    print(f"Applications checked: {total}")
    print(f"{'Would create' if dry_run else 'Created'}: {created}")
    print(f"Already existed: {existing}")

    if dry_run:
        print("\nDry run complete. No database records were changed.")


def main():
    parser = argparse.ArgumentParser(
        description="Create missing pending generator PowerConnection records."
    )
    parser.add_argument(
        "--year",
        type=int,
        default=2027,
        help="Fair year to process (default: 2027).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report changes without writing to the database.",
    )

    args = parser.parse_args()
    create_generator_connections(year=args.year, dry_run=args.dry_run)


if __name__ == "__main__":
    main()