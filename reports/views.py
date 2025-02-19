from wsgiref.util import request_uri

import datetime
import csv
from django.shortcuts import get_object_or_404, render
from django.db.models import F, Subquery, OuterRef
from django.db.models.functions import Coalesce
from weasyprint import HTML, CSS
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import get_template
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.db.models import Max, Case, When, Value, IntegerField, BooleanField
from django.contrib.postgres.aggregates import StringAgg  # PostgreSQL only

from payment.views import mitre10_financial_report_view
from .forms import (
    ReportListFilterForm,
    StallRegistrationIDFilterForm
)

from accounts.models import (
    Profile
)

from fairs.models import (
    Event,
    Fair,
    PowerBox,
    SiteHistory,
    Zone,
    ZoneMap
)

from registration.models import(
    StallRegistration
)


def reports_listview(request):
    """
    Page as a launch point for the convener reports that can be generated by the system
    """
    template_name = 'dashboards/dashboard_reports_filter.html'
    filterform = ReportListFilterForm(request.POST or None)
    stallregistrationform = StallRegistrationIDFilterForm(request.POST or None)
    form_purpose = filterform.data.get('form_purpose', '')
    alert_message = ''
    zone = None  # Initialize zone to avoid UnboundLocalError
    event = None  # Initialize event to avoid UnboundLocalError

    # Handle HTMX request for filtering
    if request.htmx:
        if form_purpose == 'filter' and filterform.is_valid():
            zone = filterform.cleaned_data.get('zone')  # Use .get() to avoid KeyError
            event = filterform.cleaned_data.get('event')  # Use .get() to avoid KeyError

            # Handle storing session data based on the presence of zone and event
            if event:  # Event is always required
                request.session['selected_event_id'] = event.id
            else:
                alert_message = 'An event must be selected.'

            if zone:  # Zone is optional for certain situations
                request.session['selected_zone_id'] = zone.id

            # Check if we need a response
            if zone and event:
                return TemplateResponse(request, 'partials/zone_selected.html', {'zone': zone, 'event': event})
            elif event:
                return TemplateResponse(request, 'partials/event_selected.html', {'event': event})
            else:
                alert_message = 'Invalid filter selection.'

    # Handle POST request for generating reports
    elif request.method == 'POST':
        if 'marshalllist' in request.POST:
            # Marshalllist requires both zone and event
            zone_id = request.session.get('selected_zone_id')
            event_id = request.session.get('selected_event_id')

            if zone_id and event_id:
                try:
                    zone = Zone.objects.get(id=zone_id)
                    event = Event.objects.get(id=event_id)
                    return marshall_zone_report(request, zone.id, event.id)
                except Zone.DoesNotExist:
                    alert_message = 'The selected zone could not be found.'
                except Event.DoesNotExist:
                    alert_message = 'The selected event could not be found.'
            else:
                alert_message = 'Both a zone and an event must be selected to generate the marshall list.'

        if 'trestlereport' in request.POST:
            # Trestlereport only requires event
            event_id = request.session.get('selected_event_id')

            if event_id:
                try:
                    event = Event.objects.get(id=event_id)
                    return trestle_distribution_report(request, event.id)
                except Event.DoesNotExist:
                    alert_message = 'The selected event could not be found.'
            else:
                alert_message = 'An event must be selected to generate the trestle distribution report.'

        if 'foodstallreport' in request.POST:
            # Food stall report only requires event
            event_id = request.session.get('selected_event_id')

            if event_id:
                try:
                    event = Event.objects.get(id=event_id)
                    return food_stall_site_report(request, event.id)
                except Event.DoesNotExist:
                    alert_message = 'The selected event could not be found.'
            else:
                alert_message = 'An event must be selected to generate the food stall sites report.'

        if 'searchstalllist' in request.POST:
            # Food stall report only requires event
            event_id = request.session.get('selected_event_id')

            if event_id:
                try:
                    event = Event.objects.get(id=event_id)
                    return stall_search_report(request, event.id)
                except Event.DoesNotExist:
                    alert_message = 'The selected event could not be found.'
            else:
                alert_message = 'An event must be selected to generate the stall stall sites report.'

        if 'stallcsv' in request.POST:
            # Search stall csv generation report only requires event
            event_id = request.session.get('selected_event_id')

            if event_id:
                try:
                    event = Event.objects.get(id=event_id)
                    return stall_search_csv_report(request, event.id)
                except Event.DoesNotExist:
                    alert_message = 'The selected event could not be found.'
            else:
                alert_message = 'An event must be selected to generate the food stall sites csv report.'

        if 'mitre10report' in request.POST:
            # Mitre 10 payment generation report doesn't require zone or event
            return mitre10_financial_report_view(request)

        if 'passpack' in request.POST:
            # Pass Pack  only requires stallregistration id to be provided

            if stallregistrationform.is_valid():
            # Access the cleaned data from the form
                stallregistration_id = stallregistrationform.cleaned_data['stallregistration_id']


            if stallregistration_id:
                try:
                    stallregistration = StallRegistration.objects.get(id=stallregistration_id)

                    return fair_passpack_generator(request, stallregistration.id)
                except StallRegistration.DoesNotExist:
                    alert_message = 'The selected stallregistration could not be found.'
            else:
                alert_message = 'A stallregistration must be selected to generate the pass pack.'

    # Default template response for GET and invalid cases
    context = {
        'filterform': filterform,
        'stallregistrationfilterform': stallregistrationform,
        'zone': zone,
        'alert_message': alert_message
    }
    return TemplateResponse(request, template_name, context)


