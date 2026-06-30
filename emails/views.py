# email/views.py
from allauth.account.views import email
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.admin.templatetags.admin_list import pagination
from django.contrib.auth.decorators import login_required, permission_required
from django.template.response import TemplateResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import (
    Email
)
from .forms import (
    EmailHistoryFilterForm
)
from fairs.models import (
    Fair
)

from django.db.models import Count

from emails.services.email_history_service import EmailHistoryService

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


def email_history_dashboard_view(request):
    """
    Populate the email history dashboard with email history data.
    Display counts and percentages for various subject types.
    """
    email_histories = Email.emailhistorycurrentmgr.all()

    # Count occurrences of each subject_type
    subject_counts = email_histories.filter(subject_type__isnull=False).values(
    'subject_type__type_name', 'subject_type' ).annotate(count=Count('id')).order_by('-count')

    # Total email count
    total_count = email_histories.count()

    # Prepare data with percentages
    subject_stats = []
    for subject in subject_counts:
        count = subject['count']
        percentage = (count / total_count * 100) if total_count > 0 else 0
        subject_stats.append({
            'id': subject.get('subject_type', None),  # Use .get() to avoid KeyError
            'name': subject.get('subject_type__type_name', 'Unknown'),  # Default name if missing
            'count': count,
            'percentage': round(percentage, 2)
        })

    template_name = 'dashboard_emails.html'

    return TemplateResponse(request, template_name, {
        'email_histories': email_histories,
        'subject_stats': subject_stats,
        'total_count': total_count,
    })


def parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


@login_required
@permission_required('emails.view_email', raise_exception=True)
def email_history_listview(request):
    """
    List emails sent to stallholders.

    Filtering is performed entirely from GET parameters so that
    pagination naturally preserves the current filter state.
    """

    filterform = EmailHistoryFilterForm(request.GET or None)
    current_fair = Fair.currentfairmgr.last()
    cards_per_page = 5

    template_name = (
        "email_history_list_partial.html"
        if request.htmx
        else "email_history_list.html"
    )

    fair = None
    selected_stallholder = None

    if filterform.is_valid():
        fair = filterform.cleaned_data["fair"]
        selected_stallholder = filterform.cleaned_data["selected_stallholder"]

    filter_data = EmailHistoryService.get_filters(
        fair=fair,
        stallholder_id=selected_stallholder,
        subject_type=request.GET.get("subject_type"),
        current_fair=current_fair,
    )

    queryset = EmailHistoryService.get_queryset(filter_data)

    email_list, page_range = pagination_data(
        cards_per_page,
        queryset,
        request,
    )

    return TemplateResponse(
        request,
        template_name,
        {
            "filterform": filterform,
            "email_list": email_list,
            "page_range": page_range,
            "alert_message": filter_data.alert_message,
            "subject_type": filter_data.subject_type,
            "selected_stallholder": filter_data.selected_stallholder,
        },
    )