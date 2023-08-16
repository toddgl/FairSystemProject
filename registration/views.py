# registration/views.py
import datetime
import decimal

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse_lazy, reverse
from django.views.decorators.http import require_POST
from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
)
from accounts.models import(
    CustomUser,
    Profile
)

from fairs.models import (
    Fair,
    SiteAllocation,
    InventoryItemFair
)
from registration.models import (
    FoodPrepEquipment,
    FoodSaleType,
    StallCategory,
    StallRegistration,
    FoodRegistration,
    FoodPrepEquipReq,
    RegistrationComment,
    AdditionalSiteRequirement,
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
    CommentFilterForm,
    CommentReplyForm,
    StallRegistrationFilterForm,
    AdditionalSiteReqForm,
)

# Global Variables
current_year = datetime.datetime.now().year
next_year = current_year + 1


# Create your views here.
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


@login_required
@permission_required('registration.change_stallregistration', raise_exception=True)
def stall_registration_listview(request):
    """
    List stall registration used by the Fair Conveners in the view and management of stall registrations
    """
    filter_dict ={}
    global stallholder
    cards_per_page = 6
    request.session['registration'] = 'registration:stallregistration-list'
    template_name = 'stallregistration/stallregistration_list.html'
    filterform = StallRegistrationFilterForm(request.POST or None )
    booking_status=request.GET.get('booking_status', '')
    if booking_status:
        filtered_data = StallRegistration.registrationcurrentmgr.filter(booking_status=booking_status).order_by('stall_category').prefetch_related('site_allocation').all()
        alert_message = 'There are no stall registration of status ' + str(booking_status) + ' created yet'
    else:
        filtered_data = StallRegistration.registrationcurrentmgr.order_by('stall_category').prefetch_related('site_allocation').all()
        alert_message = 'There are no stall registrations yet.'

    if request.htmx:
        stallholder_id = request.POST.get('selected_stallholder')
        attr_stallholder = 'stallholder'
        if stallholder_id:
            stallholder = stallholder_id
            filter_dict = {
                attr_stallholder: stallholder_id
            }
            filtered_data = StallRegistration.registrationcurrentmgr.filter(**filter_dict).order_by("stall_category").prefetch_related('site_allocation').all()
            template_name = 'stallregistration/stallregistration_list_partial.html'
            page_list, page_range = pagination_data(cards_per_page, filtered_data, request)
            stallregistration_list = page_list
            return TemplateResponse(request, template_name, {
                'stallregistration_list': stallregistration_list,
                'page_range': page_range,
                'alert_mgr': alert_message,
            })
        if filterform.is_valid():
            fair = filterform.cleaned_data['fair']
            site_size = filterform.cleaned_data['site_size']
            attr_fair = 'fair'
            attr_site_size = 'site_size'
            if fair and site_size and stallholder:
                alert_message = 'There are no stall registrations where the fair is ' + str(
                fair) + ' and site size is ' + str(site_size) + ' stallholder ID is ' + str(stallholder)
                filter_dict = {
                    attr_fair: fair,
                    attr_site_size: site_size,
                    attr_stallholder: stallholder
                }
            elif fair and site_size:
                alert_message = 'There are no stall registrations where the fair is ' + str(fair) + ' and site size is ' + str(site_size)
                filter_dict = {
                    attr_fair: fair,
                    attr_site_size: site_size,
                }
            elif fair and stallholder:
                alert_message = 'There are no stall registrations where the fair is ' + str(fair)  + ' stallholder ID is ' + str(stallholder)
                filter_dict = {
                    attr_fair: fair,
                    attr_stallholder: stallholder
                }
            elif site_size and stallholder:
                alert_message = 'There are no stall registrations where the site size is ' + str(site_size)  + ' stallholder ID is ' + str(stallholder)
                filter_dict = {
                    attr_site_size: site_size,
                    attr_stallholder: stallholder
                }
            elif fair:
                alert_message = 'There are no stall registrations where the fair is ' + str(fair)
                filter_dict = {
                    attr_fair: fair,
                }
            elif site_size:
                alert_message = 'There are no stall registrations where the site size is ' + str(site_size)
                filter_dict = {
                    attr_site_size: site_size,
                }
            else:
                alert_message = 'There are no stall registration created yet'
                filter_dict = {}
            filtered_data = StallRegistration.registrationcurrentmgr.filter(**filter_dict).order_by('stall_category').prefetch_related('site_allocation').all()
            template_name = 'stallregistration/stallregistration_list_partial.html'
            page_list, page_range = pagination_data(cards_per_page, filtered_data, request)
            stallregistration_list = page_list
            return TemplateResponse(request, template_name, {
                'stallregistration_list': stallregistration_list,
                'page_range': page_range,
                'alert_mgr': alert_message,
            })
        filtered_data = StallRegistration.registrationcurrentmgr.filter(**filter_dict).order_by("stall_category").prefetch_related('site_allocation').all()
        template_name = 'stallregistration/stallregistration_list_partial.html'
        page_list, page_range = pagination_data(cards_per_page, filtered_data, request)
        stallregistration_list = page_list
        return TemplateResponse(request, template_name, {
            'stallregistration_list': stallregistration_list,
            'page_range': page_range,
            'alert_mgr': alert_message,
        })
    else:
        page_list, page_range = pagination_data(cards_per_page, filtered_data, request)
        stallregistration_list = page_list
        stallholder = ''
        return TemplateResponse(request, template_name, {
            'filterform': filterform,
            'stallregistration_list': stallregistration_list,
            'page_range': page_range,
            'alert_mgr': alert_message,
        })



