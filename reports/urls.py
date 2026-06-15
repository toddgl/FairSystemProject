# reports/urls.py

from django.urls import path

from reports.views import (
    site_allocation_numbers_report,
    marshall_zone_report,
    reports_listview,
    fair_passpack_generator,
    stall_validation_report,
    site_allocation_audit_report,
    export_site_allocation_audit_pdf,
    export_site_allocation_audit_csv,
)


app_name = 'reports'  # This is the namespace, so you can reverse urls with payment:*

urlpatterns = [
    path('reports/zonelist/', marshall_zone_report, name='marshal-zone-list'),
    path('reports/dashboard/',reports_listview, name='report-dashboard' ),
    path('reports/passpack/<int:stallregistration>', fair_passpack_generator, name='stallholder-passpack'),
    path('reports/unallocated-stalls/', stall_validation_report, name='unallocated_stalls_report'),
    path('reports/allocated-site-numbers/', site_allocation_numbers_report, name='allocated-site-numbers-report'),
    path('reports/site-allocations-review-list/', site_allocation_audit_report, name='site-allocation-audit-report'),
    path('reports/site-allocations-audit-pdf/', export_site_allocation_audit_pdf, name='site-allocation-audit-pdf'),
    path('reports/site-allocations-audit-csv/', export_site_allocation_audit_csv, name='site-allocation-audit-csv'),
]
