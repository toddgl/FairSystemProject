# foodlicence/admin.py
from django.contrib import admin
from .models import (
    FoodLicence,
    FoodLicenceBatch,
)
class FoodLicenceAdmin(admin.ModelAdmin):
    list_display = ('id', 'food_registration', 'licence_status', 'date_requested', 'date_completed', 'food_licence_batch')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('food_licence_batch')

class FoodLicenceBatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient_email', 'date_created', 'date_sent', 'date_returned', 'date_closed', 'batch_count')

admin.site.register(FoodLicence, FoodLicenceAdmin)
admin.site.register(FoodLicenceBatch, FoodLicenceBatchAdmin)

