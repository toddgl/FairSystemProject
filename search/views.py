# search/views.py
from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.db.models import Q
from accounts.models import (
    CustomUser,
)
from registration.models import(
    StallRegistration
)
from utils.site_allocation_tools import site_allocations


def search_view(request):
    query = request.GET.get('q')

    context = {
        "query": query
    }
    template = 'search/results_view.html'

    if request.htmx:
        template = 'search/partials/results.html'
    return render(request, template, context)


def stallholder_registration_search_view(request):
    """
    Search for Stallholders customised for the stall registrations listing
    """
    search_text = request.POST.get('search')

    results = CustomUser.stallholdermgr.filter(
        Q(id__icontains=search_text) | Q(first_name__icontains=search_text) | Q(last_name__icontains=search_text) |
        Q(profile__org_name__icontains=search_text) | Q(phone__icontains=search_text) | Q(email__icontains=search_text))

    if 'registration' not in request.session:
        context = {
            'results': results
        }
    else:
        registration = request.session['registration']
        context = {
            'results': results,
            'registration': registration
        }
    return render(request, 'search/partials/stallholder_registration_results.html', context)

def stallholder_reports_search_view(request):
    """
    Search for Stallholders customised for the report listing
    """
    search_text = request.POST.get('search')

    results = CustomUser.stallholdermgr.filter(
        Q(id__icontains=search_text) | Q(first_name__icontains=search_text) | Q(last_name__icontains=search_text) |
        Q(profile__org_name__icontains=search_text) | Q(phone__icontains=search_text) | Q(email__icontains=search_text))

    if 'reports' not in request.session:
        context = {
            'results': results
        }
    else:
        reports = request.session['reports']
        context = {
            'results': results,
            'reports': reports
        }
    return render(request, 'search/partials/stallholder_reports_results.html', context)

def stallholder_siteallocation_search_view(request):
    """
    Search for Stallholders customised for the siteallocation listing
    """
    b reearch_text = request.POST.get('search')
    siteallocation = request.session.get('siteallocation')
    if not siteallocation:
        return HttpResponseBadRequest("No site allocation found in session")
    results = CustomUser.stallholdermgr.filter(
        Q(id__icontains=search_text) | Q(first_name__icontains=search_text) | Q(last_name__icontains=search_text) |
        Q(profile__org_name__icontains=search_text) | Q(phone__icontains=search_text) | Q(email__icontains=search_text))
    context = {
        'results': results,
        'siteallocation': siteallocation
    }
    return render(request, 'search/partials/stallholder_siteallocation_results.html', context)

def create_siteallocation_search_view(request):
    """
    Search for Stallholders customised for the siteallocation creation
    """
    search_text = request.POST.get('search')


    results = CustomUser.stallholdermgr.filter(
        Q(id__icontains=search_text) | Q(first_name__icontains=search_text) | Q(last_name__icontains=search_text) |
        Q(profile__org_name__icontains=search_text) | Q(phone__icontains=search_text) | Q(email__icontains=search_text))
    context = {
        'results': results,
    }
    return render(request, 'search/partials/stallholder_create_siteallocation_results.html', context)

def stallholder_history_search_view(request):
    """
    Search for Stallholders customised for the site history dashboard
    """
    search_text = request.POST.get('search')
    stallhistory = request.session.get('stallhistory', None)

    # Handle cases where the stallhistory  might be missing
    if not stallhistory:
        # Optionally, set a default value or handle the error
        return render(request, 'search/partials/stallholder_history_results.html', {
            'error': 'Stall History not found in session',
            'results': []
        })

    results = CustomUser.stallholdermgr.filter(
        Q(id__icontains=search_text) | Q(first_name__icontains=search_text) | Q(last_name__icontains=search_text) |
        Q(profile__org_name__icontains=search_text) | Q(phone__icontains=search_text) | Q(email__icontains=search_text))
    context = {
        'results': results,
        'stallhistory': stallhistory
    }
    return render(request, 'search/partials/stallholder_history_results.html', context)

