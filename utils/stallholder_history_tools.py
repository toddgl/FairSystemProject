# utils/stallholder_history_tools.py

import logging
from fairs.models import (
    SiteHistory,
    InventoryItem,
)

db_logger = logging.getLogger('db')


def update_site_history_site_size():
    """
    A temporary function to populate the new site_size field based on the data  in the is_half_size flag. Where the
    is_half_size flag is true site_size will be set to 'Half Size Fair Site', if not set  site_size will be set
    to 'Full Size Fair Site'.
    Added to dashboard_site_history.html to initiate this function
    <div class="card-body">
        <p class="card-text">Update Site History Site Size</p>
        <form method="post">
            {% csrf_token %}
            <button class= "bth btn-primary mb-1" type="submit" name="run_script">Run Update</button>
        </form>
    </div>
    Added to Fairs view stallholder_history_dashboard_view
    if request.method == 'POST' and 'run_script' in request.POST:
        # call function
        update_site_history_site_size()
        # return user to required page
        return HttpResponseRedirect(reverse('fair:history-dashboard'))
    """
    # Get the SiteHistory
    site_histories = SiteHistory.objects.all()
    half_inventory_item = InventoryItem.objects.get(item_name='Half Size Fair Site')
    full_inventory_item = InventoryItem.objects.get(item_name='Full Size Fair Site')
    for site_history in site_histories:
        is_half_size = site_history.is_half_size
        # Determine the required site size based on the is_half_size flag
        inventory_item = half_inventory_item if is_half_size else full_inventory_item
        try:
            site_history.site_size = inventory_item
            site_history.save()
        except Exception as e:
            db_logger.error(
                'There was an error updating the SiteHistory instanceID {} ' + str(e) + ' .'.format(site_history.id),
                extra={'custom_category': 'Site_history_Update'})
        else:
            db_logger.error('Site history ID {} has been updated to set site_size.id to {}'.format(site_history.id,
                                                                                                inventory_item.id),
                            extra={'custom_category': 'Site_history_Update'})
