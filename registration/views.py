# registration/views.py
import decimal
import json
import datetime

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
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
    RegistrationComment,
)

from fairs.models import (
    Fair,
    SiteAllocation,
    InventoryItemFair
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
    RegistrationCommentForm,
    CommentReplyForm,
)

# Global Variables
current_year = datetime.datetime.now().year
next_year = current_year + 1


# Create your views here.
@login_required
@permission_required('registration.add_stallregistration', raise_exception=True)
def stall_registration_create(request):
    """
    Create a Stall Registration includes determining the total charge for the stall site based on site size,
    Trestles based on quantity requested place food licence fees if the food stall flag is set.
    """
    template_name = 'stallregistration/stallregistration_create.html'
    success_url = reverse_lazy('registration:stallregistration-dashboard')
    stallholder = request.user
    siteallocation = SiteAllocation.currentallocationsmgr.filter(stallholder_id=stallholder.id,
                                                                 stall_registration__isnull=True).first()
    if siteallocation:
        fair_id = siteallocation.event_site.event.fair.id
        site_size = siteallocation.event_site.site.site_size_id
        site_charge = InventoryItemFair.currentinventoryitemfairmgr.get(
            inventory_item__item_name=siteallocation.event_site.site.site_size).price
        total_cost = site_charge
        registrationform = StallRegistrationCreateForm(request.POST or None,
                                                       initial={'fair': fair_id, 'site_size': site_size})
        allocation_item = siteallocation
    else:
        current_fair = Fair.currentfairmgr.all().last()
        fair_id = current_fair.id
        registrationform = StallRegistrationCreateForm(request.POST or None, initial={'fair': fair_id})
        allocation_item = None
        total_cost = None

    if request.htmx:
        fair_id = request.POST.get('fair')
        template_name = 'stallregistration/stallregistration_partial.html'
        total_cost = get_registration_costs(fair_id, request)
    elif request.method == 'POST':
        total_cost = get_registration_costs(fair_id, request)
        if registrationform.is_valid():
            stall_registration = registrationform.save(commit=False)
            stall_registration.stallholder = stallholder
            stall_registration.total_charge = total_cost
            stall_registration.save()
            if siteallocation:
                stall_registration.refresh_from_db()
                siteallocation.stall_registration_id = stall_registration.id
                siteallocation.save(update_fields=['stall_registration'])
            if stall_registration.selling_food:
                success_url = reverse_lazy('registration:food-registration')
        else:
            print(
                registrationform.errors.as_data())  # here you print errors to terminal TODO these should go to a log
        return HttpResponseRedirect(success_url)

    return TemplateResponse(request, template_name, {
        'allocation_item': allocation_item,
        'billing': total_cost,
        'registrationform': registrationform
    })


def get_registration_costs(fair_id, request):
    site_size = request.POST.get('site_size')
    stall_category = request.POST.get('stall_category')

    if stall_category:
        category = StallCategory.objects.get(pk=stall_category)
        if category.has_inventory_item:
            category_price = InventoryItemFair.objects.get(inventory_item_id=category.inventory_item.id).price
            price_rate = InventoryItemFair.objects.get(inventory_item_id=category.inventory_item.id).price_rate
            category_price = category_price * price_rate
        else:
            category_price = decimal.Decimal(0.00)

    if site_size:
        site_price = InventoryItemFair.objects.get(fair=fair_id, inventory_item__id=site_size).price
        price_rate = InventoryItemFair.objects.get(fair=fair_id, inventory_item__id=site_size).price_rate
        site_price = price_rate * site_price
    else:
        site_price = decimal.Decimal(0.00)
    trestle_num = request.POST.get('trestle_quantity')
    if trestle_num:
        trestle_price = InventoryItemFair.objects.get(fair=fair_id, inventory_item__item_name='Trestle Table').price
        price_rate = InventoryItemFair.objects.get(fair=fair_id, inventory_item__item_name='Trestle Table').price_rate
        total_trestle_cost = price_rate * trestle_price * decimal.Decimal(trestle_num)
    else:
        total_trestle_cost = decimal.Decimal(0.00)
    power_req = request.POST.get('power_required')
    if power_req:
        power_price = InventoryItemFair.objects.get(fair=fair_id, inventory_item__item_name='Power Point').price
        price_rate = InventoryItemFair.objects.get(fair=fair_id, inventory_item__item_name='Power Point').price_rate
        power_price = price_rate * power_price
    else:
        power_price = decimal.Decimal(0.00)
    total_cost = category_price + site_price + total_trestle_cost + power_price
    return total_cost


