# utils/delete_unregistered_allocations.py

import logging
from fairs.models import (
    SiteAllocation,
)

db_logger = logging.getLogger('db')

unregistered_allocations = SiteAllocation.objects.filter(stall_registration__isnull=True, on_hold=False)
if unregistered_allocations:
        try:
            unregistered_allocations.delete()
        except Exception as e:          # It will catch other errors related to the delete call.
            db_logger.error('There was an error deleting the unregistered site allocations.'+ e,  extra={'custom_category':'Site Allocations'})