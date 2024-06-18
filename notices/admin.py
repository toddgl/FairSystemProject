
# notice/admin.py
from django.contrib import admin
from .models import (
    Notice
)
# Register your models here.
myModels = [ Notice ]
# iterable list
admin.site.register(myModels)
