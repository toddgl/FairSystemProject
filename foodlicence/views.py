# foodlicence/views.py

import io
from django.http import HttpResponse
import datetime
from django.conf import settings
from django.template.loader import get_template
from weasyprint import HTML
from pypdf import PdfWriter, PdfReader
from django.core.files.base import ContentFile
from .models import (
    FoodLicenceBatch,
    FoodLicence
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

    # Return the combined PDF as a response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="combined.pdf"'
    response.write(combined_pdf)

    return response