# faq/views.py

from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.response import TemplateResponse
from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
)

from faq.models import (
    FAQ,
)
from fairs.models import(
    InventoryItemFair
)
from .forms import(
    FaqCreateForm,
    FaqFilterForm,
    FaqUpdateForm,
)


# Create your views here.
class FaqCreateView(PermissionRequiredMixin, CreateView):
    """
    Create a FAQ
    """
    permission_required = 'faq.add_faq'
    model = FAQ
    form_class = FaqCreateForm
    template_name = 'faq_create.html'
    success_url = reverse_lazy('faq:faq-list')


def pagination_data(faq_per_page, filtered_data, request):
    """
    Refactored pagination code that is available to all views that included pagination
    It takes request, cards per page, and filtered_data and returns the page_list and page_range
    """
    paginator = Paginator(filtered_data, per_page=faq_per_page)
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


def faq_listview(request):
    """
    List  Fair FAQ, this is available for the genera public and those who are logged into the system
    """
    global faq_filter_dict
    alert_message = ''
    template_name = 'faq_list.html'
    faq_per_page = 8
    current_prices = InventoryItemFair.currentinventoryitemfairmgr.all()

    filterform = FaqFilterForm(request.POST or None)
    form_purpose = filterform.data.get('form_purpose', '')

    if request.htmx:
        if form_purpose == 'filter':
            # Handle filter form submission
            category = filterform.data.get('category', '')
            if category:
                faq_filter_dict['category'] = category
                alert_message = f'There are no FAQs of category {category} created yet'
            else:
                faq_filter_dict = {}
                alert_message = 'There are no FAQs yet.'
        else:
            # Handle pagination
            # The filter _dict is retained from the filter selection which ensures that the correct data is appplied
            # to subsequent pages
            pass
        # Alert message logic
        template_name = 'faq_list_partial.html'
    else:
        faq_filter_dict ={}

    # Apply filters to the queryset
    filtered_data = FAQ.activefaqmgr.filter(**faq_filter_dict).order_by("category").all()

    # Pagination logic
    page_list, page_range = pagination_data(faq_per_page, filtered_data, request)
    faq_list = page_list

    # Template response
    return TemplateResponse(request, template_name, {
        'filterform': filterform,
        'faq_list': faq_list,
        'page_range': page_range,
        'current_prices': current_prices,
        'alert_mgr': alert_message,
    })


class FaqDetailUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Display an editable form of Fair FAQ
    """
    permission_required = 'faq.change_faq'
    model = FAQ
    form_class = FaqUpdateForm
    template_name = 'faq_detail.html'
    success_url = reverse_lazy('faq:faq-list')


