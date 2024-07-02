# foodlicence/views.py

import io
from django.core.mail import EmailMessage
from django.http import HttpResponse
import datetime
from django.conf import settings
from django.template.loader import get_template, render_to_string
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse_lazy, reverse
from django.template.response import TemplateResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django_fsm import can_proceed
from weasyprint import HTML
from pypdf import PdfWriter, PdfReader
from django.core.files.base import ContentFile
from .models import (
    FoodLicenceBatch,
    FoodLicence
)
from .forms import (
    FoodlicenceStatusFilterForm
)

def generate_pdf(object):
    # Render a template to HTML
    html_template = get_template('swdc_foodlicence.html', {'object': object})

    # Convert HTML to PDF
    pdf_file = HTML(string=html_template).write_pdf()

    return pdf_file

def merge_pdfs(pdf_files):
    pdf_writer = PdfWriter()

    for pdf_file in pdf_files:
        pdf_reader = PdfReader(io.BytesIO(pdf_file))
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            pdf_writer.add_page(page)

    output = io.BytesIO()
    pdf_writer.write(output)

    return output.getvalue()

def generate_combined_pdf(request):
    # Fetch selected objects

    selected_licences = FoodLicence.objects.filter(licence_status=FoodLicence.CREATED)  # Adjust filter as needed

    if not selected_licences.exists():
        return HttpResponse("No licences found.", content_type="text/plain")

    # Generate PDFs for each object
    pdf_files = [generate_pdf(obj) for obj in selected_licences]

    # Merge the PDFs
    combined_pdf = merge_pdfs(pdf_files)

    # Retrieve recipient email from settings
    recipient_email = getattr(settings, 'SWDC_FOOD_LICENCE_EMAIL_ADDRESS')

    # Create and populate FoodLicenceBatch instance
    food_licence_batch = FoodLicenceBatch(
        recipient_email=recipient_email,
        date_sent=datetime.datetime.now(),
        date_returned=None,
        date_closed=None,
        batch_count=len(selected_licences)
    )

    # Save the PDF to the instance
    food_licence_batch.pdf_file.save('combined.pdf', ContentFile(combined_pdf))
    food_licence_batch.save()

    # Update FoodLicence objects to reference the new batch
    selected_licences.update(food_licence_batch=food_licence_batch)

    # Render email body
    email_body = render_to_string('email_template.html', {'batch': food_licence_batch})

    # Create and send email
    email = EmailMessage(
        subject='Martinborough Fair - Food Licence Batch Notification',
        body=email_body,
        from_email=settings.EMAIL_HOST_USER,
        to=[recipient_email],
    )

    # Attach PDF
    email.attach('combined.pdf', combined_pdf, 'application/pdf')

    # Send email
    email.send()

    # Return the combined PDF as a response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="combined.pdf"'
    response.write(combined_pdf)

    return response

def add_licence_to_batch(request, id):
    """
    Description: Called from foodlicence list to set the status of teh food licence to batched ready to be included
    in SWDC Licence request combined pdf.
    """
    success_url = reverse_lazy('foodlicence:foodlicence-list')
    foodlicence = get_object_or_404(FoodLicence, pk=id)
    if not can_proceed(foodlicence.to_booking_status_submitted):
        raise PermissionDenied
    foodlicence.to_licence_status_batched()
    return HttpResponseRedirect(success_url)

def foodlicence_listview(request):
    """
    Description: view for displaying food licences in a table with filter based on licence_status and providing
    functionality to change the status from Created to Batched, Submitted to Completed and Submitted to Rejected.
    Plus the ability to drillddown to see the respective StallRegistration / Food Registration
    """
    global foodlicence_status_filter_dict
    template_name = 'foodlicence_list.html'
    filterform = FoodlicenceStatusFilterForm(request.POST or None)
    foodlicence_list = FoodLicence.foodlicencecurrentmgr.all()
    alert_message = 'There are no food licences created yet.'
    if request.htmx:
        form_purpose = filterform.data.get('form_purpose', '')
        if form_purpose == 'filter':
            if filterform.is_valid():
                foodlicence_status = filterform.cleaned_data['licence_status']
                attr_foodlicence_status = 'foodlicence_status'
                if foodlicence_status:
                    alert_message = 'There are no food licences for status ' + str(foodlicence_status)
                    foodlicence_status_filter_dict = {
                        attr_foodlicence_status: foodlicence_status,
                    }
            else:
                alert_message = 'There are no food licences created yet'
                foodlicence_status_filter_dict = {}
        else:
            # Handle pagination
            # The stallregistration_filter _dict is retained from the filter selection which ensures that the correct
            # data is applied
            # to subsequent pages
            pass
        foodlicence_list = FoodLicence.foodlicencecurrentmgr.filter( **foodlicence_status_filter_dict).all()
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







