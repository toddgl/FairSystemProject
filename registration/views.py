# registration/views.py

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    ListView,
    UpdateView
)

from registration.models import (
    FoodPrepEquipment,
)

from .forms import (
    FoodPrepEquipmentCreationForm,
    FoodPrepEquipmentUpdateForm,
)

# Create your views here.


class FoodPrepEquipmentCreateView(PermissionRequiredMixin, CreateView):
    """
    Create a food preparation equipment
    """
    permission_required = 'fairs.add_location'
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
    permission_required = "fairs.view_location"
    model = FoodPrepEquipment
    template_name = 'foodprepequipment/foodprepequipment_list.html'
    queryset = FoodPrepEquipment.objects.all()


class FoodPrepEquipmentDetailUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Display an editable form of food preparation equipment
    """
    permission_required = 'fairs.change_location'
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
