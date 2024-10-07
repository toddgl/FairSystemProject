# registration/views.py
import datetime
import decimal
import logging

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse_lazy, reverse
from django.views.decorators.http import require_POST, require_http_methods
from django.core.exceptions import PermissionDenied
from django_fsm import can_proceed
from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
)
from accounts.models import (
    CustomUser,
    Profile
)

from fairs.models import (
    Fair,
    SiteAllocation,
    InventoryItemFair
)
from payment.models import (
    PaymentHistory,
    Invoice,
    InvoiceItem,
    DiscountItem
)
from registration.models import (
    CommentType,
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
    StallRegistrationStallholderEditForm,
    FoodRegistrationStallholderEditForm,
    StallRegistrtionConvenerEditForm,
    FoodRegistrationConvenerEditForm,
    RegistrationDiscountForm,
)

# Global Variables
current_year = datetime.datetime.now().year
next_year = current_year + 1
db_logger = logging.getLogger('db')


class HTTPResponseHXRedirect(HttpResponseRedirect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["HX-Redirect"] = self["Location"]

    status_code = 200


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
    List stall application used by the Fair Conveners in the view and management of stall registrations
    """
    # global stallregistration_filter_dict
    global stallholder
    cards_per_page = 6
    request.session['registration'] = 'registration:stallregistration-list'
    template_name = 'stallregistration/stallregistration_list.html'
    filterform = StallRegistrationFilterForm(request.POST or None)
    booking_status = request.GET.get('booking_status', '')
    selling_food = request.GET.get('selling_food', False)
    if booking_status:
        alert_message = 'There are no stall application of status ' + str(booking_status) + ' created yet'

        # Define the stallregistration_filter_dict
        attr_booking_status = 'booking_status'
        stallregistration_filter_dict = {
            attr_booking_status: booking_status
        }
        filtered_data = StallRegistration.registrationcurrentallmgr.filter(
            **stallregistration_filter_dict).order_by("stall_category").prefetch_related('site_allocation').all()
        filtered_data = filtered_data.prefetch_related('additional_sites_required')
        page_list, page_range = pagination_data(cards_per_page, filtered_data, request)
        stallregistration_list = page_list
        return TemplateResponse(request, template_name, {
            'filterform': filterform,
            'stallregistration_list': stallregistration_list,
            'page_range': page_range,
            'alert_mgr': alert_message,
        })

    if selling_food:
        alert_message = 'There are no stall application of status ' + 'Selling Food' + ' created yet'

        # Define the stallregistration_filter_dict
        attr_selling_food = 'selling_food'
        stallregistration_filter_dict = {
            attr_selling_food: True
        }
        filtered_data = StallRegistration.registrationcurrentallmgr.filter(
            **stallregistration_filter_dict).order_by("stall_category").prefetch_related('site_allocation').all()
        filtered_data = filtered_data.prefetch_related('additional_sites_required')
        page_list, page_range = pagination_data(cards_per_page, filtered_data, request)
        stallregistration_list = page_list
        return TemplateResponse(request, template_name, {
            'filterform': filterform,
            'stallregistration_list': stallregistration_list,
            'page_range': page_range,
            'alert_mgr': alert_message,
        })

    if request.htmx:
        stallholder_id = request.POST.get('selected_stallholder')
        attr_stallholder = 'stallholder'
        if stallholder_id:
            stallholder = stallholder_id
            stallregistration_filter_dict = {
                attr_stallholder: stallholder_id
            }
        form_purpose = filterform.data.get('form_purpose', '')

        if form_purpose == 'filter':
            # existing filter logic...
            if filterform.is_valid():
                fair = filterform.cleaned_data['fair']
                site_size = filterform.cleaned_data['site_size']
                attr_fair = 'fair'
                attr_site_size = 'site_size'
                if fair and site_size and stallholder:
                    alert_message = 'There are no stall registrations where the fair is ' + str(
                        fair) + ' and site size is ' + str(site_size) + ' stallholder ID is ' + str(stallholder)
                    stallregistration_filter_dict = {
                        attr_fair: fair,
                        attr_site_size: site_size,
                        attr_stallholder: stallholder
                    }
                elif fair and site_size:
                    alert_message = 'There are no stall registrations where the fair is ' + str(
                        fair) + ' and site size is ' + str(site_size)
                    stallregistration_filter_dict = {
                        attr_fair: fair,
                        attr_site_size: site_size,
                    }
                elif fair and stallholder:
                    alert_message = 'There are no stall registrations where the fair is ' + str(
                        fair) + ' stallholder ID is ' + str(stallholder)
                    stallregistration_filter_dict = {
                        attr_fair: fair,
                        attr_stallholder: stallholder
                    }
                elif site_size and stallholder:
                    alert_message = 'There are no stall registrations where the site size is ' + str(
                        site_size) + ' stallholder ID is ' + str(stallholder)
                    stallregistration_filter_dict = {
                        attr_site_size: site_size,
                        attr_stallholder: stallholder
                    }
                elif fair:
                    alert_message = 'There are no stall registrations where the fair is ' + str(fair)
                    stallregistration_filter_dict = {
                        attr_fair: fair,
                    }
                elif site_size:
                    alert_message = 'There are no stall registrations where the site size is ' + str(site_size)
                    stallregistration_filter_dict = {
                        attr_site_size: site_size,
                    }
                else:
                    alert_message = 'There are no stall application created yet'
        else:
            # Pagination logic
            if 'stallregistration_filter_dict' not in locals():
                stallregistration_filter_dict = {}

        filtered_data = StallRegistration.registrationcurrentallmgr.filter(**stallregistration_filter_dict).order_by(
            "stall_category").prefetch_related('site_allocation').all()

        page_list, page_range = pagination_data(cards_per_page, filtered_data, request)
        stallregistration_list = page_list
        template_name = 'stallregistration/stallregistration_list_partial.html'
        return TemplateResponse(request, template_name, {
            'stallregistration_list': stallregistration_list,
            'page_range': page_range,
        })

    else:
        filtered_data = StallRegistration.registrationcurrentallmgr.order_by('stall_category').prefetch_related( 'site_allocation').all()
        filtered_data = filtered_data.prefetch_related('additional_sites_required')
        alert_message = 'There are no stall registrations yet.'

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
    Create a Stall Application includes determining the total charge for the stall site based on site size,
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
    comments = RegistrationComment.objects.filter(stallholder=stallholder.id, is_archived=False,
                                                  convener_only_comment=False, comment_parent__isnull=True,
                                                  fair=current_fair.id)
    comment_filter_message = 'Showing current comments of the current fair'
    registration_id = None
    if siteallocation:
        fair_id = siteallocation.event_site.event.fair.id
        site_size = siteallocation.event_site.site.site_size_id
        site_charge = InventoryItemFair.currentinventoryitemfairmgr.get(
            inventory_item__item_name=siteallocation.event_site.site.site_size).price
        site_rate = InventoryItemFair.currentinventoryitemfairmgr.get(
            inventory_item__item_name=siteallocation.event_site.site.site_size).price_rate
        total_cost = site_charge * site_rate
        registrationform = StallRegistrationCreateForm(initial={'fair': fair_id, 'site_size': site_size})
        allocation_item = siteallocation
    else:
        current_fair = Fair.currentfairmgr.all().last()
        fair_id = current_fair.id
        registrationform = StallRegistrationCreateForm(initial={'fair': fair_id})
        allocation_item = None
        total_cost = None

    if request.htmx:
        fair_id = request.POST.get('fair')
        site_size = request.POST.get('site_size')
        stall_category = request.POST.get('stall_category')
        trestle_num = request.POST.get('trestle_quantity')
        vehicle_length = request.POST.get('vehicle_length')
        power_req = request.POST.get('power_required')
        template_name = 'stallregistration/stallregistration_partial.html'
        total_cost = get_registration_costs(request, fair_id, registration_id, site_size, stall_category,
                                            trestle_num, vehicle_length, power_req)
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
        site_size = request.POST.get('site_size')
        stall_category = request.POST.get('stall_category')
        trestle_num = request.POST.get('trestle_quantity')
        vehicle_length = request.POST.get('vehicle_length')
        power_req = request.POST.get('power_required')
        total_cost = get_registration_costs(request, fair_id, registration_id, site_size, stall_category, trestle_num,
                                            vehicle_length, power_req)
        if registrationform.is_valid():
            stall_registration = registrationform.save(commit=False)
            stall_registration.stallholder = stallholder
            stall_registration.total_charge = total_cost
            stall_registration.save()
            stall_registration.refresh_from_db()
            if siteallocation:
                allocations = SiteAllocation.currentallocationsmgr.filter(stallholder_id=stallholder.id,
                                                                          stall_registration__isnull=True)
                for allocation in allocations:
                    allocation.stall_registration = stall_registration
                    allocation.save(update_fields=['stall_registration'])
            if stall_registration.selling_food:
                return redirect('registration:food-registration', stall_registration.id)
            else:
                return HttpResponseRedirect(success_url)
        else:
            db_logger.error('There was an error with saving the stall application. '
                            + registrationform.errors.as_data(),
                            extra={'custom_category': 'Stall Application'})
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


@login_required
@permission_required('registration.delete_stallregistration', raise_exception=True)
@require_http_methods(['DELETE'])
def stall_registration_cancel_view(request, pk):
    """
    Remove a stall application
    """
    stallregistration = get_object_or_404(StallRegistration, id=pk)
    stallholder = stallregistration.stallholder

    # Get all site allocations associated with the stall registration
    siteallocations = SiteAllocation.currentallocationsmgr.filter(stallholder_id=stallholder.id, stall_registration=pk)

    try:
        # Set stall registration as cancelled
        stallregistration.is_cancelled = True
        stallregistration.to_booking_status_cancelled()
        stallregistration.save(update_fields=['is_cancelled', 'booking_status'])

        # If site allocations exist, update them
        if siteallocations.exists():
            for siteallocation in siteallocations:
                siteallocation.stall_registration = None
                siteallocation.save(update_fields=['stall_registration'])
    except Exception as e:
        db_logger.error('There was an error cancelling the stall application: ' + str(e),
                        extra={'custom_category': 'Stall Application'})

    return HTTPResponseHXRedirect(redirect_to=reverse_lazy("registration:stallregistration-dashboard"))


def get_registration_costs(request, fair_id, parent_id=None, site_size=None, stall_category=None, trestle_num=None, vehicle_length=None, power_req=None):
    total_additional_site_costs = decimal.Decimal(0.00)
    total_vehicle_cost = decimal.Decimal(0.00)

    # check to see if this a stall application update
    if parent_id:
        # Check to see if there are additional sites required
        if AdditionalSiteRequirement.objects.filter(stall_registration_id=parent_id).exists():
            additional_site_list = AdditionalSiteRequirement.objects.filter(stall_registration_id=parent_id)
            for additional_site in additional_site_list:
                site_price = InventoryItemFair.objects.get(fair=fair_id,
                                                           inventory_item__id=additional_site.site_size.id).price
                price_rate = InventoryItemFair.objects.get(fair=fair_id,
                                                           inventory_item__id=additional_site.site_size.id).price_rate
                additional_site_costs = price_rate * site_price * additional_site.site_quantity
                total_additional_site_costs = total_additional_site_costs + additional_site_costs

    if stall_category:
        db_logger.debug(f"Stall category ID: {stall_category}")
        category = StallCategory.objects.get(pk=stall_category)
        if category.has_inventory_item:
            category_price = InventoryItemFair.objects.get(fair=fair_id,
                                                           inventory_item_id=category.inventory_item.id).price
            price_rate = InventoryItemFair.objects.get(fair=fair_id,
                                                       inventory_item_id=category.inventory_item.id).price_rate
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


    if trestle_num:
        trestle_price = InventoryItemFair.objects.get(fair=fair_id, inventory_item__item_name='Trestle Table').price
        price_rate = InventoryItemFair.objects.get(fair=fair_id, inventory_item__item_name='Trestle Table').price_rate
        total_trestle_cost = price_rate * trestle_price * decimal.Decimal(trestle_num)
    else:
        total_trestle_cost = decimal.Decimal(0.00)

    if vehicle_length:
        try:
            # Attempt to convert the vehicle length to a float
            vehicle_length = float(vehicle_length)

            # Check if the vehicle length is greater than 6
            if vehicle_length > 6:
                vehicle_price = InventoryItemFair.objects.get(fair=fair_id,
                                                              inventory_item__item_name='Over 6m vehicle on site').price
                price_rate = InventoryItemFair.objects.get(fair=fair_id,
                                                           inventory_item__item_name='Over 6m vehicle on site').price_rate
                total_vehicle_cost = price_rate * vehicle_price
            else:
                total_vehicle_cost = decimal.Decimal(0.00)

        except ValueError:
            # If conversion to float fails, handle the error (e.g., log or return an appropriate message)
            total_vehicle_cost = decimal.Decimal(0.00)

    if power_req:
        power_price = InventoryItemFair.objects.get(fair=fair_id, inventory_item__item_name='Power Point').price
        price_rate = InventoryItemFair.objects.get(fair=fair_id, inventory_item__item_name='Power Point').price_rate
        power_price = price_rate * power_price
    else:
        power_price = decimal.Decimal(0.00)

    total_cost = (category_price + site_price + total_trestle_cost + total_vehicle_cost + power_price +
                  total_additional_site_costs)
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
        siteallocations = SiteAllocation.currentallocationsmgr.filter(stallholder_id=stallholder.id,
                                                                      stall_registration=pk)
    else:
        siteallocations = None
    # list of active parent comments
    comments = RegistrationComment.objects.filter(stallholder=request.user, is_archived=False,
                                                  convener_only_comment=False, comment_parent__isnull=True,
                                                  fair=registration_fair.id)
    registrationform = StallRegistrationUpdateForm(instance=obj)

    context = {
        'billing': total_cost,
        'stallregistration': obj,
        'registrationform': registrationform,
        'additionalsiteform': additionalsiteform,
        'commentfilterform': commentfilterform,
        'commentform': commentform,
        'replyform': replyform,
        'filter': comment_filter_message,
        'comments': comments,
    }
    if siteallocations:
        context['allocations'] = siteallocations

    # Additional Sites add and display
    addsites_form = AdditionalSiteReqForm(request.POST or None)
    additional_sites = AdditionalSiteRequirement.objects.filter(stall_registration=obj)
    if additional_sites:
        total_cost = get_registration_costs(request, registration_fair.id, pk)
        context['site_requirement_list'] = additional_sites

    if request.htmx:
        site_size = request.POST.get('site_size')
        stall_category = request.POST.get('stall_category')
        trestle_num = request.POST.get('trestle_quantity')
        vehicle_length = request.POST.get('vehicle_length')
        power_req = request.POST.get('power_required')
        template_name = 'stallregistration/stallregistration_partial.html'
        total_cost = get_registration_costs(request, registration_fair.id, pk, site_size, stall_category,
                                            trestle_num, vehicle_length, power_req)
        return TemplateResponse(request, template_name, {
            'billing': total_cost,
            'registrationform': registrationform,
        })
    elif request.method == 'POST':
        site_size = request.POST.get('site_size')
        stall_category = request.POST.get('stall_category')
        trestle_num = request.POST.get('trestle_quantity')
        vehicle_length = request.POST.get('vehicle_length')
        power_req = request.POST.get('power_required')
        total_cost = get_registration_costs(request, registration_fair.id, pk, site_size, stall_category,
                                            trestle_num, vehicle_length, power_req)
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
                    # get Food Application object
                    obj = FoodRegistration.objects.get(registration=new_instance)
                except FoodRegistration.DoesNotExist:  #f FoodRegistration object does not exist
                    # create FoodRegistration object
                    obj = FoodRegistration(registration=new_instance, has_food_certificate=False,
                                           food_fair_consumed=False, has_food_prep=False, is_valid=False)
                    obj.save()
                return redirect('registration:food-registration', stall_registration.id)
            else:
                return HttpResponseRedirect(success_url)
        else:
            db_logger.error('There was an error with saving the stall Application. '
                            + registrationform.errors.as_data(),
                            extra={'custom_category': 'Stall Application'})
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
        # Refresh the obj from the database in case the form validation changed it
        obj = self.get_object()
        context['obj'] = context['foodprepequipment'] = obj
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
    queryset = FoodSaleType.objects.all().order_by('food_sale_type')


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
        # Refresh the obj from the database in case the form validation changed it
        obj = self.get_object()
        context['obj'] = context['foodsaletype'] = obj
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
        # Refresh the obj from the database in case the form validation changed it
        obj = self.get_object()
        context['obj'] = context['stallcategory'] = obj
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
    comment_filter_message = 'Showing current comments of the current fair'
    current_fairs = StallRegistration.objects.filter(fair__is_activated=True)
    commentfilterform = CommentFilterForm(request.POST or None)
    commentform = RegistrationCommentForm(request.POST or None)
    replyform = CommentReplyForm(request.POST or None)
    # list of active parent comments
    current_fair = Fair.currentfairmgr.all().last()
    comments = RegistrationComment.objects.filter(stallholder=request.user, is_archived=False, convener_only_comment=False, comment_parent__isnull=True, fair=current_fair.id)
    try:
        # Use prefetch_related to bring through the site allocation data associated with the stall registration
        myfair_list = StallRegistration.registrationcurrentmgr.filter(stallholder=request.user).prefetch_related(
            'site_allocation').all()
    except ObjectDoesNotExist:
        myfair_list = StallRegistration.registrationcurrentmgr.filter(stallholder=request.user)
    payment_history = PaymentHistory.paymenthistorycurrentmgr.get_stallholder_payment_history( stallholder=request.user).last()
    discounts = DiscountItem.discountitemmgr.get_stallholder_discounts(stallholder=request.user)

    return TemplateResponse(request, template, {
        'payment_history': payment_history,
        'discounts': discounts,
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
    comment_filter_message = 'Showing current comments of the current fair'
    # list of active parent comments
    current_fair = Fair.currentfairmgr.all().last()
    comments = RegistrationComment.objects.filter(stallholder=request.user, is_archived=False,
                                                  convener_only_comment=False, comment_parent__isnull=True,
                                                  fair=current_fair.id)
    foodregistration = get_object_or_404(FoodRegistration, registration=pk)
    food_form = FoodRegistrationForm(instance=foodregistration)
    equipment_form = FoodPrepEquipReqForm(request.POST or None)
    equipment_list = FoodPrepEquipReq.objects.filter(food_registration_id=foodregistration.id)
    if equipment_list:
        context = {
            'food_form': food_form,
            'equipment_form': equipment_form,
            'foodregistration': foodregistration,
            'equipment_list': equipment_list,
            'commentfilterform': commentfilterform,
            'comments': comments,
            'commentform': commentform,
            'replyform': replyform,
            'filter': comment_filter_message,
        }
    else:
        context = {
            'food_form': food_form,
            'equipment_form': equipment_form,
            'foodregistration': foodregistration,
            'commentfilterform': commentfilterform,
            'comments': comments,
            'commentform': commentform,
            'replyform': replyform,
            'filter': comment_filter_message,
        }

    if request.method == 'POST':
        food_form = FoodRegistrationForm(request.POST, request.FILES or None, instance=foodregistration)
        if food_form.is_valid():
            obj = food_form.save(commit=False)
            obj.is_valid = True
            obj.save()
            return HttpResponseRedirect(success_url)
    return TemplateResponse(request, template_name, context)


@login_required
def food_registration_update_view(request, id=None):
    comment_filter_message = 'Showing current comments of the current fair'
    commentfilterform = CommentFilterForm(request.POST or None)
    commentform = RegistrationCommentForm(request.POST or None)
    replyform = CommentReplyForm(request.POST or None)
    current_fair = Fair.currentfairmgr.all().last()
    comments = RegistrationComment.objects.filter(stallholder=request.user, is_archived=False,
                                                  convener_only_comment=False, comment_parent__isnull=True,
                                                  fair=current_fair.id)
    obj = get_object_or_404(FoodRegistration, id=id)
    form = FoodRegistrationForm(request.POST, request.FILES, instance=obj)
    context = {
        "form": form,
        "obj": obj,
        'commentfilterform': commentfilterform,
        'comments': comments,
        'commentform': commentform,
        'replyform': replyform,
        'comment_filter': comment_filter_message
    }
    if form.is_valid():
        obj = form.save(commit=False)
        obj.is_valid = True
        obj.save()
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
            stall_registration_obj = StallRegistration.objects.get(id=pk)
            # if stall application object exist
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
            # get parent food application from hidden input
            try:
                # id integer e.g. 15
                food_registration_id = int(request.POST.get('food_registration_id'))
            except Exception:
                food_registration_id = None
            # if food_registration_id has been submitted get the food_registration_obj id
            if food_registration_id:
                food_registration_obj = FoodRegistration.objects.get(id=food_registration_id)
                # if food application object exist
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


def comments_view_add(request):
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
        comments = RegistrationComment.objects.filter(stallholder=request.user.id, is_archived=False,
                                                      convener_only_comment=False, comment_parent__isnull=True,
                                                      fair=current_fair.id)
    if request.htmx:
        if stallholder_id:
            comments = RegistrationComment.objects.filter(stallholder=stallholder_id, convener_only_comment=False,
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
                db_logger.error('There was an error with saving the comment form. '
                                + commentform.errors.as_data(),
                                extra={'custom_category': 'Comments'})
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


def convener_stall_registration_detail_view(request, id):
    """
    Display the details of the stall and food application data provided by the stallholder
    Includes functionality to update details that have an impact on pricing
    """
    template = "stallregistration/convener_stall_registration_detail.html"
    comment_filter_message = 'Showing current comments of the current fair'
    commentfilterform = CommentFilterForm(request.POST or None)
    commentform = RegistrationCommentForm(request.POST or None)
    replyform = CommentReplyForm(request.POST or None)
    current_fair = Fair.currentfairmgr.all().last()
    stall_registration = StallRegistration.objects.get(id=id)

    # Determine if there are any discounts, if so sum them and add it to the context
    discounts = DiscountItem.objects.filter(stall_registration=stall_registration)
    total_discount = sum(discounts.values_list('discount_amount', flat=True)) if discounts else decimal.Decimal(0.00)

    request.session['stallholder_id'] = stall_registration.stallholder.id
    stallholder_detail = Profile.objects.get(user=stall_registration.stallholder)
    additionalsiteform = AdditionalSiteReqForm(request.POST or None)
    registrationupdateform = StallRegistrtionConvenerEditForm(instance=stall_registration)
    applydiscountform = RegistrationDiscountForm(request.POST or None)
    comments = RegistrationComment.objects.filter(stallholder=stall_registration.stallholder.id, is_archived=False,
                                                  convener_only_comment=False, comment_parent__isnull=True,
                                                  fair=current_fair.id)
    payment_history_list = PaymentHistory.paymenthistorycurrentmgr.get_stallholder_payment_history(
        stallholder=stall_registration.stallholder.id)

    # Initialize food_registration to avoid UnboundLocalError
    food_registration = None
    foodregistrtionupdateform = None

    if stall_registration.selling_food:
        food_registration = FoodRegistration.objects.get(registration=stall_registration)
        foodregistrtionupdateform = FoodRegistrationConvenerEditForm(instance=food_registration)

    context = {
        'registrationupdateform': registrationupdateform,
        'additionalsiteform': additionalsiteform,
        'applydiscountform': applydiscountform,
        'payment_histories': payment_history_list,
        'stallholder_detail': stallholder_detail,
        "stall_data": stall_registration,
        'commentfilterform': commentfilterform,
        'comments': comments,
        'commentform': commentform,
        'replyform': replyform,
        'comment_filter': comment_filter_message,
        'discounts': discounts,
        'total_discount': total_discount,
    }

    # Add food form and additional food-related data if applicable
    if foodregistrtionupdateform:
        context['foodregistrationupdateform'] = foodregistrtionupdateform

    additional_sites = AdditionalSiteRequirement.objects.filter(stall_registration=stall_registration)
    if additional_sites:
        context['site_requirement_list'] = additional_sites

    if stall_registration.multi_site:
        context['additional_sites'] = AdditionalSiteRequirement.objects.filter(stall_registration_id=stall_registration.id)

    if FoodRegistration.objects.filter(registration=id).exists():
        food_registration = FoodRegistration.objects.get(registration=id)
        context["food_data"] = food_registration
        context["equipment_list"] = FoodPrepEquipReq.objects.filter(food_registration=food_registration)

    if request.method == 'POST':
        registrationupdateform = StallRegistrtionConvenerEditForm(request.POST, request.FILES or None,
                                                                  instance=stall_registration)
        foodregistrtionupdateform = FoodRegistrationConvenerEditForm(request.POST, request.FILES or None,
                                                                     instance=food_registration) if food_registration else None
        applydiscountform = RegistrationDiscountForm(request.POST or None)

        if 'discount' in request.POST and applydiscountform.is_valid():
            new_discount = applydiscountform.save(commit=False)
            new_discount.stall_registration = stall_registration
            new_discount.created_by = request.user
            new_discount.save()
            stall_registration.is_invoiced = False
            stall_registration.save()
            # revert the registration to amended so that obvious to the convener that it needs to be reinvoiced
            if can_proceed(stall_registration.to_booking_status_amended):
                stall_registration.to_booking_status_amended()
                stall_registration.save()
            return redirect(request.META.get('HTTP_REFERER'))

        if 'update' in request.POST and registrationupdateform.is_valid():
            stall_registration = registrationupdateform.save(commit=False)
            stall_registration.is_invoiced = False
            stall_registration.save()
            # revert the registration to amended so that obvious to the convener that it needs to be reinvoiced
            if can_proceed(stall_registration.to_booking_status_amended):
                stall_registration.to_booking_status_amended()
                stall_registration.save()

            if foodregistrtionupdateform and foodregistrtionupdateform.is_valid():
                food_registration = foodregistrtionupdateform.save(commit=False)
                food_registration.save()

    return TemplateResponse(request, template, context)


def stallholder_stall_registration_detail_view(request, id):
    """
    Display the details of the stall and food application data provided by the stallholder
    """
    template = "stallregistration/stallholder_stall_registration_detail.html"
    comment_filter_message = 'Showing current comments of the current fair'
    commentfilterform = CommentFilterForm(request.POST or None)
    commentform = RegistrationCommentForm(request.POST or None)
    replyform = CommentReplyForm(request.POST or None)
    current_fair = Fair.currentfairmgr.all().last()
    stall_registration = StallRegistration.registrationcurrentallmgr.get(id=id)
    food_registration = FoodRegistration.objects.get(registration=stall_registration)
    request.session['stallholder_id'] = stall_registration.stallholder.id
    stallholder_detail = Profile.objects.get(user=stall_registration.stallholder)
    comments = RegistrationComment.objects.filter(stallholder=stall_registration.stallholder.id, is_archived=False,
                                                  convener_only_comment=False, comment_parent__isnull=True,
                                                  fair=current_fair.id)
    registrationupdateform = StallRegistrationStallholderEditForm(instance=stall_registration)
    foodregistrtionupdateform = FoodRegistrationStallholderEditForm(instance=food_registration)
    equipment_form = FoodPrepEquipReqForm(request.POST or None)
    context = {
        'registrationupdateform': registrationupdateform,
        'foodregistrationupdateform': foodregistrtionupdateform,
        'equipment_form': equipment_form,
        'stallholder_detail': stallholder_detail,
        "stall_data": stall_registration,
        'commentfilterform': commentfilterform,
        'comments': comments,
        'commentform': commentform,
        'replyform': replyform,
        'comment_filter': comment_filter_message
    }
    if stall_registration.multi_site:
        context['additional_sites'] = AdditionalSiteRequirement.objects.filter(
            stall_registration_id=stall_registration.id)

    if FoodRegistration.objects.filter(registration=id).exists():
        context["food_data"] = food_registration = FoodRegistration.objects.get(registration=id)
        context["equipment_list"] = FoodPrepEquipReq.objects.filter(food_registration=food_registration)

    if request.method == 'POST':
        registrationupdateform = StallRegistrationStallholderEditForm(request.POST, request.FILES or None,
                                                                      instance=stall_registration)
        foodregistrtionupdateform = FoodRegistrationStallholderEditForm(request.POST, request.FILES or None,
                                                                        instance=food_registration)
        if registrationupdateform.is_valid() and foodregistrtionupdateform.is_valid():
            stall_registration = registrationupdateform.save(commit=False)
            stall_registration.save()
            food_registration = foodregistrtionupdateform.save(commit=False)
            food_registration.save()

        else:
            db_logger.error('There was an error with updating the stall Application. '
                            + registrationupdateform.errors.as_data(),
                            extra={'custom_category': 'Stall Application'})
            return TemplateResponse(request, template, context)

    return TemplateResponse(request, template, context)


def submit_stall_registration(request, id):
    """
    Stall holder driven request to submit a stall application  to status submitted for the convener to  review
    """
    success_url = reverse_lazy('registration:stallregistration-dashboard')
    stallregistration = get_object_or_404(StallRegistration, pk=id)
    stallholder_id = stallregistration.stallholder.id
    if not can_proceed(stallregistration.to_booking_status_submitted):
        raise PermissionDenied
    error_comment, is_ok = validate_stallregistration(stallholder_id, stallregistration)
    if not is_ok:
        comment_type = CommentType.objects.get(type_name__in=['Submission Error'])
        obj = RegistrationComment.createregistrationcommentmgr.create_comment(stallregistration.stallholder,
                                                                              stallregistration.fair, comment_type,
                                                                              error_comment)
        return HttpResponseRedirect(success_url)

    stallregistration.to_booking_status_submitted()
    stallregistration.save()
    return HttpResponseRedirect(success_url)


@login_required
@permission_required('registration.change_stallregistration', raise_exception=True)
def reinvoice_stall_registration(request, id):
    """
    Convener driven request to re-invoice a stallregistration. it is needed if cost driven items are added to a stall
    application by the convener or if a discount has been applied to the stallregistration.
    """
    stallregistration = get_object_or_404(StallRegistration, pk=id)
    if not can_proceed(stallregistration.to_booking_status_invoiced):
        raise PermissionDenied

    InvoiceItem.invoiceitemmgr.create_invoice_items(stallregistration)

    # check that the invoice and payment history records has been created
    invoices = Invoice.invoicecurrentmgr.get_registration_invoices(stallregistration)
    payment_history = PaymentHistory.paymenthistorycurrentmgr.get_registration_payment_history(stallregistration)
    if invoices and payment_history:
        stallregistration.to_booking_status_invoiced()
        stallregistration.is_invoiced = True
        stallregistration.save()
    else:
        db_logger.error('There was an error with the creation of the re-invoice and payment history for '
                        'stallregistration ID ' + str(stallregistration.id),
                        extra={'custom_category': 'Stall Application Invoicing'})

    return redirect(request.META.get('HTTP_REFERER'))


def invoice_stall_registration(request, id):
    """
    Stall holder driven request to submit a stall application to the status invoiced.  This initiates a multi-step
    process to firstly check to see whether the registration can be moved to invoiced without convener review. If it
    passes the tests the status of the registration is changed to invoiced, if it fails a comment is created
    detailing why it requires the convener's review, and it's status is changed to submitted.
    If it missing data the submission will be rejected and the items that nee to be rectified detailed in comment
    message the Comment type is Submission Error (8) Comment type
    If the stallregistrationis correct but cannot be progressed without Convener intervention the details of this
    will be detailed in an Invoicing (4) Comment type
    """
    success_url = reverse_lazy('registration:stallregistration-dashboard')
    stallregistration = get_object_or_404(StallRegistration, pk=id)
    stallholder_id = stallregistration.stallholder.id
    if not can_proceed(stallregistration.to_booking_status_invoiced):
        raise PermissionDenied

    # Check to see if stallregistration is complete otherwise create stallholder comment detailing the issues
    error_comment, is_ok = validate_stallregistration(stallholder_id, stallregistration)
    if not is_ok:
        comment_type = CommentType.objects.get(type_name__in=['Submission Error'])
        obj = RegistrationComment.createregistrationcommentmgr.create_comment(stallregistration.stallholder,
                                                                              stallregistration.fair, comment_type,
                                                                              error_comment)
        return HttpResponseRedirect(success_url)

    # Check to see if stallregistration can be invoiced otherwise submit it for convener review
    error_comment, is_ok = check_needs_convener_review(stallregistration)
    if not is_ok:
        is_done_flag = True  # So created comment doesn't respond to unactioned comments test.
        comment_type = CommentType.objects.get(type_name__in=['Invoicing'])
        obj = RegistrationComment.createregistrationcommentmgr.create_comment(stallregistration.stallholder,
                                                                              stallregistration.fair, comment_type,
                                                                              error_comment, is_done_flag)
        # Set the registration to submitted
        if can_proceed(stallregistration.to_booking_status_submitted):
            stallregistration.to_booking_status_submitted()
            stallregistration.save()

        return HttpResponseRedirect(success_url)
    InvoiceItem.invoiceitemmgr.create_invoice_items(stallregistration)

    # check that the invoice and payment history records has been created
    invoices = Invoice.invoicecurrentmgr.get_registration_invoices(stallregistration)
    payment_history = PaymentHistory.paymenthistorycurrentmgr.get_registration_payment_history(stallregistration)
    if invoices and payment_history:
        stallregistration.to_booking_status_invoiced()
        stallregistration.is_invoiced = True
        stallregistration.save()
    else:
        db_logger.error('There was an error with the creation of the invoice and payment history for '
                        'stallregistration ID '
                        + stallregistration.id,
                        extra={'custom_category': 'Stall Registration Invoicing'})

    return HttpResponseRedirect(success_url)


def check_needs_convener_review(stallregistration):
    """
    Check to sse if the stall and food registration submission  need convener input before the cost of the
    registration can be invoiced.
    Args:
        stallregistration : instance of stallregistration
    Returns:
        Boolean : True / False
    error_comment: String of the issues found that can be used to create a stall holder comment
    """
    error_comment = "Stall registration ID " + str(stallregistration.id) + (' will need to be reviewed by the convener '
                                                                            'because:\n')
    is_ok = True
    if stallregistration.vehicle_on_site:
        not_oversize = StallRegistration.vehicleonsitemgr.not_oversize(stallregistration.id)
        if not_oversize:
            pass
        else:
            error_comment = error_comment + '- you have a vehicle on site that is over 6 metres in length.\n'
            is_ok = False
    if stallregistration.multi_site:
        error_comment = error_comment + ('- you have requested a multi-site registration the extra sites will need to '
                                         'be allocated by the convener.\n')
        is_ok = False
    if stallregistration.selling_food:
        valid_cert = FoodRegistration.certificatevaliditymgr.not_expiring(stallregistration.id)
        if valid_cert:
            pass
        else:
            error_comment = error_comment + '- the food certificate is not valid for the period of the fair.'
            is_ok = False
    if is_ok:
        error_comment = ''
    return error_comment, is_ok


def validate_stallregistration(stallholder_id, stallregistration):
    """
    Check to see if stallregistrtion is complete otherwise create stallholder comment detailing the issues .
    used by the invoice_stall_registration and submit_stall_registration functions
    Args:
        stallregistration : instance of stallregistration
    Returns:
        Boolean : True / False
        error_comment: String of the issues found that can be used to create a stall holder comment
    """
    error_comment = "Stall registration ID " + str(stallregistration.id) + ' cannot be submitted because \n'
    is_ok = True
    has_unactioned_comments = RegistrationComment.hasunactionedcommentsmgr.filter_by_stallholder(
        stallholder_id).exists()
    if has_unactioned_comments:
        error_comment = error_comment + ' - there are unactioned comments that need to be resolved.\n'
        is_ok = False
    if stallregistration.vehicle_on_site:
        has_size = StallRegistration.vehicleonsitemgr.has_size(stallregistration.id)
        has_image = StallRegistration.vehicleonsitemgr.has_image(stallregistration.id)
        if has_size and has_image:
            pass
        else:
            error_comment = error_comment + (' - you have a vehicle on site and you have not declared its size or  '
                                             'provided an image of the vehicle.\n')
            is_ok = False
    if stallregistration.multi_site:
        has_related_objects = AdditionalSiteRequirement.objects.filter(
            stall_registration_id=stallregistration.id).exists()
        if has_related_objects:
            pass
        else:
            error_comment = error_comment + (' - you have asked for a multi site registration but have not provided '
                                             'the requirements for the additional site(s).\n')
            is_ok = False
    if stallregistration.selling_food:
        has_cert = FoodRegistration.certificatevaliditymgr.has_certificate(stallregistration.id)
        if has_cert:
            pass
        else:
            error_comment = error_comment + ' - you need to upload your food certificate'
            is_ok = False
    if is_ok:
        error_comment = ''
    return error_comment, is_ok


def transition_booking_status(request, stall_registration_id, target_status):
    stall_registration = get_object_or_404(StallRegistration, id=stall_registration_id)

    # Get the appropriate transition method based on the target_status
    for transition in stall_registration.get_available_booking_status_transitions():
        if transition.target == target_status:
            method = getattr(stall_registration, transition.name)
            method()  # Call the method on the stall_registration instance
            stall_registration.save()
            break

    return redirect(request.META.get('HTTP_REFERER'))