@login_required
@permission_required('registration.add_stallregistration', raise_exception=True)
def stall_registration_update_view(request, pk):
    template = 'stallregistration/stallregistration_update.html'
    success_url = reverse_lazy('registration:stallregistration-dashboard')

    obj = get_object_or_404(StallRegistration, id=pk)
    total_cost = obj.total_charge
    registrationform = StallRegistrationUpdateForm(request.POST or None, instance=obj)
    siteallocation = SiteAllocation.currentallocationsmgr.filter(stall_registration=pk).first()

    if siteallocation:
        allocation_item = siteallocation
        fair_id = siteallocation.event_site.event.fair.id
    else:
        current_fair = Fair.currentfairmgr.all().last()
        fair_id = current_fair.id

    if request.htmx:
        template = 'stallregistration/stallregistration_partial.html'
        total_cost = get_registration_costs(fair_id, request)
    elif request.method == 'POST':
        total_cost = get_registration_costs(fair_id, request)
        if registrationform.is_valid():
            stall_registration = registrationform.save(commit=False)
            stall_registration.total_charge = total_cost
            stall_registration.save()
            return HttpResponseRedirect(success_url)

    return TemplateResponse(request, template, {
        'allocation_item': allocation_item,
        'billing': total_cost,
        'registrationform': registrationform
    })


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
    paginate_by = 12
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
    paginate_by = 12
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
    commentform = RegistrationCommentForm(request.POST or None)
    replyform = CommentReplyForm(request.POST or None)
    # list of active parent comments
    current_fair = Fair.currentfairmgr.all().last()
    comments = RegistrationComment.objects.filter(stallholder=request.user, is_active=True, comment_parent__isnull=True, fair=current_fair.id)
    try:
        # Use prefetch_related to bring through the site allocation data associated with the stall registration
        myfair_list = current_fairs.filter(stallholder=request.user).prefetch_related('site_allocation').all()
    except ObjectDoesNotExist:
        myfair_list = current_fairs.filter(stallholder=request.user)

    if request.htmx:
        comment_template = 'stallregistration/registration_comments.html'
        commentform = RegistrationCommentForm(request.POST or None)
        replyform = CommentReplyForm(request.POST or None)
        parent_id = int(request.POST.get('parent_id'))
        comments = RegistrationComment.objects.filter(stallholder=request.user, is_active=True,
                                                      comment_parent__isnull=True, fair=current_fair.id)
        print(parent_id)
        return TemplateResponse(request, comment_template, {
            'comments': comments,
            'commentform': commentform,
            'replyform': replyform,
        })

    if request.method == 'POST':
        # comment has been added
        commentform = RegistrationCommentForm(request.POST)
        replyform = CommentReplyForm(request.POST)
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
                        'registrations': myfair_list,
                        'comments': comments,
                        'commentform': commentform,
                        'replyform': replyform,
                    })
        elif commentform.is_valid():
            # normal comment
            # create comment object but do not save to database
            new_comment = commentform.save(commit=False)
            # assign stallholder to the comment
            new_comment.stallholder = request.user
            # assign user to created.by
            new_comment.created_by = request.user
            # assign current fair to fair
            new_comment.fair_id = current_fair.id
            # save
            new_comment.save()
            return TemplateResponse(request, template, {
                'registrations': myfair_list,
                'comments': comments,
                'commentform': commentform,
                'replyform': replyform,
            })
    return TemplateResponse(request, template, {
        'registrations': myfair_list,
        'comments': comments,
        'commentform': commentform,
        'replyform': replyform,
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


@require_POST
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
