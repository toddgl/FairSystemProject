# foodlicence/views.py

import io
import os
from django.utils.timezone import now
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import get_template, render_to_string
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse_lazy, reverse
from django.template.response import TemplateResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django_fsm import can_proceed
from weasyprint import HTML, CSS
from pypdf import PdfWriter, PdfReader
from pypdf.annotations import FreeText
from django.core.files.base import ContentFile
from django.db.models import Q
from accounts.models import (
    Profile
)
from registration.models import (
    StallRegistration,
    FoodRegistration
)
from payment.models import (
    PaymentHistory,
)
from .models import (
    FoodLicenceBatch,
    FoodLicence
)
from .forms import (
    FoodlicenceStatusFilterForm,
    FoodLicenceBatchUpUpdateForm
)

def generate_pdf(object, request):
    # Get the current site domain
    current_site = get_current_site(request)
    domain = current_site.domain
    protocol = 'https' if request.is_secure() else 'http'

    # Full URL for the certificate
    full_certificate_url = f'{protocol}://{domain}{object.food_registration.food_registration_certificate.url}'

    # Render a template to HTML
    stall_registration =StallRegistration.objects.get(id=object.food_registration.registration.id)
    stallholder_detail =  Profile.objects.get(user=stall_registration.stallholder)
    # Use render_to_string to render the template with context
    html_content = render_to_string('swdc_foodlicence.html', {
        'object': object,
        'stallholder_detail': stallholder_detail,
        'full_certificate_url': full_certificate_url
    })
    css_file = os.path.join(settings.STATIC_ROOT, 'css', 'licence.css')
    # Convert HTML to PDF
    pdf_file = HTML(string=html_content).write_pdf(stylesheets=[CSS(filename=css_file)])

    return pdf_file

def merge_pdfs(pdf_files):
    pdf_writer = PdfWriter()
    current_page_number = 1

    for pdf_file in pdf_files:
        pdf_reader = PdfReader(io.BytesIO(pdf_file))
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            pdf_writer.add_page(page)

            # Add page number (this part is theoretical; actual code may vary)
            '''
            annotation = FreeText(
                text=f"Page {current_page_number}",
                rect=(50, 550, 200, 650),
            )
            pdf_writer.add_annotation(
                page_num, annotation=annotation
            )
            current_page_number += 1
            '''
    output = io.BytesIO()
    pdf_writer.write(output)

    return output.getvalue()

def generate_combined_pdf(request):
    # Fetch selected objects
    selected_licences = FoodLicence.objects.filter(licence_status="Staged")  # Adjust filter as needed

    if not selected_licences.exists():
        return HttpResponse("No licences found.", content_type="text/plain")

    # Generate PDFs for each object
    pdf_files = [generate_pdf(obj, request) for obj in selected_licences]

    # Merge the PDFs
    combined_pdf = merge_pdfs(pdf_files)

    # Retrieve recipient email from settings
    recipient_email = getattr(settings, 'SWDC_FOOD_LICENCE_EMAIL_ADDRESS')

    # Create and populate FoodLicenceBatch instance
    food_licence_batch = FoodLicenceBatch(
        recipient_email=recipient_email,
        date_sent=now(),
        date_returned=None,
        date_closed=None,
        batch_count=len(selected_licences)
    )
    food_licence_batch.save()  # Save first to get the ID

    # Retrieve the batch ID
    batch_id = food_licence_batch.id

    # Get the current datetime
    current_datetime = now().strftime('%Y%m%d_%H%M%S')

    # Create the filename with batch ID and datetime
    filename = f'combined_{batch_id}_{current_datetime}.pdf'

    # Save the PDF to the instance
    food_licence_batch.pdf_file.save(filename, ContentFile(combined_pdf))
    food_licence_batch.save()

    # Update FoodLicence objects to reference the new batch
    selected_licences.update(food_licence_batch=food_licence_batch)

    # Mark all selected licences as Batched
    for foodlicence in selected_licences:
        if can_proceed(foodlicence.to_licence_status_batched):
            foodlicence.to_licence_status_batched()
            foodlicence.save()

    # Render email body
    email_body = render_to_string('email_template.html', {'batch': food_licence_batch})

    # Create and send email
    email = EmailMessage(
        subject='Martinborough Fair - Food Licence Batch Notification',
        body=email_body,
        from_email=settings.EMAIL_HOST_USER,
        to=[recipient_email],
    )

    # Specify that the content is HTML
    email.content_subtype = 'html' # This makes the email render as HTML

    # Attach PDF
    email.attach(filename, combined_pdf, 'application/pdf')

     # Try sending the email
    try:
        email.send()
    except Exception as e:
        return HttpResponse(f"Email sending failed: {str(e)}", content_type="text/plain")

    # Mark all selected licences as Submitted
    for foodlicence in selected_licences:
        if can_proceed(foodlicence.to_licence_status_submitted):
            foodlicence.to_licence_status_submitted()
            foodlicence.date_requested = now()
            foodlicence.save()

    # Return the combined PDF as a response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write(combined_pdf)

    return response