@login_required
@permission_required('registration.add_stallregistration', raise_exception=True)
def stall_registration_create(request):
    """
    Create a Stall Registration includes determining the total charge for the stall site based on site size,
    Trestles based on quantity requested place food licence fees if the food stall flag is set.
    """
    template_name = 'stallregistration/stallregistration_create.html'
    success_url = reverse_lazy('registration:stallregistration-dashboard')
    commentfilterform = CommentFilterForm(request.POST or None)
    commentform = RegistrationCommentForm(request.POST or None)
    replyform = CommentReplyForm(request.POST or None)
    stallholder = request.user
    siteallocation = SiteAllocation.currentallocationsmgr.filter(stallholder_id=stallholder.id,
                                                                 stall_registration__isnull=True).first()
    current_fair = Fair.currentfairmgr.all().last()
    comments = RegistrationComment.objects.filter(stallholder=stallholder.id,  is_archived=False, convener_only_comment=False, comment_parent__isnull=True, fair=current_fair.id)
    comment_filter_message = 'Showing current comments of the current fair'
    if siteallocation:
        fair_id = siteallocation.event_site.event.fair.id
        site_size = siteallocation.event_site.site.site_size_id
        site_charge = InventoryItemFair.currentinventoryitemfairmgr.get(
            inventory_item__item_name=siteallocation.event_site.site.site_size).price
        total_cost = site_charge
        registrationform = StallRegistrationCreateForm( initial={'fair': fair_id, 'site_size': site_size})
        allocation_item = siteallocation
    else:
        current_fair = Fair.currentfairmgr.all().last()
        fair_id = current_fair.id
        registrationform = StallRegistrationCreateForm(initial={'fair': fair_id})
        allocation_item = None
        total_cost = None

    if request.htmx:
        fair_id = request.POST.get('fair')
        template_name = 'stallregistration/stallregistration_partial.html'
        total_cost = get_registration_costs(request, fair_id)
        return TemplateResponse(request, template_name, {
            'allocation_item': allocation_item,
            'billing': total_cost,
            'registrationform': registrationform,
        })
    elif request.method == 'POST':
        if siteallocation:
            registrationform = StallRegistrationCreateForm(request.POST, request.FILES or None,
                                                       initial={'fair': fair_id, 'site_size': site_size})
        else:
            registrationform = StallRegistrationCreateForm(request.POST, request.FILES or None,
                                                           initial={'fair': fair_id})
        total_cost = get_registration_costs(request, fair_id)
        if registrationform.is_valid():
            stall_registration = registrationform.save(commit=False)
            stall_registration.stallholder = stallholder
            stall_registration.total_charge = total_cost
            stall_registration.save()
            stall_registration.refresh_from_db()
            if siteallocation:
                siteallocation.stall_registration = stall_registration
                siteallocation.save(update_fields=['stall_registration'])
            if stall_registration.selling_food:
                return redirect('registration:food-registration', stall_registration.id)
            else:
                return HttpResponseRedirect(success_url)
        else:
            print(
                registrationform.errors.as_data())  # here you print errors to terminal TODO these should go to a log
            return TemplateResponse(request, template_name, {
                'allocation_item': allocation_item,
                'billing': total_cost,
                'registrationform': registrationform,
                'commentfilterform': commentfilterform,
                'commentform': commentform,
                'replyform': replyform,
                'comments': comments,
                'comment_filter': comment_filter_message
            })

    return TemplateResponse(request, template_name, {
        'allocation_item': allocation_item,
        'billing': total_cost,
        'registrationform': registrationform,
        'commentfilterform': commentfilterform,
        'commentform': commentform,
        'replyform': replyform,
        'comments': comments,
        'comment_filter': comment_filter_message
    })


