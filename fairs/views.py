# fairs/view.py
import datetime
import os
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect, HttpResponse, FileResponse, Http404, HttpResponseNotFound
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    FormView,
    ListView,
    UpdateView
)

from fairs.models import (
    Fair,
    Event,
    EventSite,
    Site,
    Location,
    Zone,
    ZoneMap,
    InventoryItem,
    InventoryItemFair,
    PowerBox,
    EventPower,
)
from .forms import (
    FairDetailForm,
    FairCreateForm,
    EventCreateForm,
    EventDetailForm,
    SiteCreateForm,
    SiteDetailForm,
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
    InventoryItemFairDetailForm,
    InventoryItemFairCreateForm,
    DashboardSiteFilterForm,
    PowerBoxCreateForm,
    PowerBoxUpdateDetailForm,
    EventPowerCreateForm,
    EventPowerUpdateDetailForm
)

# Global Variables
current_year = datetime.datetime.now().year
next_year = current_year + 1
media_root = settings.MEDIA_ROOT


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
        sites = Site.objects.all()
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
        context['obj'] = context['fair'] = obj
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
    queryset = Site.objects.all().order_by("-date_created")


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
        events = Event.filtermgr.all()
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
    queryset = Zone.objects.all().order_by("-date_created")


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
    pdf_path = os.path.join('media', str(zonemap.map_pdf))
    filename = os.path.basename(pdf_path)
    if os.path.exists(pdf_path):
        with open(pdf_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/pdf")
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


class EventSiteListView(PermissionRequiredMixin, ListView):
    """
    List all sites associated with an event order on event
    """
    permission_required = 'fairs.view_eventsite'
    model = EventSite
    template_name = 'eventsites/eventsite_list.html'
    queryset = EventSite.objects.all().order_by("site_status")


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
    queryset = InventoryItemFair.objects.all().order_by("inventory_item")


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
    events = EventSite.objects.all()
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