def mark_licence_as_staged(request, id):
    """
    Description: Called from foodlicence list to set the status of the food licence to staged ready to be included
    in SWDC Licence request combined pdf.
    """
    success_url = reverse_lazy('foodlicence:foodlicence-list')
    foodlicence = get_object_or_404(FoodLicence, pk=id)
    if not can_proceed(foodlicence.to_licence_status_staged):
        raise PermissionDenied
    foodlicence.to_licence_status_staged()
    foodlicence.save()
    return HttpResponseRedirect(success_url)

def mark_licence_as_batched(request, id):
    """
    Description: Called from create SWDC PDF function to set the status of the foodlicence to batched. This is a
    transient status prior to the email being sent to SWDC
    """
    success_url = reverse_lazy('foodlicence:foodlicence-list')
    foodlicence = get_object_or_404(FoodLicence, pk=id)
    if not can_proceed(foodlicence.to_booking_status_batched):
        raise PermissionDenied
    foodlicence.to_licence_status_batched()
    foodlicence.save()
    return HttpResponseRedirect(success_url)

def mark_licence_as_submitted(request, id):
    """
    Description: Called from create SWDC PDF function to set the status of the foodlicence to submitted. This is
    set once the email is successfully sent to the SWDC.  The requested date is also set for tracking purposes
    """
    success_url = reverse_lazy('foodlicence:foodlicence-list')
    foodlicence = get_object_or_404(FoodLicence, pk=id)
    if not can_proceed(foodlicence.to_booking_status_submitted):
        raise PermissionDenied
    foodlicence.to_licence_status_submitted()
    foodlicence.date_requested = now()
    foodlicence.save()
    return HttpResponseRedirect(success_url)

def mark_licence_as_approved(request, id):
    """
    Description: Called from foodlicence list to set the status of the foodlicence to approved and set the
    completed date
    """
    success_url = reverse_lazy('foodlicence:foodlicence-list')
    foodlicence = get_object_or_404(FoodLicence, pk=id)
    if not can_proceed(foodlicence.to_booking_status_approved):
        raise PermissionDenied
    foodlicence.to_licence_status_approved()
    foodlicence.date_completed = now()
    foodlicence.save()
    return HttpResponseRedirect(success_url)

def mark_licence_as_rejected(request, id):
    """
    Description: Called from foodlicence list to set the status of the foodlicence to rejected and set the
    completed date
    """
    success_url = reverse_lazy('foodlicence:foodlicence-list')
    foodlicence = get_object_or_404(FoodLicence, pk=id)
    if not can_proceed(foodlicence.to_booking_status_rejected):
        raise PermissionDenied
    foodlicence.to_licence_status_rejected()
    foodlicence.date_completed = now()
    foodlicence.save()
    return HttpResponseRedirect(success_url)

def foodlicence_listview(request):
    """
    Description: view for displaying food licences in a table with filter based on licence_status and providing
    functionality to change the status from Created to Batched, Submitted to Completed and Submitted to Rejected.
    Plus the ability to drillddown to see the respective StallRegistration / Food Registration
    """
    foodlicence_status_filter_dict = {}
    template_name = 'foodlicence_list.html'
    filterform = FoodlicenceStatusFilterForm(request.POST or None)
    licence_status=request.GET.get('licence_status', '')
    if licence_status:
        foodlicence_list = FoodLicence.foodlicencecurrentmgr.filter(licence_status=licence_status).all().select_related('food_licence_batch')
        alert_message = 'There are no Food Licences of status ' + str(licence_status) + ' created yet'
    else:
        foodlicence_list = FoodLicence.foodlicencecurrentmgr.all().select_related('food_licence_batch')
        alert_message = 'There are no food licences created yet.'

    if request.htmx:
        form_purpose = filterform.data.get('form_purpose', '')
        if form_purpose == 'filter':
            if filterform.is_valid():
                foodlicence_status = filterform.cleaned_data['licence_status']
                attr_foodlicence_status = 'licence_status'
                if foodlicence_status:
                    alert_message = 'There are no food licences for status ' + str(foodlicence_status)
                    foodlicence_status_filter_dict = { attr_foodlicence_status: foodlicence_status }
                else:
                    alert_message = 'There are no food licences created yet'
                    foodlicence_status_filter_dict = {}
        else:
            # Handle pagination
            # The foodlicence_status_filter _dict is retained from the filter selection which ensures that the correct
            # data is applied
            # to subsequent pages
            pass
        foodlicence_list = FoodLicence.foodlicencecurrentmgr.filter( **foodlicence_status_filter_dict).all().select_related('food_licence_batch')
        template_name = 'foodlicence_list_partial.html'
        return TemplateResponse(request, template_name, {
            'food_licence_list': foodlicence_list,
            'alert_mgr': alert_message,
        })
    else:
        return TemplateResponse(request, template_name, {
            'filterform': filterform,
            'food_licence_list': foodlicence_list,
            'alert_mgr': alert_message,
        })

