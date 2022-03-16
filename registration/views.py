# registration/views.py

import json

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.dispatch.dispatcher import logger
from django.template.response import TemplateResponse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy
from django.views.generic import (
    View,
    CreateView,
    ListView,
    UpdateView,
)
from django.views.generic.detail import (SingleObjectTemplateResponseMixin)
from django.views.generic.edit import (
    ModelFormMixin,
    ProcessFormView
)
from registration.models import (
    FoodPrepEquipment,
    FoodSaleType,
    StallCategory,
    StallRegistration,
    FoodRegistration,
    FoodPrepEquipReq,
)

from fairs.models import (
    EventSite,
)

from .forms import (
    FoodPrepEquipmentCreationForm,
    FoodPrepEquipmentUpdateForm,
    FoodSaleTypeCreationForm,
    FoodSaleTypeUpdateForm,
    StallCategoryCreationForm,
    StallCategoryUpdateForm,
    StallRegistrationFilterForm,
    StallRegistrationCreateUpdateForm,
    FoodRegistrationForm,
    FoodPrepEquipReqForm,
)


# Create your views here.


class FoodPrepEquipmentCreateView(PermissionRequiredMixin, CreateView):
    """
    Create a food preparation equipment
    """
    permission_required = 'registration.add_foodprepequipment'
    model = FoodPrepEquipment
    form_class = FoodPrepEquipmentCreationForm
    template_name = 'foodprepequipment/foodprepequipment_create.html'
    success_url = reverse_lazy('registration:foodprepequipment-list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_initial(self, *args, **kwargs):
        initial = super(FoodPrepEquipmentCreateView, self).get_initial(**kwargs)
        return initial

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(FoodPrepEquipmentCreateView, self).get_form_kwargs(*args, **kwargs)
        kwargs['created_by'] = self.request.user
        return kwargs


class FoodPrepEquipmentListView(PermissionRequiredMixin, ListView):
    """
    List all food preparation equipment
    """
    permission_required = "registration.view_foodprepequipment"
    model = FoodPrepEquipment
    template_name = 'foodprepequipment/foodprepequipment_list.html'
    queryset = FoodPrepEquipment.objects.all()


class FoodPrepEquipmentDetailUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Display an editable form of food preparation equipment
    """
    permission_required = 'registration.change_foodprepequipment'
    model = FoodPrepEquipment
    form_class = FoodPrepEquipmentUpdateForm
    template_name = 'foodprepequipment/foodprepequipment_detail.html'
    success_url = reverse_lazy('registration:foodprepequipment-list')

    def get_context_data(self, **kwargs):
        context = super(FoodPrepEquipmentDetailUpdateView, self).get_context_data(**kwargs)
        # Refresh the object from the database in case the form validation changed it
        object = self.get_object()
        context['object'] = context['foodprepequipment'] = object
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class FoodSaleTypeCreateView(PermissionRequiredMixin, CreateView):
    """
    Create a food sale type
    """
    permission_required = 'registration.add_foodsaletype'
    model = FoodSaleType
    form_class = FoodSaleTypeCreationForm
    template_name = 'foodsaletype/foodsaletype_create.html'
    success_url = reverse_lazy('registration:foodsaletype-list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_initial(self, *args, **kwargs):
        initial = super(FoodSaleTypeCreateView, self).get_initial(**kwargs)
        return initial

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(FoodSaleTypeCreateView, self).get_form_kwargs(*args, **kwargs)
        kwargs['created_by'] = self.request.user
        return kwargs


class FoodSaleTypeListView(PermissionRequiredMixin, ListView):
    """
    List all food sale types
    """
    permission_required = "registration.view_foodsaletype"
    model = FoodPrepEquipment
    template_name = 'foodsaletype/foodsaletype_list.html'
    queryset = FoodSaleType.objects.all()


class FoodSaleTypeDetailUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Display an editable form of food sale types
    """
    permission_required = 'registration.change_foodsaletype'
    model = FoodSaleType
    form_class = FoodSaleTypeUpdateForm
    template_name = 'foodsaletype/foodsaletype_detail.html'
    success_url = reverse_lazy('registration:foodsaletype-list')

    def get_context_data(self, **kwargs):
        context = super(FoodSaleTypeDetailUpdateView, self).get_context_data(**kwargs)
        # Refresh the object from the database in case the form validation changed it
        object = self.get_object()
        context['object'] = context['foodsaletype'] = object
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class StallCategoryCreateView(PermissionRequiredMixin, CreateView):
    """
    Create a stall category
    """
    permission_required = 'registration.add_stallcategory'
    model = StallCategory
    form_class = StallCategoryCreationForm
    template_name = 'stallcategory/stallcategory_create.html'
    success_url = reverse_lazy('registration:stallcategory-list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_initial(self, *args, **kwargs):
        initial = super(StallCategoryCreateView, self).get_initial(**kwargs)
        return initial

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(StallCategoryCreateView, self).get_form_kwargs(*args, **kwargs)
        kwargs['created_by'] = self.request.user
        return kwargs


class StallCategoryListView(PermissionRequiredMixin, ListView):
    """
    List all stall categories
    """
    permission_required = "registration.view_stallcategory"
    model = FoodPrepEquipment
    template_name = 'stallcategory/stallcategory_list.html'
    queryset = StallCategory.objects.all().order_by('category_name')


class StallCategoryDetailUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Display an editable form of stall categories
    """
    permission_required = 'registration.change_stallcategory'
    model = StallCategory
    form_class = StallCategoryUpdateForm
    template_name = 'stallcategory/stallcategory_detail.html'
    success_url = reverse_lazy('registration:stallcategory-list')

    def get_context_data(self, **kwargs):
        context = super(StallCategoryDetailUpdateView, self).get_context_data(**kwargs)
        # Refresh the object from the database in case the form validation changed it
        object = self.get_object()
        context['object'] = context['stallcategory'] = object
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


filter_dict = {}
filter_message = ""


@login_required
@permission_required('registration.add_stallregistration', raise_exception=True)
@permission_required('registration.change_stallregistration', raise_exception=True)
def stall_registration_view(request):
    """
    Populate the stall registration forms in particular provide a filter view of available sites based on
    site size,
    """
    global filter_message
    filter_message = 'Showing unfiltered data - of all available sites for the current fair'
    filterform = StallRegistrationFilterForm()
    registrationform = StallRegistrationCreateUpdateForm()
    available_first_event_sites = EventSite.site_available_first_event
    available_second_event_sites = EventSite.site_available_second_event
    template_name = 'stallregistration/stallregistration_createupdate.html'

    if request.POST:
        filterform = StallRegistrationFilterForm(request.POST)
        registrationform = StallRegistrationCreateUpdateForm(request.POST)
        registrationform.fields['event_site_first'].queryset = available_first_event_sites
        registrationform.fields['event_site_second'].queryset = available_second_event_sites
        if filterform.is_valid():
            zone = filterform.cleaned_data['zone']
            site_size = filterform.cleaned_data['site_size']
            attr_zone = 'site__zone'
            attr_site_size = 'site__site_size'
            if zone and site_size:
                filter_message = 'Showing filtered data where the zone is ' + str(zone) + ' and site size is a ' + str(
                    site_size)
                filter_dict = {
                    attr_zone: zone,
                    attr_site_size: site_size
                }
            elif zone:
                filter_dict = {
                    attr_zone: zone
                }
                filter_message = 'Showing filtered data where the zone is ' + str(zone) + ' and all site sizes'
            elif site_size:
                filter_dict = {
                    attr_site_size: site_size
                }
                filter_message = 'Showing filtered data where the site size is ' + str(site_size) + ' and all ' \
                                                                                                    'zones '
            else:
                filter_dict = {}
                filter_message = 'Showing unfiltered data - of all available sites for the current fair'

            registrationform.fields['event_site_first'].queryset = available_first_event_sites.filter(**filter_dict)
            registrationform.fields['event_site_second'].queryset = available_second_event_sites.filter(**filter_dict)
            if request.htmx:
                template_name = 'stallregistration/stallregistration_partial.html'
            return TemplateResponse(request, template_name, {
                'filterform': filterform,
                'registrationform': registrationform,
                'filter': filter_message,
            })

    else:
        return TemplateResponse(request, template_name, {
            'filterform': filterform,
            'registrationform': registrationform,
            'filter': filter_message,
        })


def find_second_eventsite(request):
    """
    Using the selection of the first event site find the matching second event site for the same site_name
    """
    template_name = 'stallregistration/stallregistration_partial.html'
    registrationform = StallRegistrationCreateUpdateForm()
    available_first_event_sites = EventSite.site_available_first_event
    available_second_event_sites = EventSite.site_available_second_event
    eventsite_first_id = request.GET['event_site_first']
    eventsite = EventSite.objects.get(id=eventsite_first_id)
    site_id = eventsite.site_id
    eventsite_second_qs = available_second_event_sites.filter(site__id=site_id)
    eventsite_second_id = eventsite_second_qs.values('id')[0].get('id')
    registrationform.fields['event_site_first'].queryset = available_first_event_sites.filter(**filter_dict)
    registrationform.fields['event_site_first'].initial = eventsite_first_id
    registrationform.fields['event_site_second'].queryset = eventsite_second_qs
    registrationform.fields['event_site_second'].initial = eventsite_second_id
    return TemplateResponse(request, template_name, {
        'registrationform': registrationform,
        'filter': filter_message,
    })

def food_registration(request):
    if request.method == "POST":
        form = FoodRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse(status=204, headers={'HX-Trigger': 'foodRegistrationChanged'})
    else:
        form = FoodRegistrationForm()
    return render(request, 'stallregistration/food_registration.html', {
        'form': form,
    })


@login_required
@permission_required('registration.add_foodprepequipreq', raise_exception=True)
@permission_required('registration.change_foodprepequipreq', raise_exception=True)
@permission_required('registration.delete_foodprepequipreq', raise_exception=True)
def display_food_equipment(request):
    return render(request, 'equipmentregistration/equipment_registration.html')


def equipment_list(request):
    return render(request, 'equipmentregistration/equipment_list.html', {
        'foodprepequipreq': FoodPrepEquipReq.objects.all()
    })


def add_equipment(request):
    if request.method == "POST":
        form = FoodPrepEquipReqForm(request.POST)
        if form.is_valid():
            equipment =form.save(commit=False)
            equipment.food_registration = FoodRegistration.objects.get(id=id)
            equipment = form.save()
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "equipmentListChanged": None,
                        "showMessage": f"{equipment.food_prep_equipment} added."
                    })
                })
        else:
            print(form)
            print("Invalid Form")
            print(form.errors)
            return render(request, 'equipmentregistration/equipment_form.html',{'form':form})
    else:
        form =FoodPrepEquipReqForm()
    return render(request, 'equipmentregistration/equipment_form.html', {
        'form': form,
    })


def edit_equipment(request, pk):
    equipment = get_object_or_404(FoodPrepEquipReq, pk=pk)
    if request.method == "POST":
        form = FoodPrepEquipReqForm(request.POST, instance=equipment)
        if form.is_valid():
            form.save()
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "equipmentListChanged": None,
                        "showMessage": f"{equipment.food_prep_equipment} updated."
                    })
                }
            )
    else:
        form = FoodPrepEquipReqForm(instance=equipment)
    return render(request, 'equipmentregistration/equipment_form.html', {
        'form': form,
        'equipment': equipment,
    })


@ require_POST
def remove_equipment(request, pk):
    equipment = get_object_or_404(FoodPrepEquipReq, pk=pk)
    equipment.delete()
    return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                "equipmenteListChanged": None,
                "showMessage": f"{equipment.food_prep_equipment} deleted."
            })
        }
    )
