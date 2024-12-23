# reports/urls.py

from django.urls import path

from reports.views import (
    marshall_zone_report,
    reports_listview,
)


app_name = 'reports'  # This is the namespace, so you can reverse urls with payment:*

urlpatterns = [
    path('reports/zonelist/', marshall_zone_report, name='marshal-zone-list'),
    path('reports/dashboard/',reports_listview, name='report-dashboard' )
]