def foodlicence_dashboard_view(request):
    """
    Populate the Foodlicence Dashboard with counts of the various food licences statuses
    """
    total_counts = FoodLicence.foodlicencecurrentmgr.count()
    created_counts = FoodLicence.foodlicencecurrentmgr.get_created().count()
    batched_counts = FoodLicence.foodlicencecurrentmgr.get_batched().count()
    submitted_counts = FoodLicence.foodlicencecurrentmgr.get_submitted().count()
    rejected_counts = FoodLicence.foodlicencecurrentmgr.get_rejected().count()
    approved_counts = FoodLicence.foodlicencecurrentmgr.get_approved().count()

    return TemplateResponse(request, 'dashboard_foodlicences.html', {
        'total_counts': total_counts,
        'created_counts': created_counts,
        'batched_counts': batched_counts,
        'submitted_counts': submitted_counts,
        'rejected_counts': rejected_counts,
        'approved_counts': approved_counts
    })

def foodlicence_batch_listview(request):
    """
    Description: to view and set completed date for the FoodLicenceBatched instannces including the ability to view
    the generated PDF's
    """
    template_name = 'foodlicence_batch_list.html'
    foodlicence_batch_list = FoodLicenceBatch.foodlicencebatchcurrentmgr.all()
    alert_message = 'There are no food licences batches created yet.'

    # Process form submission if request method is POST
    if request.method == 'POST':
        # Get the batch ID from the POST data
        batch_id = request.POST.get('batch_id')
        foodlicence_batch = get_object_or_404(FoodLicenceBatch, id=batch_id)

        # Bind form data to the form
        foodlicencebatchupdateform = FoodLicenceBatchUpUpdateForm(request.POST, instance=foodlicence_batch)

        # Check if form is valid and save the changes
        if foodlicencebatchupdateform.is_valid():
            foodlicencebatchupdateform.save()
            return redirect(request.META.get('HTTP_REFERER'))

    else:
        # If not POST, initialize an empty form
        foodlicencebatchupdateform = FoodLicenceBatchUpUpdateForm()

    return TemplateResponse(request, template_name, {
        'food_licence_batch_list': foodlicence_batch_list,
        'form': foodlicencebatchupdateform,
        'alert_mgr': alert_message,
    })

def create_food_licence_from_stallregistration(request, stallregistration_id):
    success_url = reverse_lazy('foodlicence:foodlicence-list')
    # Get the FoodRegistration instance associated with the StallRegistration ID
    food_registration = get_object_or_404(FoodRegistration, registration_id=stallregistration_id)

    # Check to ensure that the StallRegistration is either "Complete" "Reconciled" or "Credit" and it has a foodregistration
    ready_for_foodlicence =StallRegistration.registrationcurrentmgr.filter(id=stallregistration_id,
        food_registration__isnull=False
    ).filter(
        Q(invoice__payment_history__payment_status__in=[
            PaymentHistory.COMPLETED,
            PaymentHistory.RECONCILED,
            PaymentHistory.CREDIT
        ])
    )

    if ready_for_foodlicence:
        # Create the FoodLicence instance with status "Created"
        food_licence = FoodLicence.objects.create(
            food_registration=food_registration,
            licence_status=FoodLicence.CREATED
        )

    # Redirect to the calling view
    return HttpResponseRedirect(success_url)

def create_food_licence_if_eligible(request):
    success_url = reverse_lazy('foodlicence:foodlicence-list')
    # Step 1: Find stall registrations with completed payments
    eligible_stall_registrations = StallRegistration.registrationcurrentmgr.filter(
        invoice__payment_history__payment_status=PaymentHistory.COMPLETED,
        food_registration__isnull=False  # Ensures that a FoodRegistration exists
    ).distinct()

    # Step 2: Filter out stall registrations that already have a FoodLicence created
    eligible_stall_registrations = eligible_stall_registrations.exclude(
        food_registration__food_licence__isnull=False
    )

    # Step 3: If eligible stall registrations exist, cycle through and create the Foodlicences
    if eligible_stall_registrations.exists():
        for stall_registration in eligible_stall_registrations:
            food_registration = stall_registration.food_registration

            # Create the FoodLicence instance
            food_licence = FoodLicence.objects.create(
                food_registration=food_registration,
                licence_status=FoodLicence.CREATED
            )

        # Redirect to the Foodlicence list view page
        return HttpResponseRedirect(success_url)
    else:
        # Redirect to the Foodlicence list view page
        return HttpResponseRedirect(success_url)