def get_registration_costs(request, fair_id, parent_id=None):
    site_size = request.POST.get('site_size')
    stall_category = request.POST.get('stall_category')
    additional_site_costs = decimal.Decimal(0.00)
    total_additional_site_costs = decimal.Decimal(0.00)

    # check to see if this a stall registration update
    if parent_id:
        # Check to see if there are additional sites required
        if AdditionalSiteRequirement.objects.filter(stall_registration_id=parent_id ).exists():
            additional_site_list = AdditionalSiteRequirement.objects.filter(stall_registration_id=parent_id )
            for additional_site in additional_site_list:
                site_price = InventoryItemFair.objects.get(fair=fair_id, inventory_item__id=additional_site.site_size.id).price
                price_rate = InventoryItemFair.objects.get(fair=fair_id, inventory_item__id=additional_site.site_size.id).price_rate
                additional_site_costs = price_rate * site_price * additional_site.site_quantity
                total_additional_site_costs = total_additional_site_costs + additional_site_costs

    if stall_category:
        category = StallCategory.objects.get(pk=stall_category)
        if category.has_inventory_item:
            category_price = InventoryItemFair.objects.get(fair=fair_id,inventory_item_id=category.inventory_item.id).price
            price_rate = InventoryItemFair.objects.get(fair=fair_id,inventory_item_id=category.inventory_item.id).price_rate
            category_price = category_price * price_rate
        else:
            category_price = decimal.Decimal(0.00)
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
    total_cost = category_price + site_price + total_trestle_cost + power_price + total_additional_site_costs
    return total_cost


