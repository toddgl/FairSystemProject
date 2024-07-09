# foodlicence/admin.py
from django.contrib import admin
from .models import (
    FoodLicence
)

class FoodLicenceAdmin(admin.ModelAdmin):
    list_display = ('id', 'food_registration', 'licence_status', 'date_requested', 'date_completed', 'food_licence_batch')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('food_licence_batch')

admin.site.register(FoodLicence, FoodLicenceAdmin)
