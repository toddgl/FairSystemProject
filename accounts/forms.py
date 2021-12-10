# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from allauth.account.forms import SignupForm
from django.forms import TextInput, EmailInput, ModelForm
from.models import CustomUser, Profile


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
        label="Phone Number",
        widget=forms.TextInput(attrs={
            'class': "form-control",
            'style': 'max-width: 300px;',
            'placeholder': 'Phone Number'
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

            return user


class CustomUserCreationForm(UserCreationForm):

    phone = forms.CharField(
        label="Phone Number",
        widget=forms.TextInput(attrs={
            'class': "form-control",
            'style': 'max-width: 300px;',
            'placeholder': 'Phone Number'
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
        label="Phone Number",
        widget=forms.TextInput(attrs={
            'class': "form-control",
            'style': 'max-width: 300px;',
            'placeholder': 'Phone Number'
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
            'phone': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Contact Phone Number'
            }),
        }


class ProfileChangeForm(ModelForm):

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
            'phone2': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Alternative Phone Number'
            }),
            'org_name': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Organisation Name'
            }),
        }
