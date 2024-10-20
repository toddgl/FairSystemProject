# fairs/views.py
import datetime
import os
import logging
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_http_methods
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect, HttpResponse, FileResponse, Http404, HttpResponseNotFound
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404,redirect, render
from django.urls import reverse_lazy, reverse
from collections import defaultdict
from django.db import transaction
from django.views.generic import (
    CreateView,
    FormView,
    ListView,
    UpdateView,
    DeleteView,
)

from fairs.models import (
    Fair,
    Event,
    EventSite,
    Site,
    SiteAllocation,
    Location,
    Zone,
    ZoneMap,
    InventoryItem,
    InventoryItemFair,
    PowerBox,
    EventPower,
    SiteHistory,
)

from registration.models import (
    StallRegistration,
    RegistrationComment,
    AdditionalSiteRequirement
)

from utils.site_allocation_tools import (
    site_allocations,
    site_allocation_emails,
    delete_unregistered_allocations
)

from utils.stallholder_history_tools import(
    update_site_history_site_size
)

from .forms import (
    FairDetailForm,
    FairCreateForm,
    EventCreateForm,
    EventDetailForm,
    SiteListFilterForm,
    SiteCreateForm,
    SiteDetailForm,
    SiteAllocationListFilterForm,
    SiteAllocationFilterForm,
    SiteAllocationCreateForm,
    SiteAllocationUpdateForm,
    StallHolderIDForm,
    LocationCreateForm,
    LocationUpdateForm,
    ZoneCreateForm,
    ZoneDetailForm,
    ZoneMapCreateForm,
    ZoneMapDetailForm,
    InventoryItemCreateForm,
    InventoryItemDetailForm,
    EventSiteDetailForm,
    EventSiteCreateForm,
    EventSiteListFilterForm,
    InventoryItemFairDetailForm,
    InventoryItemFairCreateForm,
    DashboardSiteFilterForm,
    PowerBoxCreateForm,
    PowerBoxUpdateDetailForm,
    EventPowerCreateForm,
    EventPowerUpdateDetailForm,
    DashboardRegistrationFilterForm,
    MessageFilterForm,
    MessageReplyForm,
    SiteHistoryFilerForm,
    SiteAllocationFilerForm
)

from registration.forms import (
    CommentFilterForm,
)


# Global Variables
current_year = datetime.datetime.now().year
current_month = datetime.datetime.now().month
next_year = current_year + 1
media_root = settings.MEDIA_ROOT
site_status_dict = {
    1: 'Available',
    2: 'Allocated',
    3: 'Pending',
    4: 'Booked',
    5: 'Unavailable',
    6: 'Archived'
}
db_logger = logging.getLogger('db')


# Create your views here.

class LocationCreateView(PermissionRequiredMixin, CreateView):
    """
    Create a Location
    """
    permission_required = 'fairs.add_location'
    model = Location
    form_class = LocationCreateForm
    template_name = 'locations/location_create.html'
    success_url = reverse_lazy('fair:location-list')


class LocationListView(PermissionRequiredMixin, ListView):
    """
    List all locations
    """
    permission_required = "fairs.view_location"
    model = Location
    template_name = 'locations/location_list.html'
    queryset = Location.objects.all()


class LocationDetailUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Display an editable form of Fair Locations
    """
    permission_required = 'fairs.change_location'
    model = Location
    form_class = LocationUpdateForm
    template_name = 'locations/location_detail.html'
    success_url = reverse_lazy('fair:location-list')


class FairCreateView(PermissionRequiredMixin, CreateView):
    """
    Create a fair including recording who created it
    """
    permission_required = 'fairs.add_fair'
    model = Fair
    form_class = FairCreateForm
    template_name = 'fairs/fair_create.html'
    success_url = reverse_lazy('fair:fair-list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_initial(self, *args, **kwargs):
        initial = super(FairCreateView, self).get_initial(**kwargs)
        initial['fair_name'] = 'My Fair'
        return initial

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(FairCreateView, self).get_form_kwargs(*args, **kwargs)
        kwargs['created_by'] = self.request.user
        return kwargs


class FairListView(PermissionRequiredMixin, ListView):
    """
    List all fairs in the system by created date
    """
    permission_required = 'fairs.view_fair'
    model = Fair
    template_name = 'fairs/fair_list.html'
    queryset = Fair.objects.all().order_by("-date_created")


class FairDetailUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Display an editable form of the details of a fair
    """
    permission_required = 'fairs.change_fair'
    model = Fair
    form_class = FairDetailForm
    template_name = 'fairs/fair_detail.html'
    success_url = reverse_lazy('fair:fair-list')

    def get_context_data(self, **kwargs):
        context = super(FairDetailUpdateView, self).get_context_data(**kwargs)
        # Refresh the obj from the database in case the form validation changed it
        obj = self.get_object()
        context['obj'] = context['fair'] = obj
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.updated_by = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class EventCreateView(PermissionRequiredMixin, CreateView):
    """
    Create an Event including recording who created it
    """
    permission_required = 'fairs.add_event'
    model = Event
    form_class = EventCreateForm
    template_name = 'events/event_create.html'
    success_url = reverse_lazy('fair:event-list')

    def generate_event_sites(self, *args, **kwargs):
        """
        Create the event site relationship with the just created event and all sites
        """
        sites = Site.objects.filter(is_active=True) # Only create EventSite instances for sites that are active
        objs = [
            EventSite(
                event=self.object,
                site=site,
                site_status=1,
            )
            for site in sites
        ]
        EventSite.objects.bulk_create(objs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()
        self.generate_event_sites()
        # return HttpResponseRedirect(self.get_success_url())
        return super(EventCreateView, self).form_valid(form)

    def get_initial(self, *args, **kwargs):
        initial = super(EventCreateView, self).get_initial(**kwargs)
        return initial

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(EventCreateView, self).get_form_kwargs(*args, **kwargs)
        kwargs['created_by'] = self.request.user
        return kwargs


class EventListView(PermissionRequiredMixin, ListView):
    """
    List all events in the system by created date
    """
    permission_required = 'fairs.view_event'
    model = Event
    template_name = 'events/event_list.html'
    queryset = Event.objects.all().order_by("-date_created")


class EventDetailUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Display an editable form of the details of an event
    """
    permission_required = 'fairs.change_event'
    model = Event
    form_class = EventDetailForm
    template_name = 'events/event_detail.html'
    success_url = reverse_lazy('fair:event-list')

    def get_context_data(self, **kwargs):
        context = super(EventDetailUpdateView, self).get_context_data(**kwargs)
        # Refresh the obj from the database in case the form validation changed it
        obj = self.get_object()
        context['obj'] = context['event'] = obj
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.updated_by = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class SiteListView(PermissionRequiredMixin, ListView):
    """
    List all sites in the system by created date
    """
    permission_required = 'fairs.view_site'
    model = Site
    template_name = 'sites/site_list.html'
    paginate_by = 12
    queryset = Site.objects.all().order_by("site_name")


@login_required
@permission_required('fairs.add_site', raise_exception=True)
@permission_required('fairs.change_site', raise_exception=True)
def site_listview(request):
    """
    List all the sites and provide filtered views based on a dropdown filter of Zones
    """
    global filter_dict
    alert_message = 'There are no sites created yet.'
    template_name = 'sites/site_list.html'
    filterform = SiteListFilterForm(request.POST or None)
    # filtered_data = Site.objects.all().order_by("site_name")
    cards_per_page = 9

    if not request.htmx:
        filter_dict = {}

    elif request.htmx:
        if filterform.is_valid():
            zone = filterform.cleaned_data['zone']
            site_size = filterform.cleaned_data['site_size']
            attr_zonesite = 'zone'
            attr_site_size = 'site_size'
            if zone and site_size:
                alert_message = 'There are no sites where the zone is ' + str(zone) + ' the site size is ' + str(site_size)
                filter_dict = {
                    attr_zonesite: zone,
                    attr_site_size: site_size
                }
            elif zone:
                alert_message = 'There are no sites where the zone is ' + str(zone)
                filter_dict = {
                    attr_zonesite: zone
                }
            elif site_size:
                alert_message = 'There are no sites where the site size is ' + str(site_size)
                filter_dict = {
                    attr_site_size: site_size
                }
            else:
                alert_message = 'There are no event sites created yet.'
                filter_dict = {}
            filtered_data = Site.objects.filter(**filter_dict).order_by("site_name")
            template_name = 'sites/site_list_partial.html'
            page_list, page_range = pagination_data(cards_per_page, filtered_data, request)
            site_list = page_list
            return TemplateResponse(request, template_name, {
                'site_list': site_list,
                'page_range': page_range,
                'alert_mgr': alert_message,
            })
        filtered_data = Site.objects.filter(**filter_dict).order_by("site_name")
        template_name = 'sites/site_list_partial.html'
        page_list, page_range = pagination_data(cards_per_page, filtered_data, request)
        site_list = page_list
        return TemplateResponse(request, template_name, {
            'site_list': site_list,
            'page_range': page_range,
            'alert_mgr': alert_message,
        })
    filtered_data = Site.objects.filter(**filter_dict).order_by("site_name")
    page_list, page_range = pagination_data(cards_per_page, filtered_data, request)
    site_list = page_list
    return TemplateResponse(request, template_name, {
        'filterform': filterform,
        'site_list': site_list,
        'page_range': page_range,
        'alert_mgr': alert_message,
    })



class SiteDetailUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Display an editable form of the details of a site
    """
    permission_required = 'fairs.change_site'
    model = Site
    form_class = SiteDetailForm
    template_name = 'sites/site_detail.html'
    success_url = reverse_lazy('fair:site-list')

    def get_context_data(self, **kwargs):
        context = super(SiteDetailUpdateView, self).get_context_data(**kwargs)
        # Refresh the obj from the database in case the form validation changed it
        obj = self.get_object()
        context['obj'] = context['site'] = obj
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.updated_by = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class SiteCreateView(PermissionRequiredMixin, CreateView):
    """
    Create a Site including recording who created it
    """
    permission_required = 'fairs.add_site'
    model = Site
    form_class = SiteCreateForm
    template_name = 'sites/site_create.html'
    success_url = reverse_lazy('fair:site-list')

    def generate_event_sites(self, *args, **kwargs):
        """
        Create the event site relationship with the just created site and all future events
        """
        events = Event.currenteventfiltermgr.all()
        objs = [
            EventSite(
                event=event,
                site=self.object,
                site_status=1,
            )
            for event in events
        ]
        EventSite.objects.bulk_create(objs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()
        self.generate_event_sites()
        return super(SiteCreateView, self).form_valid(form)

    def get_initial(self, *args, **kwargs):
        initial = super(SiteCreateView, self).get_initial(**kwargs)
        return initial

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(SiteCreateView, self).get_form_kwargs(*args, **kwargs)
        kwargs['created_by'] = self.request.user
        return kwargs


class ZoneListView(PermissionRequiredMixin, ListView):
    """
    List all zones in the system by created date
    """
    permission_required = 'fairs.view_zone'
    model = Site
    template_name = 'zones/zone_list.html'
    paginate_by = 12
    queryset = Zone.objects.all().order_by("zone_code")


class ZoneDetailUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Display an editable form of the details of a zone
    """
    permission_required = 'fairs.change_zone'
    model = Zone
    form_class = ZoneDetailForm
    template_name = 'zones/zone_detail.html'
    success_url = reverse_lazy('fair:zone-list')

    def get_context_data(self, **kwargs):
        context = super(ZoneDetailUpdateView, self).get_context_data(**kwargs)
        # Refresh the obj from the database in case the form validation changed it
        obj = self.get_object()
        context['obj'] = context['zone'] = obj
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.updated_by = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class ZoneCreateView(PermissionRequiredMixin, CreateView):
    """
    Create a Zone including recording who created it
    """
    permission_required = 'fairs.add_zone'
    model = Zone
    form_class = ZoneCreateForm
    template_name = 'zones/zone_create.html'
    success_url = reverse_lazy('fair:zone-list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_initial(self, *args, **kwargs):
        initial = super(ZoneCreateView, self).get_initial(**kwargs)
        return initial

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(ZoneCreateView, self).get_form_kwargs(*args, **kwargs)
        kwargs['created_by'] = self.request.user
        return kwargs


class ZoneMapCreateView(PermissionRequiredMixin, CreateView):
    """
    Upload a Zone Map
    """
    permission_required = 'fairs.add_zone'
    model = ZoneMap
    form_class = ZoneMapCreateForm
    template_name = 'zones/zone_map_create.html'
    success_url = reverse_lazy('fair:zone-list')


class ZoneMapDetailUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Display an editable form of the details of a zone map
    """
    permission_required = 'fairs.change_zone'
    model = ZoneMap
    form_class = ZoneMapDetailForm
    template_name = 'zones/zone_map_detail.html'
    success_url = reverse_lazy('fair:zone-list')

    def get_context_data(self, **kwargs):
        context = super(ZoneMapDetailUpdateView, self).get_context_data(**kwargs)
        # Refresh the obj from the database in case the form validation changed it
        obj = self.get_object()
        context['obj'] = context['zone'] = obj
        return context


def pdf_view(request, pk):
    """
    A function to return an uploaded media file for viewing and downloading. Used for Zone maps
    """
    try:
        zonemap = ZoneMap.objects.filter(zone=pk).latest('year')
    except ObjectDoesNotExist:
        return HttpResponseNotFound('<h1>Zonemap has not be loaded for this zone</h1>')
    pdf_path = os.path.join(settings.MEDIA_ROOT / str(zonemap.map_pdf))
    filename = os.path.basename(pdf_path)
    if os.path.exists(pdf_path):
        if settings.DEBUG:
            # In development, serve the file directly through Django
            with open(pdf_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/pdf")
                response['Content-Disposition'] = 'attachment; filename={}'.format(filename)
                return response
        else:
            # In production, let Nginx handle the file serving
            from django.utils.http import urlquote
            response = HttpResponse()
            response['Content-Type'] = 'application/pdf'
            response['X-Accel-Redirect'] = '/media/' + urlquote(str(zonemap.map_pdf))  # Let Nginx handle it
            response['Content-Disposition'] = 'attachment; filename={}'.format(filename)
            return response
    raise Http404


class InventoryItemListView(PermissionRequiredMixin, ListView):
    """
    List all inventory items in the system by created date
    """
    permission_required = 'fairs.view_inventoryitem'
    model = InventoryItem
    template_name = 'inventoryitems/inventoryitem_list.html'
    queryset = InventoryItem.objects.all().order_by("-date_created")


class InventoryItemDetailUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Display an editable form of the details of an inventory item
    """
    permission_required = 'fairs.change_inventoryitem'
    model = InventoryItem
    form_class = InventoryItemDetailForm
    template_name = 'inventoryitems/inventoryitem_detail.html'
    success_url = reverse_lazy('fair:inventoryitem-list')

    def get_context_data(self, **kwargs):
        context = super(InventoryItemDetailUpdateView, self).get_context_data(**kwargs)
        # Refresh the obj from the database in case the form validation changed it
        obj = self.get_object()
        context['obj'] = context['inventoryitem'] = obj
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.updated_by = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class InventoryItemCreateView(PermissionRequiredMixin, CreateView):
    """
    Create a Zone including recording who created it
    """
    permission_required = 'fairs.add_inventoryitem'
    model = InventoryItem
    form_class = InventoryItemCreateForm
    template_name = 'inventoryitems/inventoryitem_create.html'
    success_url = reverse_lazy('fair:inventoryitem-list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_initial(self, *args, **kwargs):
        initial = super(InventoryItemCreateView, self).get_initial(**kwargs)
        return initial

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(InventoryItemCreateView, self).get_form_kwargs(*args, **kwargs)
        kwargs['created_by'] = self.request.user
        return kwargs


@login_required
@permission_required('fairs.add_eventsite', raise_exception=True)
@permission_required('fairs.change_eventsite', raise_exception=True)
def event_site_listview(request):
    """
    List all the event sites and provide filtered views based on dropdown filters of events and Zones
    """
    global event_site_filter_dict
    cards_per_page = 6
    alert_message = 'There are no event sites created yet.'
    template_name = 'eventsites/eventsite_list.html'
    filterform = EventSiteListFilterForm(request.POST or None)
    form_purpose = filterform.data.get('form_purpose', '')
    site_status=request.GET.get('site_status','')

    if not request.htmx:
        if site_status:
            filtered_data = EventSite.eventsitecurrentmgr.filter(site_status=site_status).order_by("site__site_name")
            # Define the event _site_filter_dict
            attr_sitestatus = 'site_status'
            event_site_filter_dict = {
                attr_sitestatus: site_status
            }
        else:
            filtered_data = EventSite.eventsitecurrentmgr.all().order_by("site__site_name")
            event_site_filter_dict = {}

    elif request.htmx:
        if form_purpose == 'filter':
            if filterform.is_valid():
                event = filterform.cleaned_data['event']
                zone = filterform.cleaned_data['zone']
                status = filterform.cleaned_data['site_status']
                attr_zonesite = 'site__zone'
                attr_eventsite = 'event'
                attr_sitestatus = 'site_status'
                if event and zone and status:
                    alert_message = 'There are no event sites where the event is ' + str(event) + ' and zone is ' + str(
                        zone) + ' with a status of ' + str(site_status_dict[int(status)])
                    event_site_filter_dict = {
                        attr_zonesite: zone,
                        attr_eventsite: event,
                        attr_sitestatus: status,
                    }
                elif event and zone:
                    alert_message = 'There are no event sites where the event is ' + str(event) + ' and zone is ' + str(
                        zone)
                    event_site_filter_dict = {
                        attr_zonesite: zone,
                        attr_eventsite: event,
                    }
                elif event and status:
                    alert_message = 'There are no event sites  where the event is ' + str(
                        event) + ' with a status of ' + str(site_status_dict[int(status)])
                    event_site_filter_dict = {
                        attr_eventsite: event,
                        attr_sitestatus: status,
                    }
                elif event:
                    alert_message = 'There are no event sites  where the event is ' + str(event)
                    event_site_filter_dict = {
                        attr_eventsite: event
                    }
                elif zone and status:
                    alert_message = 'There are no event sites where the zone is ' + str(zone) + ' with a status of ' + str(
                        site_status_dict[int(status)])
                    event_site_filter_dict = {
                        attr_zonesite: zone,
                        attr_sitestatus: status,
                    }
                elif zone:
                    alert_message = 'There are no event sites where the zone is ' + str(zone)
                    event_site_filter_dict = {
                        attr_zonesite: zone
                    }
                elif status:
                    alert_message = 'There are no event sites with a status of ' + str(site_status_dict[int(status)])
                    event_site_filter_dict = {
                        attr_sitestatus: status,
                    }
                else:
                    alert_message = 'There are no event sites created yet.'
                    event_site_filter_dict = {}
        else:
            # Handle pagination
            # The event_site_filter _dict is retained from the filter selection which ensures that the correct
            # data is applied
            # to subsequent pages
            pass
        filtered_data = EventSite.eventsitecurrentmgr.filter(**event_site_filter_dict).order_by("site__site_name")
        template_name = 'eventsites/eventsite_list_partial.html'
        page_list, page_range = pagination_data(cards_per_page, filtered_data, request)
        eventsite_list = page_list
        return TemplateResponse(request, template_name, {
            'eventsite_list': eventsite_list,
            'page_range': page_range,
            'alert_mgr': alert_message,
        })

    filtered_data = EventSite.eventsitecurrentmgr.filter(**event_site_filter_dict).order_by("site__site_name")
    page_list, page_range = pagination_data(cards_per_page, filtered_data, request)
    eventsite_list = page_list
    return TemplateResponse(request, template_name, {
        'filterform': filterform,
        'eventsite_list': eventsite_list,
        'page_range': page_range,
        'alert_mgr': alert_message,
    })


def pagination_data(cards_per_page, filtered_data, request):
    """
    Refactored pagination code that is available to all views that included pagination
    It takes request, cards per page, and filtered_data and returns the page_list and page_range
    """
    paginator = Paginator(filtered_data, per_page=cards_per_page)
    page_number = request.GET.get('page', 1)
    page_range = paginator.get_elided_page_range(number=page_number)
    try:
        page_list = paginator.get_page(page_number)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        page_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        page_list = paginator.get_page(paginator.num_pages)
    return page_list, page_range


class EventSiteDetailUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Display an editable form of the details of a site associated with an event
    """
    permission_required = 'fairs.change_eventsite'
    model = EventSite
    form_class = EventSiteDetailForm
    template_name = 'eventsites/eventsite_detail.html'
    success_url = reverse_lazy('fair:eventsite-list')

    def get_context_data(self, **kwargs):
        context = super(EventSiteDetailUpdateView, self).get_context_data(**kwargs)
        # Refresh the obj from the database in case the form validation changed it
        obj = self.get_object()
        context['obj'] = context['eventsite'] = obj
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class EventSiteCreateView(PermissionRequiredMixin, CreateView):
    """
    Create an Event to Site relationship and its status
    """
    permission_required = 'fairs.add_eventsite'
    model = EventSite
    form_class = EventSiteCreateForm
    template_name = 'eventsites/eventsite_create.html'
    success_url = reverse_lazy('fair:eventsite-list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_initial(self, *args, **kwargs):
        initial = super(EventSiteCreateView, self).get_initial(**kwargs)
        return initial

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(EventSiteCreateView, self).get_form_kwargs(*args, **kwargs)
        return kwargs


class InventoryItemFairListView(PermissionRequiredMixin, ListView):
    """
    List all inventory items associated with a fair order on inventory_item
    """
    permission_required = 'fairs.view_inventoryitemfair'
    model = InventoryItemFair
    template_name = 'inventoryitemfairs/inventoryitemfair_list.html'
    queryset = InventoryItemFair.currentinventoryitemfairmgr.order_by("inventory_item")


class InventoryItemFairDetailUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Display an editable form of the details of an inventory item associated with a fair
    """
    permission_required = 'fairs.change_inventoryitemfair'
    model = InventoryItemFair
    form_class = InventoryItemFairDetailForm
    template_name = 'inventoryitemfairs/inventoryitemfair_detail.html'
    success_url = reverse_lazy('fair:inventoryitemfair-list')

    def get_context_data(self, **kwargs):
        context = super(InventoryItemFairDetailUpdateView, self).get_context_data(**kwargs)
        # Refresh the obj from the database in case the form validation changed it
        obj = self.get_object()
        context['obj'] = context['inventoryitemfair'] = obj
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class InventoryItemFairCreateView(PermissionRequiredMixin, CreateView):
    """
    Create an InventoryItem to Fair relationship and its price
    """
    permission_required = 'fairs.add_inventoryitemfair'
    model = InventoryItemFair
    form_class = InventoryItemFairCreateForm
    template_name = 'inventoryitemfairs/inventoryitemfair_create.html'
    success_url = reverse_lazy('fair:inventoryitemfair-list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_initial(self, *args, **kwargs):
        initial = super(InventoryItemFairCreateView, self).get_initial(**kwargs)
        return initial

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(InventoryItemFairCreateView, self).get_form_kwargs(*args, **kwargs)
        return kwargs


def site_dashboard_view(request):
    """
    Populate the Site Dashboard with counts of the various site statuses
    """
    events = EventSite.eventsitecurrentmgr.all()
    filter_message = 'Showing unfiltered data - from all future fair events and sites in all the zones'

    if request.POST:
        form = DashboardSiteFilterForm(request.POST)
        if form.is_valid():
            event = form.cleaned_data['event']
            zone = form.cleaned_data['zone']
            site_size = form.cleaned_data['site_size']
            attr_event = 'event'
            attr_zone = 'site__zone'
            attr_site_size = 'site__site_size'
            if event and zone and site_size:
                filter_message = 'Showing filtered data where the event is ' + str(event) + 'zone is, ' + str(
                    zone) + ' and site size is a ' + str(site_size)
                filter_dict = {
                    attr_event: event,
                    attr_zone: zone,
                    attr_site_size: site_size
                }
            elif event and zone and not site_size:
                filter_message = 'Showing filtered data where the event is ' + str(event) + ' and zone is ' + str(zone)
                filter_dict = {
                    attr_event: event,
                    attr_zone: zone
                }
            elif event and site_size and not zone:
                filter_message = 'Showing filtered data where the event is ' + str(
                    event) + ' and site size is a ' + str(
                    site_size)
                filter_dict = {
                    attr_event: event,
                    attr_site_size: site_size
                }
            elif zone and site_size and not event:
                filter_message = 'Showing filtered data where the zone is ' + str(
                    zone) + ' and site size is a ' + str(
                    site_size)
                filter_dict = {
                    attr_zone: zone,
                    attr_site_size: site_size
                }
            elif event and not zone and not site_size:
                filter_message = 'Showing filtered data where the event is ' + str(event) + ' and  all zones'
                filter_dict = {
                    attr_event: event,
                }
            elif zone and not event and not site_size:
                filter_dict = {
                    attr_zone: zone
                }
                filter_message = 'Showing filtered data where the zone is ' + str(zone) + ' and all future events'
            elif site_size and not event and not site_size:
                filter_dict = {
                    attr_site_size: site_size
                }
                filter_message = 'Showing filtered data where the site size is ' + str(
                    site_size) + ' and all future events'
            else:
                filter_dict = {}
                filter_message = 'Showing unfiltered data - from all future fair events and sites in all the zones'

            total_counts = events.filter(**filter_dict).count()
            available_counts = EventSite.site_available.filter(**filter_dict).count()
            allocated_counts = EventSite.site_allocated.filter(**filter_dict).count()
            pending_counts = EventSite.site_pending.filter(**filter_dict).count()
            booked_counts = EventSite.site_booked.filter(**filter_dict).count()
            unavailable_counts = EventSite.site_unavailable.filter(**filter_dict).count()

    else:
        form = DashboardSiteFilterForm()
        total_counts = events.count()
        available_counts = EventSite.site_available.count()
        allocated_counts = EventSite.site_allocated.count()
        pending_counts = EventSite.site_pending.count()
        booked_counts = EventSite.site_booked.count()
        unavailable_counts = EventSite.site_unavailable.count()

    return TemplateResponse(request, 'dashboards/dashboard_sites.html', {
        'form': form,
        'filter': filter_message,
        'total_counts': total_counts,
        'available_counts': available_counts,
        'allocated_counts': allocated_counts,
        'pending_counts': pending_counts,
        'booked_counts': booked_counts,
        'unavailable_counts': unavailable_counts
    })


class PowerBoxCreateView(PermissionRequiredMixin, CreateView):
    """
    Create a Powerbox including recording who created it
    """
    permission_required = 'fairs.add_powerbox'
    model = PowerBox
    form_class = PowerBoxCreateForm
    template_name = 'powerboxes/powerbox_create.html'
    success_url = reverse_lazy('fair:powerbox-list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_initial(self, *args, **kwargs):
        initial = super(PowerBoxCreateView, self).get_initial(**kwargs)
        return initial

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(PowerBoxCreateView, self).get_form_kwargs(*args, **kwargs)
        kwargs['created_by'] = self.request.user
        return kwargs


class PowerBoxDetailUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Display an editable form of the details of a PowerBox
    """
    permission_required = 'fairs.change_powerbox'
    model = PowerBox
    form_class = PowerBoxUpdateDetailForm
    template_name = 'powerboxes/powerbox_detail.html'
    success_url = reverse_lazy('fair:powerbox-list')

    def get_context_data(self, **kwargs):
        context = super(PowerBoxDetailUpdateView, self).get_context_data(**kwargs)
        # Refresh the obj from the database in case the form validation changed it
        obj = self.get_object()
        context['obj'] = context['powerbox'] = obj
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class PowerBoxListView(PermissionRequiredMixin, ListView):
    """
    List all power boxes used  in a fair
    """
    permission_required = 'fairs.view_powerbox'
    model = PowerBox
    template_name = 'powerboxes/powerbox_list.html'
    queryset = PowerBox.objects.all().order_by('power_box_name')


class EventPowerListView(PermissionRequiredMixin, ListView):
    """
    List all PowerBoxes associated with an event order on event
    """
    permission_required = 'fairs.view_eventpower'
    model = EventPower
    template_name = 'eventpower/eventpower_list.html'
    queryset = EventPower.objects.all().order_by("event")


class EventPowerDetailUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Display an editable form of the details of a Powerbox associated with an event
    """
    permission_required = 'fairs.change_eventpower'
    model = EventPower
    form_class = EventPowerUpdateDetailForm
    template_name = 'eventpower/eventpower_detail.html'
    success_url = reverse_lazy('fair:eventpower-list')

    def get_context_data(self, **kwargs):
        context = super(EventPowerDetailUpdateView, self).get_context_data(**kwargs)
        # Refresh the obj from the database in case the form validation changed it
        obj = self.get_object()
        context['obj'] = context['eventpower'] = obj
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class EventPowerCreateView(PermissionRequiredMixin, CreateView):
    """
    Create an Event to PowerBox relationship and the power_load variable
    """
    permission_required = 'fairs.add_eventsite'
    model = EventPower
    form_class = EventPowerCreateForm
    template_name = 'eventpower/eventpower_create.html'
    success_url = reverse_lazy('fair:eventpower-list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_initial(self, *args, **kwargs):
        initial = super(EventPowerCreateView, self).get_initial(**kwargs)
        return initial

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(EventPowerCreateView, self).get_form_kwargs(*args, **kwargs)
        return kwargs


@login_required
@permission_required('fairs.add_siteallocation', raise_exception=True)
@permission_required('fairs.change_siteallocation', raise_exception=True)
def site_allocation_listview(request):
    """
    Populate the site allocation forms in particular provide a filtered view of dropdown boxes
    based on the stallholder filters
    """
    global site_allocation_filter_dict
    stallholder = ''
    request.session['siteallocation'] = 'fair:siteallocation-list'
    alert_message = 'There are no sites allocated yet.'
    template_name = 'siteallocations/siteallocation_list.html'
    filterform = SiteAllocationListFilterForm(request.POST or None)
    form_purpose = filterform.data.get('form_purpose', '')
    filtered_data = SiteAllocation.currentallocationsmgr.all().order_by("event_site__site")
    cards_per_page = 6
    if request.htmx:
        stallholder_id = request.POST.get('selected_stallholder')
        attr_stallholder = 'stallholder'
        if stallholder_id:
            stallholder = stallholder_id
            site_allocation_filter_dict = {
                attr_stallholder: stallholder_id
            }
            filtered_data = SiteAllocation.currentallocationsmgr.filter(**site_allocation_filter_dict).order_by( "event_site__site")
            template_name = 'siteallocations/siteallocation_list_partial.html'
            page_list, page_range = pagination_data(cards_per_page, filtered_data, request)
            allocation_list = page_list
            return TemplateResponse(request, template_name, {
                'allocation_list': allocation_list,
                'page_range': page_range,
                'alert_mgr': alert_message,
            })
        if form_purpose == 'filter':
            if filterform.is_valid():
                event = filterform.cleaned_data['event']
                zone = filterform.cleaned_data['zone']
                on_hold = filterform.cleaned_data['on_hold']
                attr_zonesite = 'event_site__site__zone'
                attr_eventsite = 'event_site__event'
                attr_onhold = 'on_hold'
                if event and zone and stallholder and on_hold:
                    alert_message = 'There are no sites allocated where the event is ' + str(event) + ' and zone is ' + str(
                        zone) + ' stallholder ID is ' + str(stallholder) + ' that are on hold'
                    site_allocation_filter_dict = {
                        attr_zonesite: zone,
                        attr_eventsite: event,
                        attr_stallholder: stallholder,
                        attr_onhold: on_hold
                    }
                elif event and zone and stallholder:
                    alert_message = 'There are no sites allocated where the event is ' + str(
                        event) + ' and zone is ' + str(
                        zone) + ' stallholder ID is ' + str(stallholder)
                    site_allocation_filter_dict = {
                        attr_zonesite: zone,
                        attr_eventsite: event,
                        attr_stallholder: stallholder
                    }
                elif event and zone and on_hold:
                    alert_message = 'There are no sites allocated where the event is ' + str(event) + ' and zone is ' + str(
                        zone)  + ' that are on hold'
                    site_allocation_filter_dict = {
                        attr_zonesite: zone,
                        attr_eventsite: event,
                        attr_onhold: on_hold
                    }
                elif event and stallholder and on_hold:
                    alert_message = 'There are no sites allocated where the event is ' + str(
                        event) + ' stallholder ID is ' + str(stallholder)  + ' that are on hold'
                    site_allocation_filter_dict = {
                        attr_eventsite: event,
                        attr_stallholder: stallholder,
                        attr_onhold: on_hold
                    }
                elif event and zone:
                    alert_message = 'There are no sites allocated where the event is ' + str(event) + ' and zone is ' + str(
                        zone)
                    site_allocation_filter_dict = {
                        attr_zonesite: zone,
                        attr_eventsite: event
                    }
                elif event and on_hold:
                    alert_message = 'There are no sites allocated where the event is ' + str(event)  + ' that are on hold'
                    site_allocation_filter_dict = {
                        attr_eventsite: event,
                        attr_onhold: on_hold
                    }
                elif event and stallholder:
                    alert_message = 'There are no sites allocated where the event is ' + str(event) + ' stallholder ID is ' + str(stallholder)
                    site_allocation_filter_dict = {
                        attr_eventsite: event,
                        attr_stallholder: stallholder
                    }
                elif zone and stallholder:
                    alert_message = 'There are no sites allocated where the zone is ' + str(zone) + ' stallholder ID is ' + str(stallholder)
                    site_allocation_filter_dict = {
                        attr_zonesite: zone,
                        attr_stallholder: stallholder
                    }
                elif zone and on_hold:
                    alert_message = 'There are no sites allocated where the zone is ' + str(
                        zone) + ' that are on hold'
                    site_allocation_filter_dict = {
                        attr_zonesite: zone,
                        attr_onhold: on_hold
                    }
                elif stallholder and on_hold:
                    alert_message = 'There are no sites allocated where the stallholder ID is ' + str(stallholder)  + ' that are on hold'
                    site_allocation_filter_dict = {
                        attr_stallholder: stallholder,
                        attr_onhold: on_hold
                    }
                elif event:
                    alert_message = 'There are no sites allocated where the event is ' + str(event)
                    site_allocation_filter_dict = {
                        attr_eventsite: event
                    }
                elif zone:
                    alert_message = 'There are no sites allocated where the zone is ' + str(zone)
                    site_allocation_filter_dict = {
                        attr_zonesite: zone
                    }
                elif on_hold:
                    alert_message = 'There are no sites allocated that are on hold'
                    site_allocation_filter_dict = {
                        attr_onhold: on_hold
                    }
                else:
                    alert_message = 'There are no sites allocated yet.'
                    site_allocation_filter_dict = {}
        else:
            # Handle pagination
            # The event_site_filter _dict is retained from the filter selection which ensures that the correct
            # data is applied
            # to subsequent pages
            pass
        template_name = 'siteallocations/siteallocation_list_partial.html'
        filtered_data = SiteAllocation.currentallocationsmgr.filter(**site_allocation_filter_dict).order_by( "event_site__site")
        page_list, page_range = pagination_data(cards_per_page, filtered_data, request)
        allocation_list = page_list
        return TemplateResponse(request, template_name, {
            'allocation_list': allocation_list,
            'page_range': page_range,
            'alert_mgr': alert_message,
        })
    else:
        page_list, page_range = pagination_data(cards_per_page, filtered_data, request)
        allocation_list = page_list
        stallholder = ''
        return TemplateResponse(request, template_name, {
            'filterform': filterform,
            'allocation_list': allocation_list,
            'page_range': page_range,
            'alert_mgr': alert_message,
        })


class SiteAllocationUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Update a Site Allocation including recording who created it
    """
    permission_required = 'fairs.change_siteallocation'
    model = SiteAllocation
    form_class = SiteAllocationUpdateForm
    template_name = 'siteallocations/siteallocation_update.html'
    success_url = reverse_lazy('fair:siteallocation-list')

    def get_context_data(self, **kwargs):
        context = super(SiteAllocationUpdateView, self).get_context_data(**kwargs)
        # Refresh the obj from the database in case the form validation changed it
        obj = self.get_object()
        context['obj'] = context['siteallocation'] = obj
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.updated_by = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


@login_required
@permission_required('fairs.add_siteallocation', raise_exception=True)
@permission_required('fairs.change_siteallocation', raise_exception=True)
def site_allocation_create(request):
    """
    Create a site allocation view with filters for events, zones and stallholders to reduce the listings for
    stallholders, event_sites and event _power.
    """

    filter_message = 'Showing unfiltered date of all events and zones'
    template_name = 'siteallocations/siteallocation_create.html'
    success_url = reverse_lazy('fair:siteallocation-list')
    request.session['create-siteallocation'] = 'fair:siteallocation-create'

    filterform = SiteAllocationFilterForm(request.POST or None)
    siteallocationform = SiteAllocationCreateForm(request.POST or None)
    if request.htmx:
        stallholder_id = request.POST.get('selected_stallholder')
        if stallholder_id:
            request.session['stallholder_id'] = stallholder_id
        else:
            stallholder_id = request.session.get('stallholder_id')
        siteallocationform.fields['event_site'].queryset = EventSite.site_available
        if filterform.is_valid():
            event = filterform.cleaned_data['event']
            zone = filterform.cleaned_data['zone']
            attr_zonesite = 'site__zone'
            attr_eventsite = 'event'
            if event and zone:
                filter_message = 'Showing filtered data where the event is  ' + str(event) + ' and zone is ' + str(
                    zone)
                event_filter_dict = {
                    attr_zonesite: zone,
                    attr_eventsite: event
                }
            elif event:
                filter_message = 'Showing filtered data where the event is  ' + str(event) + ' and all zones'
                event_filter_dict = {
                    attr_eventsite: event
                }
            elif zone:
                filter_message = 'Showing filtered data where the zone is  ' + str(zone) + ' and all events'
                event_filter_dict = {
                    attr_zonesite: zone
                }
            else:
                event_filter_dict = {}
                filter_message = 'Showing unfiltered data - of all current events and zones'
            siteallocationform.fields['event_site'].queryset = EventSite.site_available.filter(**event_filter_dict)
            if request.htmx:
                template_name = 'siteallocations/siteallocation_partial.html'
            return TemplateResponse(request, template_name, {
                'filterform': filterform,
                'siteallocationform': siteallocationform,
                'filter': filter_message,
            })
        if request.htmx:
            template_name = 'siteallocations/stallholder_partial.html'
        return TemplateResponse(request, template_name, {
            'filterform': filterform,
            'siteallocationform': siteallocationform,
            'filter': filter_message,
            'stallholder_id': stallholder_id,  # Pass it back if needed
        })
    elif request.method == 'POST':
        # Retrieve stallholder_id from session
        stallholder_id = request.session.get('stallholder_id')
        if stallholder_id and siteallocationform.is_valid():
            site_allocation = siteallocationform.save(commit=False)
            site_allocation.stallholder_id = stallholder_id
            site_allocation.site_status = 2
            site_allocation.created_by = request.user
            siteallocationform.save()
        else:
            db_logger.error('There was an error with saving the site allocation. ' + str(siteallocationform.errors.as_data()), extra={'custom_category': 'Site Allocations'})
        return HttpResponseRedirect(success_url)

    else:
        return TemplateResponse(request, template_name, {
            'filterform': filterform,
            'siteallocationform': siteallocationform,
            'filter': filter_message,
        })


def stallholder_select(request):
    """
    Capture the stallholder id passed from the Stallholder search app
    """
    template_name = 'siteallocations/stallholder_partial.html'

    stallholder_id = request.POST.get('selected_stallholder')
    form = StallHolderIDForm(initial={'stallholder_id': stallholder_id})
    return TemplateResponse(request, template_name, {
        'stallholderform': form
    })


@login_required
@permission_required('fairs.delete_siteallocation', raise_exception=True)
@require_http_methods(['DELETE'])
def siteallocation_delete_view(request, pk):
    """
    Remove a site allocation
    """
    template_name = 'siteallocations/siteallocation_list_partial.html'
    allocation = get_object_or_404(SiteAllocation, id=pk)
    eventsite = allocation.event_site
    eventsite.site_status = 1
    try:
        allocation.delete()
        eventsite.save()
    except Exception as e:  # It will catch other errors related to the delete call.
        db_logger.error('There was an error deleting the unregistered site allocation.' + e,
                        extra={'custom_category': 'Site Allocations'})
    allocation_list = SiteAllocation.currentallocationsmgr.all().order_by("event_site__site")
    if not allocation_list:
        alert_message = 'There are no sites allocated yet.'
    else:
        alert_message = ""
    paginator = Paginator(allocation_list, per_page=6)  # 6 allocations per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return TemplateResponse(request, template_name, {
        'allocation_list': allocation_list,
        'page_obj': page_obj,
        'alert_mgr': alert_message,
    })


@login_required
@permission_required('fairs.view_siteallocation', raise_exception=True)
def stall_registration_dashboard_view(request):
    """
    Populate the Stall Application dashboard with counts of a selected group of Application statuses
    """
    stall_registrations = StallRegistration.objects.all()
    template_name = 'dashboards/dashboard_registrations.html'
    filter_message = 'Showing unfiltered data - from all current and future fairs and site sizes'

    if request.POST:
        form = DashboardRegistrationFilterForm(request.POST)
        if form.is_valid():
            fair = form.cleaned_data['fair']
            site_size = form.cleaned_data['site_size']
            attr_fair = 'fair'
            attr_site_size = 'site_size'
            if fair and site_size:
                filter_message = 'Showing filtered data where the fair is ' + str(fair) + ' site size is ' + str(site_size)
                filter_dict = {
                    attr_fair: fair,
                    attr_site_size: site_size
                }
            elif fair and not site_size:
                filter_message = 'Showing filtered data where fair is ' + str(fair) + ' and all site sizes'
                filter_dict = {
                    attr_fair: fair,
                }
            elif site_size and not fair:
                filter_message = 'Showing filtered data where site size is ' + str(site_size) + ' and all fairs'
                filter_dict = {
                    attr_site_size: site_size
                }
            else:
                filter_dict = {}
                filter_message = 'Showing unfiltered data - from all current and future fairs and site sizes'

            total_counts = stall_registrations.filter(**filter_dict).count()
            selling_food_counts = StallRegistration.sellingfoodmgr.filter(**filter_dict).count()
            created_counts = StallRegistration.registrationcreatedmgr.filter(**filter_dict).count()
            submitted_counts = StallRegistration.registrationsubmittedmgr.filter(**filter_dict).count()
            invoiced_counts = StallRegistration.registrationinvoicedmgr.filter(**filter_dict).count()
            paid_counts = StallRegistration.registrationpaymentcomplemgr.filter(**filter_dict).count()
            booked_counts = StallRegistration.registrationbookedmgr.filter(**filter_dict).count()
            cancelled_counts = StallRegistration. registrationcancelledmgr.filter(**filter_dict).count()

    else:
        form = DashboardRegistrationFilterForm()
        total_counts = stall_registrations.count()
        selling_food_counts = StallRegistration.sellingfoodmgr.count()
        created_counts = StallRegistration.registrationcreatedmgr.count()
        submitted_counts = StallRegistration.registrationsubmittedmgr.count()
        invoiced_counts = StallRegistration.registrationinvoicedmgr.count()
        paid_counts = StallRegistration.registrationpaymentcomplemgr.count()
        booked_counts = StallRegistration.registrationbookedmgr.count()
        cancelled_counts = StallRegistration.registrationcancelledmgr.count()

    return TemplateResponse(request, template_name, {
        'form': form,
        'filter': filter_message,
        'total_counts': total_counts,
        'selling_food_counts': selling_food_counts,
        'created_counts': created_counts,
        'submitted_counts': submitted_counts,
        'invoiced_counts': invoiced_counts,
        'paid_counts': paid_counts,
        'booked_counts': booked_counts,
        'cancelled_counts': cancelled_counts
    })

@login_required
@permission_required('fairs.view_fair', raise_exception=True)
def setup_process_dashboard_view(request):
    """
    A dashboard that guides the convener through the steps to set up and initiate adn new fair
    """
    template_name = "dashboards/dashboard_management_process.html"

    # Status of site history records
    latest_history = SiteHistory.objects.latest('year')
    if int(latest_history.year) < current_year and current_month > 5:
        bgcolor1 = 'bg-danger'
    else:
        bgcolor1 = 'bg-success'

    #Status of site data
    latest_amended_site = Site.objects.filter(date_updated__isnull=False).latest('date_updated')
    if int(latest_amended_site.date_updated.year) < current_year and current_month > 5:
        bgcolor2 = 'bg-danger'
    else:
        bgcolor2 = 'bg-success'

    # Status of Fair Data
    current_fair = Fair.currentfairmgr.all().last()
    if current_fair:
        has_reached_activation_date = True
        if int(current_fair.fair_year) < current_year and current_month > 5:
            bgcolor3 = 'bg-danger'
        else:
            bgcolor3 = 'bg-success'
        latest_fair_name = current_fair.fair_name
    else:
        latest_fair_name =  None
        has_reached_activation_date = False
        bgcolor3 = 'bg-danger'

    # Status of Fair Events
    current_events = Event.currenteventfiltermgr.all()
    if current_events:
        if int(current_fair.fair_year) < current_year and current_month > 5:
            bgcolor4 = 'bg-danger'
        elif current_events:
            bgcolor4 = 'bg-success'
    else:
        bgcolor4 = 'bg-danger'

    # Status of Inventory Item Pricing
    current_pricing = InventoryItemFair.currentinventoryitemfairmgr.order_by("inventory_item")
    if current_pricing:
        bgcolor5 = 'bg-success'
        has_current_pricing = True
    else:
        has_current_pricing = False
        bgcolor5 = 'bg-danger'

    # Status of Site Allocations and running of siteallocation script
    current_siteallocations = SiteAllocation.currentallocationsmgr.all()
    if current_siteallocations:
        bgcolor6 = 'bg-success'
        has_current_siteallocations = True
    else:
        has_current_siteallocations = False
        bgcolor6 = 'bg-danger'


    # State of the email notification to existing stallholder that sites have been pre-allocated them
    if current_fair:
        if current_fair.allocation_email_date:
            bgcolor7 = 'bg-success'
            email_date = current_fair.allocation_email_date
        else:
            bgcolor7 = 'bg-danger'
            email_date = None
    else:
        bgcolor7 = 'bg-danger'
        email_date = None


    # Delete unregistered site allocations before the Fair is open to new registrations
    unregistered_allocations = SiteAllocation.currentallocationsmgr.filter(stall_registration__isnull=True, on_hold=False)
    count_unregistered_allocations = unregistered_allocations.count()
    registered_allocations = SiteAllocation.currentallocationsmgr.filter(stall_registration__isnull=False, on_hold=False)
    count_registered_allocations = registered_allocations.count()
    if unregistered_allocations:
        bgcolor8 = 'bg-danger'
    elif not current_fair:
        bgcolor8 = 'bg-danger'
    else:
        bgcolor8 = 'bg-success'

    if request.method == 'POST' and 'run_script' in request.POST:
        # call function
        site_allocations()
        # return user to required page
        return HttpResponseRedirect(reverse('fair:setup-dashboard'))
    elif request.method == 'POST' and 'create_emails' in request.POST:
        # call function
        site_allocation_emails()
        current_fair.allocation_email_date = datetime.datetime.now()
        current_fair.save()
        # return user to required page
        return HttpResponseRedirect(reverse('fair:setup-dashboard'))
    elif request.method == 'POST' and 'delete_allocations' in request.POST:
        # call function
        delete_unregistered_allocations()
        # return user to required page
        return HttpResponseRedirect(reverse('fair:setup-dashboard'))

    context = {
        'last_history_year': latest_history.year,
        'latest_amended_site': latest_amended_site.site_name,
        'date_latest_amended_site': latest_amended_site.date_updated,
        'latest_fair_name': latest_fair_name,
        'bgcolor1': bgcolor1,
        'bgcolor2': bgcolor2,
        'bgcolor3': bgcolor3,
        'bgcolor4': bgcolor4,
        'bgcolor5': bgcolor5,
        'bgcolor6': bgcolor6,
        'bgcolor7': bgcolor7,
        'bgcolor8': bgcolor8,
        'current_events': current_events,
        'has_current_siteallocations': has_current_siteallocations,
        'has_current_pricing': has_current_pricing,
        'email_date': email_date,
        'unregistered_allocations': unregistered_allocations,
        'count_unregistered_allocations': count_unregistered_allocations,
        'count_registered_allocations': count_registered_allocations,
        'reached_activation_date': has_reached_activation_date
    }

    return TemplateResponse(request, template_name, context )


@login_required
@permission_required('fairs.view_fair', raise_exception=True)
def messages_dashboard_view(request):
    """
    A dashboard that allows the convener to monitor and respond to stallholder messages
    """
    message_filter_dict = {}
    global stallholder
    request.session['message'] = 'fair:messages-dashboard'
    template = "dashboards/dashboard_messages_filter.html"
    filter_message= 'Showing current comments of the current fair'
    messagefilterform = MessageFilterForm(request.POST or None)
    replyform = MessageReplyForm(request.POST or None)
    # list of active parent comments
    current_fair = Fair.currentfairmgr.all().last()
    comments = RegistrationComment.objects.filter( is_archived=False, comment_parent__isnull=True, fair=current_fair.id)
    if request.htmx:
        comments = RegistrationComment.objects.filter( comment_parent__isnull=True)
        stallholder_id = request.POST.get('selected_stallholder')
        attr_stallholder = 'stallholder'
        attr_archive = 'is_archived'
        if stallholder_id:
            stallholder = stallholder_id
            filter_message = 'Showing all the unarchived messages for stallholder Id ' + str(stallholder)
            message_filter_dict = {
                attr_stallholder: stallholder_id,
                attr_archive: False,
            }
            filter_comments = comments.all().filter(**message_filter_dict)
            template = 'dashboards/dashboard_messages.html'
            return TemplateResponse(request, template, {
                'messagefilterform': messagefilterform,
                'replyform': replyform,
                'comments': filter_comments,
                'filter': filter_message,
            })
        if messagefilterform.is_valid():
            fair = messagefilterform.cleaned_data['fair']
            comment_type = messagefilterform.cleaned_data['comment_type']
            active_flag = messagefilterform.cleaned_data['is_active']
            resolved_flag = messagefilterform.cleaned_data['is_done']
            archive_flag = messagefilterform.cleaned_data['is_archived']
            attr_fair = 'fair'
            attr_comment_type = 'comment_type'
            attr_active = 'is_active'
            attr_resolved = 'is_done'
            if comment_type and fair and archive_flag and stallholder:
                filter_message = 'Showing all the archived messages of comment type ' + str(comment_type) + ' for the ' + str(fair) + ' and stallholder Id ' + str(stallholder)
                message_filter_dict = {
                    attr_stallholder: stallholder,
                    attr_fair: fair,
                    attr_comment_type: comment_type,
                    attr_archive: True,
                }
            elif comment_type and fair and active_flag and stallholder:
                filter_message = 'Showing all the messages that are under action of comment type ' + str(
                    comment_type) + ' for the ' + str(fair) + ' and stallholder Id ' + str(stallholder)
                message_filter_dict = {
                    attr_stallholder: stallholder,
                    attr_fair: fair,
                    attr_comment_type: comment_type,
                    attr_active: True,
                    attr_archive: False,
                }
            elif comment_type and fair and resolved_flag and stallholder:
                filter_message = 'Showing all the messages that are resolved of comment type ' + str(
                    comment_type) + ' for the ' + str(fair) + ' and stallholder Id ' + str(stallholder)
                message_filter_dict = {
                    attr_stallholder: stallholder,
                    attr_fair: fair,
                    attr_comment_type: comment_type,
                    attr_resolved: True,
                    attr_archive: False,
                }
            elif comment_type and fair and archive_flag:
                filter_message = 'Showing all the archived messages of comment type ' + str(comment_type) + ' for the ' + str(fair)
                message_filter_dict = {
                    attr_fair: fair,
                    attr_comment_type: comment_type,
                    attr_archive: True,
                }
            elif comment_type and fair and active_flag:
                filter_message = 'Showing all the messages that are under action of comment type ' + str(
                    comment_type) + ' for the ' + str(fair)
                message_filter_dict = {
                    attr_fair: fair,
                    attr_comment_type: comment_type,
                    attr_active: True,
                    attr_archive: False,
                }
            elif comment_type and fair and resolved_flag:
                filter_message = 'Showing all the messages that are resolved of comment type ' + str(
                    comment_type) + ' for the ' + str(fair)
                message_filter_dict = {
                    attr_fair: fair,
                    attr_comment_type: comment_type,
                    attr_resolved: True,
                    attr_archive: False,
                }
            elif comment_type and fair and stallholder:
                filter_message = 'Showing all the current messages of comment type ' + str(
                    comment_type) + ' for the ' + str(fair) + ' and stallholder Id ' + str(stallholder)
                message_filter_dict = {
                    attr_stallholder: stallholder,
                    attr_fair: fair,
                    attr_comment_type: comment_type,
                    attr_archive: False,
                }
            elif comment_type and archive_flag and stallholder:
                filter_message = 'Showing all the archived messages of the current fair of comment type ' + str(
                    comment_type) + ' and stallholder Id ' + str(stallholder)
                message_filter_dict = {
                    attr_stallholder: stallholder,
                    attr_fair: fair,
                    attr_comment_type: comment_type,
                    attr_archive: True,
                }
            elif comment_type and active_flag and stallholder:
                filter_message = 'Showing all the messages of the current fair that are under action for comment type ' + str(
                    comment_type) + ' and stallholder Id ' + str(stallholder)
                message_filter_dict = {
                    attr_stallholder: stallholder,
                    attr_fair: fair,
                    attr_comment_type: comment_type,
                    attr_active: True,
                }
            elif comment_type and resolved_flag and stallholder:
                filter_message = 'Showing all the messages of the the current fair that have been resolved for comment type ' + str(
                    comment_type) + ' and stallholder Id ' + str(stallholder)
                message_filter_dict = {
                    attr_stallholder: stallholder,
                    attr_fair: fair,
                    attr_comment_type: comment_type,
                    attr_resolved: True,
                    attr_archive: False,
                }
            elif active_flag and fair and stallholder:
                filter_message = 'Showing all  messages under action for the ' + str(fair) + ' and stallholder Id ' + str(stallholder)
                message_filter_dict = {
                    attr_stallholder: stallholder,
                    attr_fair: fair,
                    attr_active: True,
                    attr_archive: False,
                }
            elif resolved_flag and fair and stallholder:
                filter_message = 'Showing all resolved messages for the ' + str(fair) + ' and stallholder Id ' + str(stallholder)
                message_filter_dict = {
                    attr_stallholder: stallholder,
                    attr_fair: fair,
                    attr_resolved: True,
                    attr_archive: False,
                }
            elif archive_flag and fair and stallholder:
                filter_message = 'Showing all archived  messages for the ' + str(fair) + ' and stallholder Id ' + str(stallholder)
                message_filter_dict = {
                    attr_stallholder: stallholder,
                    attr_fair: fair,
                    attr_archive: True,
                }
            elif comment_type and fair:
                filter_message = 'Showing all the current messages of comment type ' + str(
                    comment_type) + ' for the ' + str(fair)
                message_filter_dict = {
                    attr_fair: fair,
                    attr_comment_type: comment_type,
                    attr_archive: False,
                }
            elif comment_type and archive_flag:
                filter_message = 'Showing all the archived messages of the current fair of comment type ' + str( comment_type)
                message_filter_dict = {
                    attr_fair: fair,
                    attr_comment_type: comment_type,
                    attr_archive: True,
                }
            elif comment_type and active_flag:
                filter_message = 'Showing all the messages of the current fair that are under action for comment type ' + str(comment_type)
                message_filter_dict = {
                    attr_fair: fair,
                    attr_comment_type: comment_type,
                    attr_active: True,
                    attr_archive: False,
                }
            elif comment_type and resolved_flag:
                filter_message = 'Showing all the messages of the the current fair that have been resolved for comment type ' + str(comment_type)
                message_filter_dict = {
                    attr_fair: fair,
                    attr_comment_type: comment_type,
                    attr_resolved: True,
                    attr_archive: False,
                }
            elif active_flag and fair:
                filter_message = 'Showing all  messages under action for the ' + str(fair)
                message_filter_dict = {
                    attr_fair: fair,
                    attr_active: True,
                    attr_archive: False,
                }
            elif resolved_flag and fair:
                filter_message = 'Showing all resolved for the ' + str(fair)
                message_filter_dict = {
                    attr_fair: fair,
                    attr_resolved: True,
                    attr_archive: False,
                }
            elif archive_flag and fair:
                filter_message = 'Showing all archived  messages for the ' + str(fair)
                message_filter_dict = {
                    attr_fair: fair,
                    attr_archive: True,
                }
            elif fair and stallholder:
                filter_message = 'Showing current messages for the ' + str(fair) + ' and stallholder Id ' + str(stallholder)
                message_filter_dict = {
                    attr_stallholder: stallholder,
                    attr_archive: False,
                    attr_fair: fair
                }
            elif comment_type and stallholder:
                filter_message = 'Showing all the messages of comment types of ' + str(
                    comment_type) + ' for the current fair for stallholder Id ' + str(stallholder)
                message_filter_dict = {
                    attr_stallholder: stallholder,
                    attr_fair: current_fair.id,
                    attr_comment_type: comment_type,
                    attr_archive: False,
                }
            elif active_flag and stallholder:
                filter_message = 'Showing all the messages that are under action for the current fair for stallholder Id ' + str(stallholder)
                message_filter_dict = {
                    attr_stallholder: stallholder,
                    attr_fair: current_fair.id,
                    attr_active: True,
                    attr_archive: False,
                }
            elif resolved_flag and stallholder:
                filter_message = 'Showing all the messages that are resolved for the current fair for stallholder Id ' + str(stallholder)
                message_filter_dict = {
                    attr_stallholder: stallholder,
                    attr_fair: current_fair.id,
                    attr_resolved: True,
                    attr_archive: False,
                }
            elif archive_flag and stallholder:
                filter_message = 'Showing all archived messages for the current fair for stallholder Id ' + str(stallholder)
                message_filter_dict = {
                    attr_stallholder: stallholder,
                    attr_fair: current_fair.id,
                    attr_archive: True,
                }
            elif fair:
                filter_message = 'Showing current messages for the ' + str(fair)
                message_filter_dict = {
                    attr_archive: False,
                    attr_fair: fair
                }
            elif comment_type:
                filter_message = 'Showing all the messages of comment types of ' + str(comment_type) + ' for the current fair'
                message_filter_dict = {
                    attr_fair: current_fair.id,
                    attr_comment_type: comment_type,
                    attr_archive: False,
                }
            elif active_flag:
                filter_message = 'Showing all the messages that are under action for the current fair'
                message_filter_dict = {
                    attr_fair: current_fair.id,
                    attr_active: True,
                    attr_archive: False,
                }
            elif resolved_flag:
                filter_message = 'Showing all the messages that are resolved for the current fair'
                message_filter_dict = {
                    attr_fair: current_fair.id,
                    attr_resolved: True,
                    attr_archive: False,
                }
            elif archive_flag:
                filter_message = 'Showing all archived messages for the current fair'
                message_filter_dict = {
                    attr_fair: current_fair.id,
                    attr_archive: True,
                }
            else:
                message_filter_dict = {
                    attr_archive: False,
                    attr_fair: current_fair.id
                }
                filter_message = 'Showing current messages of the current fair'
            template = 'dashboards/dashboard_messages.html'
            filter_comments = comments.all().filter(**message_filter_dict)
        return TemplateResponse(request, template, {
            'messagefilterform': messagefilterform,
            'replyform': replyform,
            'comments': filter_comments,
            'filter': filter_message,
        })
    elif request.method == 'POST':
        # comment has been added
        replyform = MessageReplyForm(request.POST)
        if replyform.is_valid():
            parent_obj = None
            # get parent comment id from hidden input
            try:
                # id integer e.g. 15
                parent_id = int(request.POST.get('parent_id'))
            except Exception:
                parent_id = None
            # if parent_id has been submitted get parent_obj id
            if parent_id:
                parent_obj = RegistrationComment.objects.get(id=parent_id)
                # if parent object exist
                if parent_obj:
                    # create reply comment object
                    reply_comment = replyform.save(commit=False)
                    # assign parent_obj to reply comment
                    reply_comment.comment_parent = parent_obj
                    # assign comment_type to replycomment
                    reply_comment.comment_type = parent_obj.comment_type
                    # assign user to created.by
                    reply_comment.created_by = request.user
                    # assign current fair to fair
                    reply_comment.fair_id = current_fair.id
                    # save
                    reply_comment.save()
                    return TemplateResponse(request, template, {
                        'messagefilterform': messagefilterform,
                        'comments': comments,
                        'replyform': replyform,
                        'filter': filter_message,
                    })
        return TemplateResponse(request, template, {
            'messagefilterform': messagefilterform,
            'comments': comments,
            'replyform': replyform,
            'filter': filter_message,
        })
    else:
        stallholder = ''
        return TemplateResponse(request, template, {
            'messagefilterform': messagefilterform,
            'comments': comments,
            'replyform': replyform,
            'filter': filter_message,
    })


def set_message_to_done(request, pk):
    """
    Function called from the conveners messages page to set
    the is_done flag on the parent comments instance and its sibling replies
    """
    # set the is_done flag to false on the parent comment
    comment_parent = RegistrationComment.objects.get(pk=pk)
    comment_parent.is_done = True
    comment_parent.is_active = False
    comment_parent.save()
    # if there are replies set is_active flag on these to false also
    if RegistrationComment.objects.filter(comment_parent=pk).exists():
        replies = RegistrationComment.objects.filter(comment_parent=pk)
        for reply in replies:
            reply.is_done = True
            reply.is_active = False
            reply.save()

    return redirect(request.META.get('HTTP_REFERER'))


def set_message_to_active(request, pk):
    """
    Function called from the conveners messages page to set
    the is_active flag on the parent comments instance and its sibling replies
    """
    # set the is_active flag to false on the parent comment
    comment_parent = RegistrationComment.objects.get(pk=pk)
    comment_parent.is_active = True
    comment_parent.is_done = False
    comment_parent.save()
    # if there are replies set is_active flag on these to false also
    if RegistrationComment.objects.filter(comment_parent=pk).exists():
        replies = RegistrationComment.objects.filter(comment_parent=pk)
        for reply in replies:
            reply.is_active = True
            reply.is_done = False
            reply.save()

    return redirect(request.META.get('HTTP_REFERER'))

def stallholder_history_dashboard_view(request):
    """
    Populate the Stallholder History dashboard with site by year information
    """
    template = 'dashboards/dashboard_sitehistory_filter.html'
    site_filter_message = 'Select a Zone to see stall holder site history for a specific zone'
    stallholder_filter_message = 'Search for and select a stall holder to see their site allocation history'
    request.session['stallhistory'] = 'fair:history-dashboard'
    historyfilterform =  SiteHistoryFilerForm(request.POST or None)
    stallholder_histories_transposed = defaultdict(list)
    site_histories_transposed = defaultdict(list)
    if request.htmx:
        stallholder_id = request.POST.get('selected_stallholder')
        attr_stallholder = 'stallholder'
        if stallholder_id:
            stallholder = stallholder_id
            stallholder_filter_message = 'Showing site history for stallholder ID ' + str(stallholder)
            stallholder_filter_dict = {
                attr_stallholder: stallholder_id
            }
            stallholder_histories = SiteHistory.fouryearhistorymgr.all().filter(**stallholder_filter_dict)
            for stallholder_history in stallholder_histories:
                stallholder = stallholder_history.stallholder
                stallholder_histories_transposed[stallholder].append((
                    stallholder_history.year, stallholder_history.site, stallholder_history.is_half_size))
            template = 'dashboards/dashboard_stallholder_history.html'
            return TemplateResponse(request, template, {
                'stallholder_filter': stallholder_filter_message,
                'historyfilterform': historyfilterform,
                'stallholder_histories_transposed': dict(stallholder_histories_transposed),
            })
        if historyfilterform.is_valid():
            zone = historyfilterform.cleaned_data['zone']
            attr_zone = 'site__zone'
            site_filter_message = 'Showing stallholder ID allocation histories for zone ' + str(zone)
            zone_filter_dict = {
                attr_zone: zone.id
            }
            site_histories =  SiteHistory.fouryearhistorymgr.all().filter(**zone_filter_dict).order_by('year','site')
            for site_history in site_histories:
                site_histories_transposed[site_history.site].append((site_history.year, site_history.stallholder.id,
                                                                     site_history.is_half_size,
                                                                     site_history.stallholder.is_active))
            template = 'dashboards/dashboard_site_history.html'
            return TemplateResponse(request, template, {
                'site_filter': site_filter_message,
                'historyfilterform': historyfilterform,
                'site_histories_transposed': dict(site_histories_transposed),
            })
    return TemplateResponse(request, template, {
        'site_filter': site_filter_message,
        'stallholder_filter': stallholder_filter_message,
        'historyfilterform': historyfilterform,
        'stallholder_histories_transposed': dict(stallholder_histories_transposed),
        'site_histories_transposed': dict(site_histories_transposed),
    })

def stallregistration_siteallocation_view(request, id):
    """
    Function to set siteallocation for a stall Application.  Called from the conveners stallregistraion list display
    """
    template = 'stallregistrations/siteallocation_filter.html'
    sitefilterform = SiteAllocationFilerForm(request.POST or None)
    site_filter_message = 'Select a Zone to see available sites for allocation'
    stallregistration = StallRegistration.objects.get(id=id)
    additional_sites_required = AdditionalSiteRequirement.objects.filter(stall_registration=id)
    siteallocations = SiteAllocation.objects.filter(stall_registration=id)
    if request.htmx:
        if sitefilterform.is_valid():
            zone = sitefilterform.cleaned_data['zone']
            event = sitefilterform.cleaned_data['event']
            site_size = sitefilterform.cleaned_data['site_size']
            attr_site_size = 'site__site_size'
            attr_zone = 'site__zone'
            attr_event ='event'
            if event and zone and site_size:
                site_filter_message = 'Showing available sites that can be allocated for zone ' + str(zone) + ' and fair event ' + str(event) + 'and site size' + str(site_size)
                zone_filter_dict = {
                    attr_event: event.id,
                    attr_zone: zone.id,
                    attr_site_size: site_size.id
                }
            elif event and site_size:
                site_filter_message = 'Showing available sites that can be allocated for  site size ' + str(
                    site_size) + ' and fair event ' + str(event)
                zone_filter_dict = {
                    attr_event: event.id,
                    attr_site_size: site_size.id
                }
            elif site_size and zone:
                site_filter_message = 'Showing available sites that can be allocated for zone ' + str(
                    zone) + ' and site size ' + str(site_size)
                zone_filter_dict = {
                    attr_zone: zone.id,
                    attr_site_size: site_size.id
                }
            elif event and zone:
                site_filter_message = 'Showing available sites that can be allocated for zone ' + str(zone) + ' and fair event ' + str(event)
                zone_filter_dict = {
                    attr_event: event.id,
                    attr_zone: zone.id,
                }
            elif site_size:
                site_filter_message = 'Showing available sites that can be allocated for site size ' + str(site_size)
                zone_filter_dict = {
                    attr_site_size: site_size.id
                }
            elif zone:
                site_filter_message = 'Showing available sites that can be allocated for zone ' + str(zone)
                zone_filter_dict = {
                    attr_zone: zone.id,
                }
            available_sites = EventSite.site_available.all().filter(**zone_filter_dict).order_by('site')
            template = 'stallregistrations/available_sites_partial.html'
            return TemplateResponse(request, template, {
                'site_filter': site_filter_message,
                'sitefilterform': sitefilterform,
                'stallregistration': stallregistration,
                'siteallocations': siteallocations,
                'site_list': available_sites,
                'additional_sites_required': additional_sites_required
            })
    elif request.method == 'POST':
        # Allocation request created
        for site in request.POST.getlist('eventsites'):
            # Create Allocation
            eventsite = EventSite.objects.get(id=site)
            SiteAllocation.objects.create(
                stallholder_id=stallregistration.stallholder.id,
                stall_registration= stallregistration,
                event_site=eventsite,
                created_by=request.user,
            )
            # Update status to allocated on the affected Eventsites
            eventsite.site_status = 2
            eventsite.save()
        return redirect('fair:stallregistration-detail', stallregistration_id=id)

    return TemplateResponse(request, template, {
        'site_filter': site_filter_message,
        'sitefilterform': sitefilterform,
        'stallregistration': stallregistration,
        'siteallocations': siteallocations,
        'additional_sites_required': additional_sites_required
    })

def stallregistration_detail_view(request, stallregistration_id):
    """
    Display the updated stallregistration after a siteallocation add, move or remove has occurred
    """
    siteallocations = SiteAllocation.objects.filter(stall_registration=stallregistration_id)
    try:
        stallregistration = StallRegistration.objects.get(pk=stallregistration_id)
    except stallregistration.DoesNotExist:
        return redirect('/')
    return render(request, 'stallregistration/stallregistration_detail.html', {
        'stallregistration': stallregistration,
        'siteallocations': siteallocations
    })


def stallregistration_move_cancel_view(request, id):
    """
    Function to cancel or move siteallocation for a stall Application.  Called from the conveners stallregistraion list display
    """
    template = 'stallregistrations/siteallocation_move_filter.html'
    sitefilterform = SiteAllocationFilerForm(request.POST or None)
    site_filter_message = 'Select a Zone to see available sites for allocation'
    stallregistration = StallRegistration.objects.get(id=id)
    siteallocations = SiteAllocation.objects.filter(stall_registration=id)
    if request.htmx:
        if sitefilterform.is_valid():
            zone = sitefilterform.cleaned_data['zone']
            event = sitefilterform.cleaned_data['event']
            site_size = sitefilterform.cleaned_data['site_size']
            attr_site_size = 'site__site_size'
            attr_zone = 'site__zone'
            attr_event ='event'
            if event and zone and site_size:
                site_filter_message = 'Showing available sites that can be allocated for zone ' + str(zone) + ' and fair event ' + str(event) + 'and site size' + str(site_size)
                zone_filter_dict = {
                    attr_event: event.id,
                    attr_zone: zone.id,
                    attr_site_size: site_size.id
                }
            elif event and site_size:
                site_filter_message = 'Showing available sites that can be allocated for  site size ' + str(
                    site_size) + ' and fair event ' + str(event)
                zone_filter_dict = {
                    attr_event: event.id,
                    attr_site_size: site_size.id
                }
            elif site_size and zone:
                site_filter_message = 'Showing available sites that can be allocated for zone ' + str(
                    zone) + ' and site size ' + str(site_size)
                zone_filter_dict = {
                    attr_zone: zone.id,
                    attr_site_size: site_size.id
                }
            elif event and zone:
                site_filter_message = 'Showing available sites that can be allocated for zone ' + str(zone) + ' and fair event ' + str(event)
                zone_filter_dict = {
                    attr_event: event.id,
                    attr_zone: zone.id,
                }
            elif site_size:
                site_filter_message = 'Showing available sites that can be allocated for site size ' + str(site_size)
                zone_filter_dict = {
                    attr_site_size: site_size.id
                }
            elif zone:
                site_filter_message = 'Showing available sites that can be allocated for zone ' + str(zone)
                zone_filter_dict = {
                    attr_zone: zone.id,
                }
            available_sites = EventSite.site_available.all().filter(**zone_filter_dict).order_by('site')
            template = 'stallregistrations/available_move_sites_partial.html'
            return TemplateResponse(request, template, {
                'site_filter': site_filter_message,
                'sitefilterform': sitefilterform,
                'stallregistration': stallregistration,
                'siteallocations': siteallocations,
                'site_list': available_sites
            })
    elif request.method == 'POST':
        # Cancel request created
        if request.POST.getlist('currentsites'):
            cancelledallocations =request.POST.getlist('currentsites')
            for cancelledallocation in cancelledallocations:
                siteallocation = SiteAllocation.objects.get(id=cancelledallocation)
                eventsite = EventSite.objects.get(id=siteallocation.event_site.id)
                siteallocation.delete()
                # Update status to available on the affected Eventsites
                eventsite.site_status = 1
                eventsite.save()
        elif request.POST.get('hidden'):
            currentallocationlist = request.POST.get('hidden').split(',')
            for siteallocation in currentallocationlist:
                siteallocation = SiteAllocation.objects.get(id=siteallocation)
                eventsite = EventSite.objects.get(id=siteallocation.event_site.id)
                siteallocation.delete()
                # Update status to available on the affected Eventsites
                eventsite.site_status = 1
                eventsite.save()
            # Move request created
            for site in request.POST.getlist('eventsites'):
                # Create Allocation
                eventsite = EventSite.objects.get(id=site)
                SiteAllocation.objects.create(
                    stallholder_id=stallregistration.stallholder.id,
                    stall_registration= stallregistration,
                    event_site=eventsite,
                    created_by=request.user,
                )
                # Update status to allocated on the affected Eventsites
                eventsite.site_status = 2
                eventsite.save()
        return redirect('fair:stallregistration-detail', stallregistration_id=id)

    return TemplateResponse(request, template, {
        'site_filter': site_filter_message,
        'sitefilterform': sitefilterform,
        'stallregistration': stallregistration,
        'siteallocations': siteallocations
    })
