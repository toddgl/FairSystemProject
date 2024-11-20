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


@login_required
@permission_required('emails.view_email', raise_exception=True)
def email_history_listview(request):
    """
    List emails sent to stallholders, filtered by subject_type and stallholder.
    """
    current_fair = Fair.currentfairmgr.last()
    cards_per_page = 30
    template_name = 'email_history_list.html'
    filterform = EmailHistoryFilterForm(request.POST or None)

    # Get filters from the request
    subject_type = request.GET.get('subject_type', '')
    stallholder_id = request.POST.get('selected_stallholder' or None)
    form_purpose = filterform.data.get('form_purpose', '') if filterform.is_bound else None
    email_filter_dict = {}

    # Subject type filtering
    if subject_type:
        email_filter_dict['subject_type_id'] = subject_type
        alert_message = f'There are no email messages of type {subject_type} created yet.'
    else:
        alert_message = 'There are no emails created yet.'

    # Stallholder and fair filtering
    if request.htmx and form_purpose == 'filter' and filterform.is_valid():
        fair = filterform.cleaned_data.get('fair')
        if stallholder_id:
            email_filter_dict['stallholder'] = stallholder_id
            alert_message = f'There are no emails where the stallholder ID is {stallholder_id}.'
        if fair:
            email_filter_dict['fair'] = fair
            alert_message = f'There are no emails where the fair is {fair}.'

    elif stallholder_id:
            # Append stallholder if only stallholder is selected without form filtering
            email_filter_dict['stallholder'] = stallholder_id
            alert_message = f'There are no emails where the stallholder ID is {stallholder_id} at the current fair.'
    else:
        email_filter_dict['fair'] = current_fair

    # Fetch filtered data
    filtered_data = Email.emailhistorycurrentmgr.filter(**email_filter_dict).order_by('-date_sent')
    page_list, page_range = pagination_data(cards_per_page, filtered_data, request)
    email_list = page_list

    # Adjust template for HTMX requests
    if request.htmx:
        template_name = 'email_history_list_partial.html'

    return TemplateResponse(request, template_name, {
        'filterform': filterform,
        'email_list': email_list,
        'page_range': page_range,
        'alert_message': alert_message,
        'subject_type': subject_type,
    })
