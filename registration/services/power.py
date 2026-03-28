# registration/services/power.py

from registration.models import PowerConnection, PowerConnectionType


def sync_legacy_power_flag(registration):
    """
    Temporary compatibility bridge.

    Keeps legacy `power_required` field aligned
    with new PowerConnection model.
    """

    has_fair_power = registration.power_connections.filter(
        connection_type=PowerConnectionType.FAIR_15A
    ).exists()

    registration.power_required = has_fair_power