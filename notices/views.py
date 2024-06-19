# notices/views.py

from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.response import TemplateResponse
from django.views.generic import (
    CreateView,
    UpdateView,
)

from notices.models import (
    Notice,
)
from .forms import(
    NoticeCreateForm,
    NoticeUpdateForm
)

class NoticeCreateView(PermissionRequiredMixin, CreateView):
    """
    Create a Notice
    """
    permission_required = 'notices.add_notice'
    model = Notice
    form_class = NoticeCreateForm
    template_name = 'notice_create.html'
    success_url = reverse_lazy('notices:notice-list')

class NoticeDetailUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Display an editable form of Fair Notices
    """
    permission_required = 'notices.change_notice'
    model = Notice
    form_class = NoticeUpdateForm
    template_name = 'notice_detail.html'
    success_url = reverse_lazy('notices:notice-list')

def pagination_data(notice_per_page, filtered_data, request):
    """
    Refactored pagination code that is available to all views that included pagination
    It takes request, cards per page, and filtered_data and returns the page_list and page_range
    """
    paginator = Paginator(filtered_data, per_page=notice_per_page)
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

def notice_listview(request):
    """
    List  Fair Notices, this is available for the genera public and those who are logged into the system
    """
    template_name = 'notice_list.html'
    notice_per_page = 8

    #  Get Notices
    notice_data = Notice.activenoticemgr.all()
    if request.htmx:
        # Handle paqgination
        template_name = 'notice_list_partial.html'

    # Pagination logic
    page_list, page_range = pagination_data(notice_per_page, notice_data, request)
    notice_list = page_list

    # Template response
    return TemplateResponse(request, template_name, {
        'notice_list': notice_list,
        'page_range': page_range,
    })