@login_required
@permission_required('registration.change_stallregistration', raise_exception=True)
def stall_registration_update_view(request, pk):
    template_name = 'stallregistration/stallregistration_update.html'
    success_url = reverse_lazy('registration:stallregistration-dashboard')
    additionalsiteform = AdditionalSiteReqForm(request.POST or None)
    commentfilterform = CommentFilterForm(request.POST or None)
    commentform = RegistrationCommentForm(request.POST or None)
    replyform = CommentReplyForm(request.POST or None)
    comment_filter_message = 'Showing current comments of the current fair'

    obj = get_object_or_404(StallRegistration, id=pk)
    total_cost = obj.total_charge
    stallholder = obj.stallholder
    registration_fair = obj.fair
    if SiteAllocation.currentallocationsmgr.filter(stallholder_id=stallholder.id, stall_registration=pk).exists():
        siteallocation = SiteAllocation.currentallocationsmgr.get(stallholder_id=stallholder.id, stall_registration=pk)
    else:
        siteallocation = None
    # list of active parent comments
    comments = RegistrationComment.objects.filter(stallholder=request.user, is_archived=False, convener_only_comment=False, comment_parent__isnull=True, fair=registration_fair.id)
    registrationform = StallRegistrationUpdateForm(instance=obj)

    context = {
        'billing': total_cost,
        'stallregistration': obj,
        'registrationform': registrationform,
        'additionalsiteform' : additionalsiteform,
        'commentfilterform': commentfilterform,
        'commentform': commentform,
        'replyform': replyform,
        'filter': comment_filter_message,
        'comments': comments,
    }
    if siteallocation:
        allocation_item = siteallocation
        context['allocation_item'] = allocation_item

    # Additional Sites add and display
    addsites_form = AdditionalSiteReqForm(request.POST or None)
    additional_sites = AdditionalSiteRequirement.objects.filter(stall_registration=obj)
    if additional_sites:
        total_cost = get_registration_costs(request, registration_fair.id, pk)
        context['site_requirement_list'] = additional_sites

    if request.htmx:
        template_name = 'stallregistration/stallregistration_partial.html'
        total_cost = get_registration_costs(request, registration_fair.id, pk)
        return TemplateResponse(request, template_name, {
            'billing': total_cost,
            'registrationform': registrationform,
        })
    elif request.method == 'POST':
        total_cost = get_registration_costs(request, registration_fair.id, pk)
        registrationform = StallRegistrationUpdateForm(request.POST, request.FILES or None, instance=obj)
        if registrationform.is_valid():
            stall_registration = registrationform.save(commit=False)
            stall_registration.id = pk
            stall_registration.stallholder = stallholder
            stall_registration.total_charge = total_cost
            stall_registration.save()
            if stall_registration.selling_food:
                new_instance = get_object_or_404(StallRegistration, id=pk)
                try:
                    # get Food Registration object
                    obj = FoodRegistration.objects.get(registration=new_instance)
                except FoodRegistration.DoesNotExist:  #f FoodRegistration object does not exist
                    # create FoodRegistration object
                    obj = FoodRegistration(registration=new_instance, has_food_certificate=False, food_fair_consumed=False, has_food_prep=False, is_valid=False)
                    obj.save()
                return redirect('registration:food-registration', stall_registration.id)
            else:
                return HttpResponseRedirect(success_url)
        else:
            print(
                registrationform.errors.as_data())  # here you print errors to terminal TODO these should go to a log
            return TemplateResponse(request, template_name, context)

    return TemplateResponse(request, template_name, context)


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
    comment_filter_message= 'Showing current comments of the current fair'
    current_fairs = StallRegistration.objects.filter(fair__is_activated=True)
    commentfilterform = CommentFilterForm(request.POST or None)
    commentform = RegistrationCommentForm(request.POST or None)
    replyform = CommentReplyForm(request.POST or None)
    # list of active parent comments
    current_fair = Fair.currentfairmgr.all().last()
    comments = RegistrationComment.objects.filter(stallholder=request.user, is_archived=False, convener_only_comment=False, comment_parent__isnull=True, fair=current_fair.id)
    try:
        # Use prefetch_related to bring through the site allocation data associated with the stall registration
        myfair_list = current_fairs.filter(stallholder=request.user).prefetch_related('site_allocation').all()
    except ObjectDoesNotExist:
        myfair_list = current_fairs.filter(stallholder=request.user)

    return TemplateResponse(request, template, {
    'registrations': myfair_list,
    'commentfilterform': commentfilterform,
    'comments': comments,
    'commentform': commentform,
    'replyform': replyform,
    'filter': comment_filter_message,
    })