def marshall_zone_report(request, zone, event):
    """
    Function to generate a marshall report for a specific Zone and Event
    """
    current_fair = Fair.currentfairmgr.all().last()
    zone_data = Zone.objects.get(id=zone)
    event_data = Event.objects.get(id=event)

    # Precompute the first and second events for the current fair
    event_query = Event.currenteventfiltermgr.annotate_event_sequence()

    # Get the first and second events
    first_event = event_query.first()
    second_event = event_query[1] if event_query.count() > 1 else None
    if event_query.count() <= 1:
        second_event = None

    # Subquery to fetch the `is_skipped` value from SiteHistory
    site_history_subquery = SiteHistory.objects.filter(
        stallholder=OuterRef('stallholder'),
        site=OuterRef('site_allocation__event_site__site'),
        year=str(current_fair.fair_year)
    ).values('is_skipped')[:1]


    # Base queryset for StallRegistration
    site_information = StallRegistration.registrationcurrentallmgr.filter(
        site_allocation__event_site__event__fair=current_fair,
        site_allocation__event_site__site__zone=zone,
    ).select_related('stallholder').annotate(
        allocated_site_name=F('site_allocation__event_site__site__site_name'),
        allocated_powerbox_name=F('site_allocation__event_site__site__powerbox__power_box_name'),
        allocated_powerbox_description=F('site_allocation__event_site__site__powerbox__power_box_description'),
        allocated_site_size=F('site_allocation__event_site__site__site_size__item_name'),
        site_has_power=F('site_allocation__event_site__site__has_power'),
        allocated_site_note=F('site_allocation__event_site__site__site_note'),
        allocated_eventsite_note=F('site_allocation__event_site__notes'),
        is_skipped=Coalesce(Subquery(site_history_subquery, output_field=BooleanField()), Value(False))
    )

    # Add event attendance flags, casting BooleanField to IntegerField
    if first_event:
        site_information = site_information.annotate(
            attending_event_1=Case(
                When(site_allocation__event_site__event=first_event, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        )

    if second_event:
        site_information = site_information.annotate(
            attending_event_2=Case(
                When(site_allocation__event_site__event=second_event, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        )
    else:
        # If there's no second event, avoid referencing it in aggregation
        site_information = site_information.annotate(
            attending_event_2=Value(0, output_field=IntegerField())
            )

    # Aggregate by site to ensure each site is listed only once
    site_information = site_information.values(
        'id',  # StallRegistration ID
        'manager_vehicle_registration',
        'vehicle_on_site',
        'power_required',
        'stall_manager_name',
        'allocated_site_name',
        'allocated_site_size',
        'allocated_powerbox_name',
        'allocated_powerbox_description',
        'site_has_power',
        'stall_description',
        'stallholder__phone',
        'stallholder__first_name',
        'stallholder__last_name',
        'is_skipped'
    ).annotate(
        # Consolidate notes into a single string
        allocated_site_note=StringAgg('site_allocation__event_site__site__site_note', delimiter=', ', distinct=True),
        allocated_eventsite_note=StringAgg('site_allocation__event_site__notes', delimiter=', ', distinct=True),
        attending_event_1=Max('attending_event_1'),
        attending_event_2=Max('attending_event_2'),
    ).order_by(
        'allocated_site_name'
    )

    context ={
        'site_information': site_information,
        'zone_data': zone_data,
        'event_data': event_data
    }

    filename= f'marshalls_{event_data.event_name}_report.pdf'

    html_template = get_template('marshallingsitelist.html').render(context)
    pdf_file = HTML(string=html_template, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="{filename}"'
    return response

def trestle_distribution_report(request, event):
    """
    Function to generate a trestle distribution report for a specific Event
    """
    current_fair = Fair.currentfairmgr.all().last()
    event_data = Event.objects.get(id=event)
    # Queryset for StallRegistration
    site_information = StallRegistration.registrationcurrentallmgr.filter(
        site_allocation__event_site__event__fair=current_fair,
        site_allocation__event_site__event=event,
        trestle_required=True,
        booking_status='Booked'
    ).select_related('stallholder').annotate(
        allocated_site_name=F('site_allocation__event_site__site__site_name'),
        allocated_site_trestle_source=F('site_allocation__event_site__site__zone__trestle_source')
    ).values(
        'allocated_site_trestle_source',
        'stallholder__first_name',
        'stallholder__last_name',
        'allocated_site_name',
        'trestle_quantity',
    ).order_by(
        'allocated_site_trestle_source'
    )

    context ={
        'site_information': site_information,
        'event_data': event_data
    }

    filename= f'trestle_distribution_{event_data.event_name}_report.pdf'

    html_template = get_template('trestlelist.html').render(context)
    pdf_file = HTML(string=html_template, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="{filename}"'
    return response

def fair_passpack_generator(request, stallregistration):
    """
    Function to generate a fair passpack for a specific stallregistration
    """
    report_date = datetime.datetime.now()
    current_fair = Fair.currentfairmgr.all().last()

    # Queryset for StallRegistration
    stall_registration = StallRegistration.objects.filter( id=stallregistration).first()

    zone_map_subquery = ZoneMap.objects.filter(
        zone=OuterRef('site_allocation__event_site__site__zone'),
        year=str(report_date.year)
    ).values('map_pdf')[:1]

    # Query to fetch PowerBox description
    power_box_subquery = PowerBox.objects.filter(
        site_powerbox__zone=OuterRef('site_allocation__event_site__site__zone')
    ).values('power_box_description')[:1]

    # Subquery to fetch a single trestle source value
    trestle_source_subquery = StallRegistration.objects.filter(
        id=OuterRef('id')
    ).values('site_allocation__event_site__site__zone__trestle_source')[:1]

    site_list = StallRegistration.registrationcurrentmgr.filter(
        id=stallregistration
    ).select_related('stallholder').annotate(
        allocated_site_name=F('site_allocation__event_site__site__site_name'),
        allocated_site_size=F('site_allocation__event_site__site__site_size__site_size'),
        allocated_event_name=F('site_allocation__event_site__event__event_name'),
        allocated_site_location=F('site_allocation__event_site__site__zone__zone_name'),
        zone_map_path=Subquery(zone_map_subquery),
        powerbox_description=Subquery(power_box_subquery),
        trestle_source=Subquery(trestle_source_subquery),
    ).values(
        'allocated_site_size',
        'allocated_site_name',
        'allocated_event_name',
        'allocated_site_location',
        'zone_map_path',
        'powerbox_description',
        'trestle_source',
    ).order_by(
        'allocated_event_name'
    )

    profile = get_object_or_404(Profile, user=stall_registration.stallholder)

    context ={
        'report_date': report_date,
        'stall_registration': stall_registration,
        'site_list': site_list,
        'profile': profile,
        'current_fair': current_fair,
        'powerbox_description': next(
            (site['powerbox_description'] for site in site_list if site['powerbox_description']), None
        ) if stall_registration.power_required else None,
        'trestle_source': next(
        (site['trestle_source'] for site in site_list if site['trestle_source']), None
        ),
    }

    # Construct URLs for the zone maps
    current_site = get_current_site(request)
    domain = current_site.domain
    protocol = 'https' if request.is_secure() else 'http'

    for site in site_list:
        if site['zone_map_path']:
            site['zone_map_url'] = f'{protocol}://{domain}/media/{site["zone_map_path"]}'
        else:
            site['zone_map_url'] = None

    filename= f'fair_passpack_for_stallregid{stallregistration}.pdf'

    html_template = get_template('passpack.html').render(context)
    pdf_file = HTML(string=html_template, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response

def food_stall_site_report(request, event):
    """
    Report to produce a listing of the food stallholders and their site for a specific fair event.
    Required the event to be selected
    """
    current_fair = Fair.currentfairmgr.all().last()
    event_data = Event.objects.get(id=event)
    # Queryset for StallRegistration
    site_information = StallRegistration.registrationcurrentallmgr.filter(
        site_allocation__event_site__event__fair=current_fair,
        site_allocation__event_site__event=event,
        selling_food=True,
        booking_status='Booked'
    ).select_related('stallholder').annotate(
        allocated_zone_name=F('site_allocation__event_site__site__zone__zone_name'),
        allocated_site_name=F('site_allocation__event_site__site__site_name'),
    ).values(
        'stallholder__first_name',
        'stallholder__last_name',
        'allocated_zone_name',
        'allocated_site_name',
        'stall_description',
        'products_on_site',
    ).order_by(
        'allocated_site_name'
    )

    context ={
        'site_information': site_information,
        'event_data': event_data
    }

    filename= f'food_stall_{event_data.event_name}_report.pdf'

    html_template = get_template('foodstalllist.html').render(context)
    pdf_file = HTML(string=html_template, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="{filename}"'
    return response

def stall_search_report(request, event):
    """
    Report to produce a listing of the stallholders and their site for a specific fair event.
    The purpose of the report is for finding sites at the Fair Information Kiosk
    Required the event to be selected
    """
    current_fair = Fair.currentfairmgr.all().last()
    event_data = Event.objects.get(id=event)
    # Queryset for StallRegistration
    site_information = StallRegistration.registrationcurrentallmgr.filter(
        site_allocation__event_site__event__fair=current_fair,
        site_allocation__event_site__event=event,
        booking_status='Booked'
    ).select_related('stallholder__profile', 'stall_category').annotate(
        allocated_zone_name=F('site_allocation__event_site__site__zone__zone_name'),
        allocated_site_name=F('site_allocation__event_site__site__site_name'),
        stallholder_org_name=F('stallholder__profile__org_name'),
        stall_category_name=F('stall_category__category_name')
    ).values(
        'stallholder__first_name',
        'stallholder__last_name',
        'stallholder__phone',
        'stallholder_org_name',
        'allocated_zone_name',
        'allocated_site_name',
        'stall_category_name',
        'stall_description',
        'products_on_site',
    ).order_by(
        'stall_category_name'
    )

    context ={
        'site_information': site_information,
        'event_data': event_data
    }

    filename= f'stall_search_{event_data.event_name}_report.pdf'

    html_template = get_template('searchstalllist.html').render(context)
    pdf_file = HTML(string=html_template, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="{filename}"'
    return response




def stall_search_csv_report(request, event):
    """
    Export the stall search data as a CSV report.
    """
    current_fair = Fair.currentfairmgr.all().last()
    event_data = Event.objects.get(id=event)

    # Queryset for StallRegistration
    site_information = StallRegistration.registrationcurrentallmgr.filter(
        site_allocation__event_site__event__fair=current_fair,
        site_allocation__event_site__event=event,
        booking_status='Booked'
    ).select_related(
        'stallholder__profile', 'stall_category'
    ).annotate(
        stall_category_name=F('stall_category__category_name'),
        stallholder_name=F('stallholder__first_name'),
        stallholder_last_name=F('stallholder__last_name'),
        organisation_name=F('stallholder__profile__org_name'),
        phone=F('stallholder__profile__phone2'),
        site_name=F('site_allocation__event_site__site__site_name'),
    ).values(
        'stall_category_name',
        'stallholder_name',
        'stallholder_last_name',
        'organisation_name',
        'phone',
        'site_name',
        'stall_description',
        'products_on_site',
    )

    # Create the HTTP response with a CSV file
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="stall_search_{event_data.event_name}_report.csv"'

    writer = csv.writer(response)
    # Write the header
    writer.writerow([
        'Stall Category', 'Stallholder', 'Organisation',
        'Phone', 'Site', 'Product Description', 'Products on Site'
    ])

    # Write data rows
    for entry in site_information:
        writer.writerow([
            entry['stall_category_name'],
            f"{entry['stallholder_name']} {entry['stallholder_last_name']}",
            entry['organisation_name'],
            entry['phone'],
            entry['site_name'],
            entry['stall_description'],
            entry['products_on_site'],
        ])

    return response


