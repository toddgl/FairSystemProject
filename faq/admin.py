# faq/admin.py

from django.contrib import admin
from .models import(
    FAQ,
)

# Register your models here.
myModels = [FAQ]
# iterable list
admin.site.register(myModels)