def archive_comments(request, pk):
    """
    Function called from the stallholder comments page to set
    the is_archived flag on the parent comments instance and its sibling replies
    """
    # set the is_archived flag to false on the parent comment
    comment_parent = RegistrationComment.objects.get(pk=pk)
    comment_parent.is_archived = True
    comment_parent.save()
    # if there are replies set is_active flag on these to false also
    if RegistrationComment.objects.filter(comment_parent=pk).exists():
        replies = RegistrationComment.objects.filter(comment_parent=pk)
        for reply in replies:
            reply.is_archived = True
            reply.save()

    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def food_registration_create_view(request, pk):
    template_name = 'stallregistration/food_registration.html'
    success_url = reverse_lazy('registration:stallregistration-dashboard')
    commentfilterform = CommentFilterForm(request.POST or None)
    commentform = RegistrationCommentForm(request.POST or None)
    replyform = CommentReplyForm(request.POST or None)
    comment_filter_message= 'Showing current comments of the current fair'
    # list of active parent comments
    current_fair = Fair.currentfairmgr.all().last()
    comments = RegistrationComment.objects.filter(stallholder=request.user, is_archived=False, convener_only_comment=False, comment_parent__isnull=True, fair=current_fair.id)
    foodregistration = get_object_or_404(FoodRegistration, registration=pk)
    food_form = FoodRegistrationForm(instance=foodregistration)
    equipment_form = FoodPrepEquipReqForm(request.POST or None)
    equipment_list = FoodPrepEquipReq.objects.filter(food_registration_id=foodregistration.id)
    if equipment_list:
        context = {
            'food_form' : food_form,
            'equipment_form' : equipment_form,
            'foodregistration' : foodregistration,
            'equipment_list': equipment_list,
            'commentfilterform': commentfilterform,
            'comments': comments,
            'commentform': commentform,
            'replyform': replyform,
            'filter': comment_filter_message,
        }
    else:
        context = {
            'food_form' : food_form,
            'equipment_form' : equipment_form,
            'foodregistration' : foodregistration,
            'commentfilterform': commentfilterform,
            'comments': comments,
            'commentform': commentform,
            'replyform': replyform,
            'filter': comment_filter_message,
        }

    if request.method == 'POST':
        food_form = FoodRegistrationForm(request.POST, request.FILES or None, instance=foodregistration)
        if food_form.is_valid():
            object=food_form.save(commit=False)
            object.is_valid = True
            object.save()
            return HttpResponseRedirect(success_url)
    return TemplateResponse(request, template_name, context)


@login_required
def food_registration_update_view(request, id=None):
    comment_filter_message= 'Showing current comments of the current fair'
    commentfilterform = CommentFilterForm(request.POST or None)
    commentform = RegistrationCommentForm(request.POST or None)
    replyform = CommentReplyForm(request.POST or None)
    current_fair = Fair.currentfairmgr.all().last()
    comments = RegistrationComment.objects.filter(stallholder=request.user, is_archived=False, convener_only_comment=False, comment_parent__isnull=True, fair=current_fair.id)
    obj = get_object_or_404(FoodRegistration, id=id)
    form = FoodRegistrationForm(request.POST, request.FILES, instance=obj)
    context = {
        "form": form,
        "object": obj,
        'commentfilterform': commentfilterform,
        'comments': comments,
        'commentform': commentform,
        'replyform': replyform,
        'comment_filter': comment_filter_message
    }
    if form.is_valid():
        object = form.save(commit=False)
        object.is_valid = True
        object.save()
        context['message'] = 'Data saved.'
    if request.htmx:
        return render(request, "stallregistration/food_form_partial.html", context)
    return render(request, "stallregistration/food_registration.html", context)


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


def add_site_requirement(request, pk):
    template = 'stallregistration/stallregistration_inline_partial.html'
    site_requirement_form = AdditionalSiteReqForm(request.POST or None)
    if request.htmx:
        if site_requirement_form.is_valid():
            stall_registration_obj= StallRegistration.objects.get(id=pk)
            # if stall registration object exist
            if stall_registration_obj:
                # create site requirement object
                site_requirement = site_requirement_form.save(commit=False)
                site_requirement.stall_registration = stall_registration_obj
                # save
                site_requirement.save()
            site_requirement_list = AdditionalSiteRequirement.objects.filter(stall_registration_id=pk)
            return TemplateResponse(request, template, {
                'site_requirement_list': site_requirement_list,
            })
        else:
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect(request.META.get('HTTP_REFERER'))



