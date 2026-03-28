# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Profile

# Register your models here.


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserChangeForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'username', 'first_name', 'last_name')

    # Explicitly define searchfields to avoid MRO issues in Python 3.14
    search_fields = ('email', 'usename', 'first_name', 'last_name')
    ordering = ('email',)

    fieldsets = (
        # *UserAdmin.fieldsets,  # original form fieldsets, expanded
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_supervisor', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Custom Fields',
            {
                'fields': (
                    'reference_id',
                    'role',
                    'phone',
                ),
            }),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Profile)
