# registration/forms.py

from django import forms
from django.forms import (
    Form,
    ModelForm,
    ChoiceField,
    ModelChoiceField,
    ModelMultipleChoiceField,
    IntegerField,
    Textarea,
    TextInput,
    FileInput,
    CheckboxInput,
    NumberInput,
    RadioSelect,
    Select,
    SelectMultiple,
    SelectDateWidget
)
from registration.models import (
    FoodPrepEquipment,
    FoodSaleType,
    StallCategory,
    StallRegistration,
)


class FoodPrepEquipmentCreationForm(ModelForm):
    """
    Form for creating new food preparation equipment
    """

    class Meta:
        model = FoodPrepEquipment
        fields = ['equipment_name', 'power_load_minimum', 'power_load_maximum', 'power_load_factor', ]
        widgets = {
            'equipment_name': TextInput(attrs={
                'class': "form-control",
                'size': '300',
                'placeholder': 'Equipment name'
            }),
            'power_load_minimum': NumberInput(attrs={
                'class': 'form-control',
                'style': 'max-width: 200px;',
                'placeholder': 'Watts'
            }),
            'power_load_maximum': NumberInput(attrs={
                'class': 'form-control',
                'style': 'max-width: 200px;',
                'placeholder': 'Watts'
            }),
            'power_load_factor': NumberInput(attrs={
                'class': 'form-control',
                'style': 'max-width: 200px;',
                'placeholder': 'Percent'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.created_by = kwargs.pop('created_by', None)
        super(FoodPrepEquipmentCreationForm, self).__init__(*args, **kwargs)

    def clean_power_box_name(self):
        equipment_name = self.cleaned_data['equipment_name']
        if FoodPrepEquipment.objects.filter(equipment_name=equipment_name).exists():
            raise forms.ValidationError("This Food Preparation Equipment has already been created.")
        return equipment_name


class FoodPrepEquipmentUpdateForm(ModelForm):
    """
    Form for updating Food Preparation Equipment Details
    """

    class Meta:
        model = FoodPrepEquipment
        fields = ['equipment_name', 'power_load_minimum', 'power_load_maximum', 'power_load_factor', ]
        widgets = {
            'equipment_name': TextInput(attrs={
                'class': "form-control",
                'size': '300',
                'placeholder': 'Equipment name'
            }),
            'power_load_minimum': NumberInput(attrs={
                'class': 'form-control',
                'style': 'max-width: 200px;',
                'placeholder': 'Watts'
            }),
            'power_load_maximum': NumberInput(attrs={
                'class': 'form-control',
                'style': 'max-width: 200px;',
                'placeholder': 'Watts'
            }),
            'power_load_factor': NumberInput(attrs={
                'class': 'form-control',
                'style': 'max-width: 200px;',
                'placeholder': 'Percent'
            }),
        }


class FoodSaleTypeCreationForm(ModelForm):
    """
    Form for creating new food sale type
    """

    class Meta:
        model = FoodSaleType
        fields = ['food_sale_type', 'is_active', ]
        widgets = {
            'food_sale_type': TextInput(attrs={
                'class': "form-control",
                'size': '400',
                'placeholder': 'Food Sale Type'
            }),
            'is_active': CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

    def __init__(self, *args, **kwargs):
        self.created_by = kwargs.pop('created_by', None)
        super(FoodSaleTypeCreationForm, self).__init__(*args, **kwargs)

    def clean_power_box_name(self):
        food_sale_type = self.cleaned_data['food_sale_type']
        if FoodSaleType.objects.filter(food_sale_type=food_sale_type).exists():
            raise forms.ValidationError("This Food Sale Type has already been created.")
        return food_sale_type


class FoodSaleTypeUpdateForm(ModelForm):
    """
    Form for updating food sale type details
    """

    class Meta:
        model = FoodSaleType
        fields = ['food_sale_type', 'is_active', ]
        widgets = {
            'food_sale_type': TextInput(attrs={
                'class': "form-control",
                'size': '400',
                'placeholder': 'Food Sale Type'
            }),
            'is_active': CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }


class StallCategoryCreationForm(ModelForm):
    """
    Form for creating new stall category
    """

    class Meta:
        model = StallCategory
        fields = ['category_name', 'is_active', ]
        widgets = {
            'category_name': TextInput(attrs={
                'class': "form-control",
                'size': '400',
                'placeholder': 'Stall Category Name'
            }),
            'is_active': CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

    def __init__(self, *args, **kwargs):
        self.created_by = kwargs.pop('created_by', None)
        super(StallCategoryCreationForm, self).__init__(*args, **kwargs)

    def clean_power_box_name(self):
        category_name = self.cleaned_data['category_name']
        if StallCategory.objects.filter(category_name=category_name).exists():
            raise forms.ValidationError("This  Stall Category has already been created.")
        return category_name


class StallCategoryUpdateForm(ModelForm):
    """
    Form for updating stall category details
    """

    class Meta:
        model = StallCategory
        fields = ['category_name', 'is_active', ]
        widgets = {
            'category_name': TextInput(attrs={
                'class': "form-control",
                'size': '400',
                'placeholder': 'Stall Category Name'
            }),
            'is_active': CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }


class StallRegistrationCreateUpdateForm(ModelForm):
    """
    Combined form for creating and updating Stall Registrations
    """

    class Meta:
        model = StallRegistration
        fields = [
                  'event_site',
                  'stall_manager_name',
                  'stall_category',
                  'stall_description',
                  'products_on_site',
                  'trestle_required',
                  'trestle_quantity',
                  'stall_shelter',
                  'power_required',
                  'event_power',
                  'total_charge',
                  'selling_food',
                  ]
        widgets = {
            'event_site': Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px;'
            }),
            'stall_manager_name': TextInput(attrs={
                'class': 'form-control',
                'style': 'max-width: 300px;'
            }),
            'stall_category': Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px;'
            }),
            'stall_description': TextInput(attrs={
                'class': 'form-control',
                'style': 'max-width: 300px;'
            }),
            'products_on_site': TextInput(attrs={
                'class': 'form-control',
                'style': 'max-width: 300px;'
            }),
            'trestle_required': CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'trestle_quantity': NumberInput(attrs={
                'class': "form_control",
                'style': 'max-width: 400px;',
                'placeholder': 'Number of Trestles',
                'label': 'Number of trestles required'
            }),
            'stall_shelter': TextInput(attrs={
                'class': 'form-control',
                'style': 'max-width: 300px;'
            }),
            'power_required': CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'event_power': Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px;'
            }),
            'total_charge': TextInput(attrs={
                'class': 'form-control',
                'style': 'max-width: 300px;',
                'readonly': 'readonly'
            }),
            'selling_food': CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