def add_food_prep_equipment(request):
    template = 'stallregistration/equipment_inline_partial.html'
    food_equipment_form = FoodPrepEquipReqForm(request.POST, request.FILES or None)
    if request.htmx:
        if food_equipment_form.is_valid():
            food_registration_obj = None
            # get parent food registration from hidden input
            try:
                # id integer e.g. 15
                food_registration_id = int(request.POST.get('food_registration_id'))
            except Exception:
                food_registration_id = None
            # if food_registration_id has been submitted get the food_registration_obj id
            if food_registration_id:
                food_registration_obj= FoodRegistration.objects.get(id=food_registration_id)
                # if food registration object exist
                if food_registration_obj:
                    # create food_registration requirement object
                    food_prep_equipment = food_equipment_form.save(commit=False)
                    food_prep_equipment.food_registration = food_registration_obj
                    # save
                    food_prep_equipment.save()
            equipment_list = FoodPrepEquipReq.objects.filter(food_registration_id=food_registration_id)
            return TemplateResponse(request, template, {
                'equipment_list': equipment_list,
            })
        else:
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect(request.META.get('HTTP_REFERER'))


@require_POST
def remove_site_requirement(request, parent_id, id):
    template = 'stallregistration/stallregistration_inline_partial.html'
    site = get_object_or_404(AdditionalSiteRequirement, pk=id)
    site.delete()
    site_requirement_list = AdditionalSiteRequirement.objects.filter(stall_registration_id=parent_id)
    return TemplateResponse(request, template, {
        'site_requirement_list': site_requirement_list,
    })


@require_POST
def remove_equipment(request, parent_id, id):
    template = 'stallregistration/equipment_inline_partial.html'
    equipment = get_object_or_404(FoodPrepEquipReq, pk=id)
    equipment.delete()
    equipment_list = FoodPrepEquipReq.objects.filter(food_registration_id=int(parent_id))
    return TemplateResponse(request, template, {
        'equipment_list': equipment_list,
        })


def comments_view_add (request):
    """
    Separation of the stallholder comments view and add code that just updates the comments displayed based on the htmx
    filterform plus the ability to create new comments and reply to existing ones
    """
    stallholder_id = None
    template = 'stallregistration/registration_comments.html'
    commentfilterform = CommentFilterForm(request.POST or None)
    commentform = RegistrationCommentForm(request.POST or None)
    replyform = CommentReplyForm(request.POST or None)
    current_fair = Fair.currentfairmgr.all().last()
    if request.session.get('stallholder_id'):
        stallholder_id = request.session['stallholder_id']
        comments = RegistrationComment.objects.filter(stallholder=stallholder_id, is_archived=False,
                                                  convener_only_comment=False, comment_parent__isnull=True,
                                                  fair=current_fair.id)
    else:
        comments = RegistrationComment.objects.filter(stallholder=request.user, is_archived=False,
                                                  convener_only_comment=False, comment_parent__isnull=True,
                                                  fair=current_fair.id)
    if request.htmx:
        if stallholder_id:
            comments = RegistrationComment.objects.filter(stallholder=stallholder_id,convener_only_comment=False,
                                                          comment_parent__isnull=True)
        else:
            comments = RegistrationComment.objects.filter(stallholder=request.user, convener_only_comment=False,
                                                      comment_parent__isnull=True)
        if commentfilterform.is_valid():
            archive_flag = commentfilterform.cleaned_data['is_archived']
            fair = commentfilterform.cleaned_data['fair']
            attr_archive = 'is_archived'
            attr_fair = 'fair'
            if archive_flag and fair:
                comment_filter_message = 'Showing all (archived and current) comments for the ' + str(fair)
                comment_filter_dict = {
                    attr_fair: fair
                }
            elif archive_flag:
                comment_filter_message = 'Showing all (archived and current) comments for the current fair'
                comment_filter_dict = {
                    attr_fair: current_fair.id
                }
            elif fair:
                comment_filter_message = 'Showing current comments for the ' + str(fair)
                comment_filter_dict = {
                    attr_archive: False,
                    attr_fair: fair
                }
            else:
                comment_filter_dict = {
                    attr_archive: False,
                    attr_fair: current_fair.id
                }
                comment_filter_message = 'Showing current comments of the current fair'
        filter_comments = comments.all().filter(**comment_filter_dict)
        return TemplateResponse(request, template, {
            'commentfilterform': commentfilterform,
            'replyform': replyform,
            'commentform': commentform,
            'comments': filter_comments,
            'comment_filter': comment_filter_message,
        })
    elif request.method == 'POST':
        # comment has been added
        replyform = CommentReplyForm(request.POST or None)
        commentform = RegistrationCommentForm(request.POST or None)
        if commentform.is_valid():
            # normal comment
            # create comment object but do not save to database
            new_comment = commentform.save(commit=False)
            # assign stallholder to the comment
            if stallholder_id:
                stallholder = CustomUser.objects.get(id=stallholder_id)
                new_comment.stallholder = stallholder
            else:
                new_comment.stallholder = request.user
            # assign user to created.by
            new_comment.created_by = request.user
            # assign current fair to fair
            new_comment.fair_id = current_fair.id
            try:
                # save
                new_comment.save()
            except Exception:
                print(
                    commentform.errors.as_data())  # here you print errors to terminal TODO these should go to a log
            return redirect(request.META.get('HTTP_REFERER'))
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
            return redirect(request.META.get('HTTP_REFERER'))


