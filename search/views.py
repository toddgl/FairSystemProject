# search/views.py
from django.shortcuts import render
from django.db.models import Q
from accounts.models import (
    CustomUser,
)


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
    registration = request.session['registration']

    results = CustomUser.stallholdermgr.filter(
        Q(id__icontains=search_text) | Q(first_name__icontains=search_text) | Q(last_name__icontains=search_text) |
        Q(profile__org_name__icontains=search_text) | Q(phone__icontains=search_text) | Q(email__icontains=search_text))
    context = {
        'results': results,
        'registration': registration
    }
    return render(request, 'search/partials/stallholder_registration_results.html', context)

def stallholder_siteallocation_search_view(request):
    """
    Search for Stallholders customised for the siteallocation listing
    """
    search_text = request.POST.get('search')
    siteallocation = request.session['siteallocation']
    print('Using stallholder_siteallocation_search_view')
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

    print('Using create_siteallocation_search_view')

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
    stallhistory = request.session['stallhistory']

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
    search_text = request.POST.get('search')
    message = request.session['message']

    results = CustomUser.stallholdermgr.filter(
        Q(id__icontains=search_text) | Q(first_name__icontains=search_text) | Q(last_name__icontains=search_text) |
        Q(profile__org_name__icontains=search_text) | Q(phone__icontains=search_text) | Q(email__icontains=search_text))
    context = {
        'results': results,
        'message': message
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
