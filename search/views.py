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


def stallholder_search_view(request):
    """
    Search for Stallholders
    """
    search_text = request.POST.get('search')

    results = CustomUser.stallholdermgr.filter(
        Q(id__icontains=search_text) | Q(first_name__icontains=search_text) | Q(last_name__icontains=search_text) |
        Q(profile__org_name__icontains=search_text) | Q(email__icontains=search_text))
    context = {'results': results}
    return render(request, 'search/partials/stallholder_results.html', context)