def stallholder_search_view(request):
    """
    Search for Stallholders customised for the messages listing
    """
    search_text = request.POST.get('search', '')

    results = CustomUser.stallholdermgr.filter(
        Q(id__icontains=search_text) | Q(first_name__icontains=search_text) | Q(last_name__icontains=search_text) |
        Q(profile__org_name__icontains=search_text) | Q(phone__icontains=search_text) | Q(email__icontains=search_text))
    context = {
        'results': results,
    }
    return render(request, 'search/partials/stallholder_results.html', context)


def stallholder_list_search_view(request):
    """
    Search for Stallholders customised for the siteallocation list display
    """
    search_text = request.POST.get('search')
    target = request.session['target']

    results = CustomUser.stallholdermgr.filter(
        Q(id__icontains=search_text) | Q(first_name__icontains=search_text) | Q(last_name__icontains=search_text) |
        Q(profile__org_name__icontains=search_text) | Q(email__icontains=search_text))
    context = {
        'results': results,
        'target': target
    }
    return render(request, 'search/partials/stallholder_list_results.html', context)

def stallholder_payment_history_search_view(request):
    """
    Search for Stallholders customised for the payment histories list display
    """

    search_text = request.POST.get('search')

    results = CustomUser.stallholdermgr.filter(
        Q(id__icontains=search_text) | Q(first_name__icontains=search_text) | Q(last_name__icontains=search_text) | Q(profile__org_name__icontains=search_text) | Q(email__icontains=search_text))
    context = {
        'results': results,
    }
    return render(request, 'search/partials/stallholder_paymenthistory_results.html', context)

def stallholder_email_history_search_view(request):
    """
    Search for Stallholders customised for the siteallocation list display
    """

    search_text = request.POST.get('search')

    results = CustomUser.stallholdermgr.filter(
        Q(id__icontains=search_text) | Q(first_name__icontains=search_text) | Q(last_name__icontains=search_text) | Q(profile__org_name__icontains=search_text) | Q(email__icontains=search_text))
    context = {
        'results': results,
    }
    return render(request, 'search/partials/stallholder_emailhistory_results.html', context)


def stall_search_view(request):
    """
    Search used to locate stall at a fair hased on vehicle registration, manager name, product description or stall description
    """
    search_text = request.POST.get('search')

    stalls = StallRegistration.registrationcurrentallmgr.exclude(booking_status='Cancelled').prefetch_related('site_allocation')

    results = stalls.filter(
        Q(id__icontains=search_text) |
        Q(stall_manager_name__icontains=search_text) |
        Q(manager_vehicle_registration__icontains=search_text) |
        Q(stall_description__icontains=search_text) |
        Q(products_on_site__icontains=search_text) |
        Q(site_allocation__event_site__site__site_name__icontains=search_text)
    )
    context = {
        'results': results
    }
    return render(request, 'search/partials/stall_search_results.html', context)

def stallholder_powerbox_search_view(request):
    """
    Search for Stallholders customised for the powerbox siteallocation list display
    """

    search_text = request.POST.get('search')

    results = CustomUser.stallholdermgr.filter(
        Q(id__icontains=search_text) | Q(first_name__icontains=search_text) | Q(last_name__icontains=search_text) | Q(profile__org_name__icontains=search_text) | Q(email__icontains=search_text))
    context = {
        'results': results,
    }
    return render(request, 'search/partials/stallholder_powerbox_results.html', context)

def stallholder_site_history_update_search_view(request):
    """
    Search for Stallholders customised for the site history update view display
    """

    search_text = request.POST.get('search')

    results = CustomUser.stallholdermgr.filter(
        Q(id__icontains=search_text) | Q(first_name__icontains=search_text) | Q(last_name__icontains=search_text) | Q(profile__org_name__icontains=search_text) | Q(email__icontains=search_text))
    context = {
        'results': results,
    }
    return render(request, 'search/partials/stallholder_site_history_update_results.html', context)

def stallholder_discount_search_view(request):
    """
    Search for Stallholders customised for the discount list display
    """

    search_text = request.POST.get('search')

    results = CustomUser.stallholdermgr.filter(
        Q(id__icontains=search_text) | Q(first_name__icontains=search_text) | Q(last_name__icontains=search_text) | Q(profile__org_name__icontains=search_text) | Q(email__icontains=search_text))
    context = {
        'results': results,
    }
    return render(request, 'search/partials/stallholder_discount_results.html', context)

