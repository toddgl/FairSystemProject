# faq/admin.py

from django.contrib import admin
from .models import(
    FAQCategory,
    FAQ,
)

# Register your models here.
myModels = [FAQCategory, FAQ]
# iterable list
admin.site.register(myModels)
