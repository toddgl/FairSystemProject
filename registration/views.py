# registration/views.py

import json
import datetime

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.template.response import TemplateResponse
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
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
    SiteAllocation
)

from .forms import (
    FoodPrepEquipmentCreationForm,
    FoodPrepEquipmentUpdateForm,
    FoodSaleTypeCreationForm,
    FoodSaleTypeUpdateForm,
    StallCategoryCreationForm,
    StallCategoryUpdateForm,
    StallRegistrationUpdateForm,
    StallRegistrationCreateForm,
    FoodRegistrationForm,
    FoodPrepEquipReqForm,
)


# Create your views here.
class StallRegistrationCreateView(PermissionRequiredMixin, CreateView):
    """
    Create a Stall Registration
    """
    permission_required = 'registration.add_stallregistration'
    model = StallRegistration
    form_class = StallRegistrationCreateForm
    template_name = 'stallregistration/stallregistration_create.html'
    success_url = reverse_lazy('registration:stallregistration-dashboard')

    def get_context_data(self, **kwargs):
        context = super(StallRegistrationCreateView, self).get_context_data(**kwargs)
        stallholder = self.request.user
        print(stallholder.id)
        context['allocation_list'] = SiteAllocation.currentallocationsmgr.filter(stallholder_id=stallholder.id, stall_registration__isnull=True)
        return context


class StallRegistrationUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Display an editable form of the details of a Stall Registration
    """
    permission_required = 'registration.change_stallregistration'
    model = StallRegistration
    form_class = StallRegistrationUpdateForm
    template_name = 'registration/stallregistration_detail.html'
    success_url = reverse_lazy('registration:stallregistration-dashboard')

    def get_context_data(self, **kwargs):
        context = super(StallRegistrationUpdateView, self).get_context_data(**kwargs)
        # Refresh the object from the database in case the form validation changed it
        object = self.get_object()
        context['object'] = context['stallregistration'] = object
        return context


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


@login_required
@permission_required('registration.view_stallregistration', raise_exception=True)
def myfair_dashboard_view(request):
    """
    Stallholders Myfair dashboard
    """

    template = "myfair/myfair_dashboard.html"
    current_fairs = StallRegistration.objects.filter(fair__is_activated=True)
    myfair_list = current_fairs.filter(stallholder=request.user)

    return TemplateResponse(request, template, {
        'registrations': myfair_list
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
            equipment = form.save(commit=False)
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
            return render(request, 'equipmentregistration/equipment_form.html', {'form': form})
    else:
        form = FoodPrepEquipReqForm()
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
                "equipmentListChanged": None,
                "showMessage": f"{equipment.food_prep_equipment} deleted."
            })
        }
    )

