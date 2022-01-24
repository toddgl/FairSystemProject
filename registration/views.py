# registration/views.py

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import (
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
)

from .forms import (
    FoodPrepEquipmentCreationForm,
    FoodPrepEquipmentUpdateForm,
    FoodSaleTypeCreationForm,
    FoodSaleTypeUpdateForm,
    StallCategoryCreationForm,
    StallCategoryUpdateForm,
    StallRegistrationCreateUpdateForm,
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


class RegistrationCreateUpdateView(PermissionRequiredMixin, SingleObjectTemplateResponseMixin, ModelFormMixin,
                                   ProcessFormView):
    """
    Description: A Joint Create and Update view for the stall registration model
    """
    permission_required = 'registration.change_stallregistration'
    model = StallRegistration
    form_class = StallRegistrationCreateUpdateForm
    template_name = 'stallregistration/stallregistration_createupdate.html'
    success_url = reverse_lazy('registration:stallregistration-detail')

    def get_object(self, queryset=None):
        try:
            return super(RegistrationCreateUpdateView, self).get_object(queryset)
        except AttributeError:
            return None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(RegistrationCreateUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(RegistrationCreateUpdateView, self).post(request, *args, **kwargs)
