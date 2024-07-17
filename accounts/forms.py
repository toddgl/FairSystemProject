# accounts/forms.py
from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from allauth.account.forms import SignupForm
from django.forms import TextInput, EmailInput, ModelForm
from.models import CustomUser, Profile
from django.core.validators import RegexValidator


class CustomSignupForm(SignupForm):

    first_name = forms.CharField(
        label="First Name",
        widget=forms.TextInput(attrs={
            'class': "form-control",
            'style': 'max-width: 300px;',
            'placeholder': 'First Name'
        }),
        )

    last_name = forms.CharField(
        label="Surname",
        widget=forms.TextInput(attrs={
            'class': "form-control",
            'style': 'max-width: 300px;',
            'placeholder': 'Surname'
        }),
        )

    phone = forms.CharField(
        max_length=13,
        validators=[RegexValidator('^\([0]\d{1}\)(\d{7}$)|(^\([0][2]\d{1}\))(\d{6,8}$)|([0][5,8,9][0][0,8])([\s-]?)(\d{5,8})$', message="Enter a valid NewZealand Phone number")],
        label="Phone Number",
        widget=forms.TextInput(attrs={
            'class': "form-control",
            'style': 'max-width: 300px;',
            'placeholder': '(xx) or (xxx)1234567 or 0800 123456'
        }),
        )
    # Add additional profile fields
    address1 = forms.CharField(
        label="Address Line 1",
        required=False,
        widget=forms.TextInput(attrs={
            'class': "form-control",
            'style': 'max-width: 300px;',
            'placeholder': 'Address Line 1'
        }),
    )

    address2 = forms.CharField(
        label="Address Line 2",
        required=False,
        widget=forms.TextInput(attrs={
            'class': "form-control",
            'style': 'max-width: 300px;',
            'placeholder': 'Address Line 2'
        }),
    )

    town = forms.CharField(
        label="Town or City",
        widget=forms.TextInput(attrs={
            'class': "form-control",
            'style': 'max-width: 300px;',
            'placeholder': 'Town or City'
        }),
    )

    postcode = forms.CharField(
        label="Postcode",
        required=False,
        widget=forms.TextInput(attrs={
            'class': "form-control",
            'style': 'max-width: 300px;',
            'placeholder': 'Postcode'
        }),
    )

    phone2 = forms.CharField(
        max_length=13,
        required=False,
        validators=[RegexValidator(r'^\([0]\d{1}\)(\d{7}$)|(^\([0][2]\d{1}\))(\d{6,8}$)|([0][5,8,9][0][0,8])([\s-]?)(\d{5,8})$', message="Enter a valid New Zealand Phone number")],
        label="Alternative Phone Number",
        widget=forms.TextInput(attrs={
            'class': "form-control",
            'style': 'max-width: 300px;',
            'placeholder': '(xx) or (xxx)1234567 or 0800 123456'
        }),
    )

    org_name = forms.CharField(
        label="Organisation Name",
        required=False,
        widget=forms.TextInput(attrs={
            'class': "form-control",
            'style': 'max-width: 300px;',
            'placeholder': 'Organisation Name'
        }),
    )

    class Meta:
        model = CustomUser

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        user.save()

        # Add user to the stallholder group
        stallholder_group = Group.objects.get(name='stallholder')
        user.groups.add(stallholder_group)

        # Update the existing profile with additional profile details
        profile = user.profile
        profile.address1 = self.cleaned_data['address1']
        profile.address2 = self.cleaned_data['address2']
        profile.town = self.cleaned_data['town']
        profile.postcode = self.cleaned_data['postcode']
        profile.phone2 = self.cleaned_data['phone2']  # This can now be blank
        profile.org_name = self.cleaned_data['org_name']
        profile.save()

        return user

class CustomUserCreationForm(UserCreationForm):

    phone = forms.CharField(
        max_length=13,
        validators=[RegexValidator('^\([0]\d{1}\)(\d{7}$)|(^\([0][2]\d{1}\))(\d{6,8}$)|([0][5,8,9][0][0,8])([\s-]?)(\d{5,8})$', message="Enter a valid NewZealand Phone number")],
        label="Phone Number",
        widget=forms.TextInput(attrs={
            'class': "form-control",
            'style': 'max-width: 300px;',
            'placeholder': '(xx) or (xxx)1234567 or 0800 123456'
        }),
        )

    class Meta:
        model = CustomUser
        fields = UserCreationForm.Meta.fields + \
            ('first_name', 'last_name', 'phone',)
        widgets = {
            'username': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Name'
                }),
            'email': EmailInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Email'
                }),
            'first_name': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'First Name'
                }),
            'last_name': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Surname'
                }),
        }


class CustomUserChangeForm(ModelForm):

    phone = forms.CharField(
        max_length=13,
        validators=[RegexValidator('^\([0]\d{1}\)(\d{7}$)|(^\([0][2]\d{1}\))(\d{6,8}$)|([0][5,8,9][0][0,8])([\s-]?)(\d{5,8})$', message="Enter a valid NewZealand Phone number")],
        label="Phone Number",
        widget=forms.TextInput(attrs={
            'class': "form-control",
            'style': 'max-width: 300px;',
            'placeholder': '(xx) or (xxx)1234567 or 0800 123456'
        }),
        )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone')
        widgets = {
            'username': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Name'
                }),
            'email': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Email'
                }),

            'first_name': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'First Name'
            }),
            'last_name': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Surname'
            }),
        }


class ProfileForm(ModelForm):

    phone2 = forms.CharField(
        max_length=13,
        required=False,
        validators=[RegexValidator('^\([0]\d{1}\)(\d{7}$)|(^\([0][2]\d{1}\))(\d{6,8}$)|([0][5,8,9][0][0,8])([\s-]?)(\d{5,8})$', message="Enter a valid NewZealand Phone number")],
        label="Alternative Phone Number",
        widget=forms.TextInput(attrs={
            'class': "form-control",
            'style': 'max-width: 300px;',
            'placeholder': '(xx) or (xxx)1234567 or 0800 123456'
        }),
    )
    class Meta:
        model = Profile
        fields = ('address1', 'address2', 'town', 'postcode', 'phone2', 'org_name',)
        widgets = {
            'address1': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Address Line One'
                }),
            'address2': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Address Line 2'
            }),
            'town': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Town or City'
            }),
            'postcode': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Postcode'
            }),
            'org_name': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Organisation Name'
            }),
        }