@login_required
def food_equipment_delete_view(request, parent_id=None, id=None):
    try:
        obj = FoodPrepEquipReq.objects.get(food_registration__id=parent_id, id=id)
    except:
        obj = None
    if obj is None:
        if request.htmx:
            return HttpResponse("Not Found")
        raise Http404
    if request.method == "POST":
        name = obj.food_prep_equipment.equipment_name
        obj.delete()
        success_url = reverse('registration:detail', kwargs={"id": parent_id})
        if request.htmx:
            return render(request, "stallregistration/equipment-inline-delete-response_partial.html", {"name": name})
        return redirect(success_url)
    context = {
        "object": obj
    }
    return render(request, "stallregistration/delete.html", context)


def stall_registration_detail_view(request, id):
    """
    Display the details of the stall and food registration data provided by the stallholder
    """
    template = "stallregistration/stall_registration_detail.html"
    comment_filter_message= 'Showing current comments of the current fair'
    commentfilterform = CommentFilterForm(request.POST or None)
    commentform = RegistrationCommentForm(request.POST or None)
    replyform = CommentReplyForm(request.POST or None)
    current_fair = Fair.currentfairmgr.all().last()
    stall_registration = StallRegistration.objects.get(id=id)
    request.session['stallholder_id'] = stall_registration.stallholder.id
    stallholder_detail = Profile.objects.get(user=stall_registration.stallholder)
    comments = RegistrationComment.objects.filter(stallholder=stall_registration.stallholder.id, is_archived=False, convener_only_comment=False, comment_parent__isnull=True, fair=current_fair.id)
    context = {
        'stallholder_detail': stallholder_detail,
        "stall_data" : stall_registration,
        'commentfilterform': commentfilterform,
        'comments': comments,
        'commentform': commentform,
        'replyform': replyform,
        'comment_filter': comment_filter_message
    }
    if stall_registration.multi_site:
        context['additional_sites'] = AdditionalSiteRequirement.objects.filter(stall_registration_id=stall_registration.id)

    if FoodRegistration.objects.filter(registration=id).exists():
        context["food_data"] = food_registration = FoodRegistration.objects.get(registration=id)
        context["equipment_list"] = FoodPrepEquipReq.objects.filter(food_registration=food_registration)

    return TemplateResponse(request, template, context)
