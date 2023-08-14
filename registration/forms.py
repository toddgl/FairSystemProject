# registration/forms.py

from django import forms
from django.core.exceptions import ValidationError
from django.forms import (
    BooleanField,
    ChoiceField,
    Form,
    HiddenInput,
    ModelForm,
    ModelChoiceField,
    Textarea,
    TextInput,
    FileInput,
    CheckboxInput,
    NumberInput,
    DateInput,
    RadioSelect,
    Select,
)
from fairs.models import (
    Fair,
    InventoryItem
)
from registration.models import (
    FoodPrepEquipment,
    FoodSaleType,
    StallCategory,
    StallRegistration,
    FoodRegistration,
    FoodPrepEquipReq,
    RegistrationComment,
    CommentType,
    AdditionalSiteRequirement,
)
import magic


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

    def clean_food_sale_type_name(self):
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
    inventory_item = ModelChoiceField(
        queryset=InventoryItem.objects.all(),
        empty_label='Please Select',
        widget=Select(attrs={
            'class': "form-select",
            'style': 'max-width: 300px;',
        })
    )

    class Meta:
        model = StallCategory
        fields = ['category_name', 'has_inventory_item', 'inventory_item', 'is_active', ]
        widgets = {
            'category_name': TextInput(attrs={
                'class': "form-control",
                'size': '400',
                'placeholder': 'Stall Category Name'
            }),
            'has_inventory_item': CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'is_active': CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

    def __init__(self, *args, **kwargs):
        self.created_by = kwargs.pop('created_by', None)
        super(StallCategoryCreationForm, self).__init__(*args, **kwargs)

    def clean_stall_category_name(self):
        category_name = self.cleaned_data['category_name']
        if StallCategory.objects.filter(category_name=category_name).exists():
            raise forms.ValidationError("This  Stall Category has already been created.")
        return category_name


class StallCategoryUpdateForm(ModelForm):
    """
    Form for updating stall category details
    """
    inventory_item = ModelChoiceField(
        queryset=InventoryItem.objects.all(),
        empty_label='Please Select',
        widget=Select(attrs={
            'class': "form-select",
            'style': 'max-width: 300px;',
        })
    )

    class Meta:
        model = StallCategory
        fields = ['category_name', 'has_inventory_item', 'inventory_item', 'is_active', ]
        widgets = {
            'category_name': TextInput(attrs={
                'class': "form-control",
                'size': '400',
                'placeholder': 'Stall Category Name'
            }),
            'has_inventory_item': CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'is_active': CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }


class StallRegistrationCreateForm(ModelForm):
    """
    Form for creating Stall Registrations
    """

    fair = ModelChoiceField(
        queryset=Fair.objects.filter(is_activated=True),
        empty_label='Please Select',
        widget=Select(attrs={
            'class': "form-select",
            'style': 'max-width: 300px;',
            'hx-trigger': 'change',
            'hx-post': '.',
            'hx-target': '#stallregistration_data',
        })
    )

    stall_category = ModelChoiceField(
        queryset=StallCategory.objects.filter(is_active=True),
        empty_label='Please Select',
        widget=Select(attrs={
            'class': "form-select",
            'style': 'max-width: 300px;',
            'hx-trigger': 'change',
            'hx-post': '.',
            'hx-target': '#stallregistration_data',
        })
    )

    site_size = ModelChoiceField(
        queryset=InventoryItem.objects.filter(item_type=1),
        empty_label='Please Select',
        label='What size Site do you want?',
        widget=Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 300px;',
            'hx-trigger': 'change',
            'hx-post': '.',
            'hx-target': '#stallregistration_data',
        })
    )

    class Meta:
        model = StallRegistration
        fields = [
            'fair',
            'stall_manager_name',
            'manager_vehicle_registration',
            'stall_category',
            'stall_description',
            'products_on_site',
            'site_size',
            'trestle_required',
            'trestle_quantity',
            'stall_shelter',
            'vehicle_on_site',
            'vehicle_length',
            'vehicle_width',
            'vehicle_image',
            'power_required',
            'multi_site',
            'selling_food'
        ]
        labels = {
            'stall_manager_name': 'Stall manager\'s name',
            'manager_vehicle_registration': 'Manager\'s vehicle registration',
            'multi-site': 'Do you want more than a single site with this registration?',
            'selling_food': 'Are you selling food?',
        }
        widgets = {
            'stall_manager_name': TextInput(attrs={
                'placeholder': 'First and last name',
                'class': "form-control",
                'style': 'max-width: 300px;',
            }),
            'manager_vehicle_registration': TextInput(attrs={
                'placeholder': 'Rego',
                'class': "form-control",
                'style': 'max-width: 300px;',
            }),
            'stall_description': Textarea(attrs={
                'class': "form-control text",
                'style': 'max-width: 400px;',
                'placeholder': 'Outline the purpose of the stall'
            }),
            'products_on_site': Textarea(attrs={
                'class': "form-control text",
                'style': 'max-width: 400px;',
                'placeholder': 'Outline of the items being sold at the stall'
            }),
            'trestle_required': CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'trestle_quantity': NumberInput(attrs={
                'class': "form_control",
                'min': '0',
                'max': '4',
                'step': '1',
                'hx-trigger': 'change',
                'hx-post': '.',
                'hx-target': '#stallregistration_data',
            }),
            'stall_shelter': Textarea(attrs={
                'class': "form-control text",
                'style': 'max-width: 400px; height: 75px;',
                'placeholder': 'Describe any shelter to be used in conjunction with the stall'
            }),
            'vehicle_on_site': CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'vehicle_length': NumberInput(attrs={
                'class': "form_control",
                'min': '0',
                'max': '10',
                'step': '0.1',
            }),
            'vehicle_width': NumberInput(attrs={
                'class': "form_control",
                'min': '0',
                'max': '10',
                'step': '0.1',
            }),
            'vehicle_image': FileInput(),
            'power_required': CheckboxInput(attrs={
                'class': 'form-check-input',
                'hx-trigger': 'change',
                'hx-post': '.',
                'hx-target': '#stallregistration_data',
            }),
            'multi-site': CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'selling_food': CheckboxInput(attrs={
                'class': 'form-check-input',
                'hx-trigger': 'change',
                'hx-post': '.',
                'hx-target': '#stallregistration_data'
        }),
        }

    def clean_vehicle_image(self):
        allowed_filetypes = [ 'image/jpeg', 'image/jpg', 'image/png']
        thefile = self.cleaned_data.get("vehicle_image", False)
        if thefile is not None:
            mime = magic.from_buffer(thefile.read(), mime=True)
            if mime not in allowed_filetypes:
                raise forms.ValidationError('File must be a png or jpg image')
            else:
                return thefile

    def clean(self):
        cleaned_data = super().clean()
        stall_category = cleaned_data.get('stall_category')
        selling_food = cleaned_data.get('selling_food')

        if stall_category and selling_food:
            # Only do something if both fields are valid so far.
            if 'Food' not in str(stall_category):
                raise ValidationError(
                    "You must select a Stall category of either:"
                    "Food Drink (other) or Food Drink (consumption on site)"
                    "If you are selling any type of food item"
                )
        return self.cleaned_data  # never forget this!


class StallRegistrationUpdateForm(ModelForm):
    """
    Form for updating Stall Registrations
    """
    fair = ModelChoiceField(
        queryset=Fair.objects.filter(is_activated=True),
        empty_label='Please Select',
        widget=Select(attrs={
            'class': "form-select",
            'style': 'max-width: 300px;',
            'hx-trigger': 'change',
            'hx-post': '.',
            'hx-target': '#stallregistration_data',
        })
    )

    stall_category = ModelChoiceField(
        queryset=StallCategory.objects.filter(is_active=True),
        empty_label='Please Select',
        widget=Select(attrs={
            'class': "form-select",
            'style': 'max-width: 300px;',
            'hx-trigger': 'change',
            'hx-post': '.',
            'hx-target': '#stallregistration_data',
        })
    )

    site_size = ModelChoiceField(
        queryset=InventoryItem.objects.filter(item_type=1),
        empty_label='Please Select',
        label='What size Site do you want?',
        widget=Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 300px;',
            'hx-trigger': 'change',
            'hx-post': '.',
            'hx-target': '#stallregistration_data',
        })
    )

    class Meta:
        model = StallRegistration
        fields = [
            'fair',
            'stall_manager_name',
            'manager_vehicle_registration',
            'stall_category',
            'stall_description',
            'products_on_site',
            'site_size',
            'trestle_required',
            'trestle_quantity',
            'stall_shelter',
            'vehicle_on_site',
            'vehicle_length',
            'vehicle_width',
            'vehicle_image',
            'power_required',
            'multi_site',
            'selling_food'
        ]
        labels = {
            'stall_manager_name': 'Stall manager\'s name',
            'manager_vehicle_registration': 'Manager\'s vehicle registration',
            'multi-site': 'Do you want more than a single site with this registration?',
            'selling_food': 'Are you selling food?',
        }
        widgets = {
            'stall_manager_name': TextInput(attrs={
                'placeholder': 'First and last name',
                'class': "form-control",
                'style': 'max-width: 300px;',
            }),
            'manager_vehicle_registration': TextInput(attrs={
                'placeholder': 'Rego',
                'class': "form-control",
                'style': 'max-width: 300px;',
            }),
            'stall_description': Textarea(attrs={
                'class': "form-control text",
                'style': 'max-width: 400px;',
                'placeholder': 'Outline the purpose of the stall'
            }),
            'products_on_site': Textarea(attrs={
                'class': "form-control text",
                'style': 'max-width: 400px;',
                'placeholder': 'Outline of the items being sold at the stall'
            }),
            'trestle_required': CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'trestle_quantity': NumberInput(attrs={
                'class': "form_control",
                'min': '0',
                'max': '4',
                'step': '1',
                'hx-trigger': 'change',
                'hx-post': '.',
                'hx-target': '#stallregistration_data',
            }),
            'stall_shelter': Textarea(attrs={
                'class': "form-control text",
                'style': 'max-width: 400px;',
                'placeholder': 'Describe any shelter to be used in conjunction with the stall'
            }),
            'vehicle_on_site': CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'vehicle_length': NumberInput(attrs={
                'class': "form_control",
                'min': '0',
                'max': '10',
                'step': '0.1',
            }),
            'vehicle_width': NumberInput(attrs={
                'class': "form_control",
                'min': '0',
                'max': '10',
                'step': '0.1',
            }),
            'vehicle_image': FileInput(),
            'power_required': CheckboxInput(attrs={
                'class': 'form-check-input',
                'hx-trigger': 'change',
                'hx-post': '.',
                'hx-target': '#stallregistration_data',
            }),
            'multi-site': CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'selling_food': CheckboxInput(attrs={
                'class': 'form-check-input',
                'hx-trigger': 'change',
                'hx-post': '.',
                'hx-target': '#stallregistration_data'
            }),
        }

    def clean_vehicle_image(self):
        allowed_filetypes = [ 'image/jpeg', 'image/jpg', 'image/png']
        thefile = self.cleaned_data.get("vehicle_image", False)
        if thefile is not None:
            mime = magic.from_buffer(thefile.read(), mime=True)
            print(mime)
            if mime not in allowed_filetypes:
                raise forms.ValidationError('File must be a png or jpg image')
            else:
                return thefile

    def clean(self):
        cleaned_data = super().clean()
        stall_category = cleaned_data.get('stall_category')
        selling_food = cleaned_data.get('selling_food')

        if stall_category and selling_food:
            # Only do something if both fields are valid so far.
            if 'Food' not in str(stall_category):
                raise ValidationError(
                    "You must select a Stall category of either:"
                    "Food Drink (other) or Food Drink (consumption on site)"
                    "If you are selling any type of food item"
                )
        return self.cleaned_data  # never forget this!

class FoodRegistrationForm(ModelForm):
    """
    Form for capturing details need for a food stall registration
    """

    food_stall_type = ModelChoiceField(
        queryset=FoodSaleType.objects.filter(is_active=True),
        empty_label='Please Select',
        label='Food Stall Type',
        required=True,
        widget=Select(attrs={'class': "form-select", 'style': 'max-width: 300px;', })
    ),

    class Meta:
        model = FoodRegistration
        fields = [
            'registration',
            'food_stall_type',
            'food_display_method',
            'food_fair_consumed',
            'food_source',
            "has_food_prep",
            'food_storage_prep_method',
            'food_storage_prep',
            'hygiene_methods',
            'has_food_certificate',
            'certificate_expiry_date',
            'food_registration_certificate',
        ]
        labels = {
            'food_stall_type': 'Food Stall Type',
            'food_display_method': 'How will the food be displayed',
            'food_fair_consumed': 'Is the food being sold intended for consumption at the fair',
            'food_source': 'Where will you obtain the food from',
            'has_food_prep': 'Is any storage or preparation of the food to be undertaken after it is obtained by the '
                             'operator of the food stall?',
            'food_storage_prep_method': 'Please describe food storage and/or preparation prior to the fair day',
            'food_storage_prep': 'How will food utensils, appliances and equipment be stored during the day',
            'hygiene_methods': 'What arrangements do you have for hand washing',
            'has_food_certificate': 'Do you have a food registration certificate',
            'certificate_expiry_date': 'What is the expiry date of the certificate',
            'food_registration_certificate': 'Please upload your food certificate',
        }
        widgets = {
            'registration': HiddenInput(),
            'food_display_method': Textarea(attrs={
                'class': "form-control",
                'style': 'max-width: 400px;',
                'rows': '5',
                'placeholder': 'Describe how the food will be displayed'
            }),
            'food_fair_consumed': CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'food_source': Textarea(attrs={
                'rows': '5',
                'class': "form-control",
                'style': 'max-width: 400px;',
                'placeholder': 'Describe where the food being sold will be sourced from'
            }),
            'has_food_prep': CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'food_storage_prep_method': Textarea(attrs={
                'rows': '5',
                'class': "form-control",
                'style': 'max-width: 400px;',
                'placeholder': 'Describe where and how will the pre-sale storage or preparation of the food take place'
            }),
            'food_storage_prep': Textarea(attrs={
                'rows': '5',
                'class': "form-control",
                'style': 'max-width: 400px;',
                'placeholder': 'Describe method and location of Food utensils, appliances and equipment.'
            }),
            'hygiene_methods': Textarea(attrs={
                'rows': '5',
                'class': "form-control",
                'style': 'max-width: 400px;',
                'placeholder': 'Describe What arrangements have been made for toilet use and washing hands.'
            }),
            'has_food_certificate': CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'certificate_expiry_date': DateInput(attrs={
                'class': 'form-control',
                'style': 'max-width: 400px;',
                'type' : 'date'
            }),
            'food_registration_certificate': FileInput(),
        }

    def clean_food_registration_certificate(self):
        allowed_filetypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png']
        thefile = self.cleaned_data.get("food_registration_certificate", False)
        if thefile is not None:
            mime = magic.from_buffer(thefile.read(), mime=True)
            print(mime)
            if mime not in allowed_filetypes:
                raise forms.ValidationError('File must be a pdf, png or jpg document')
            else:
                return thefile

class FoodPrepEquipReqForm(ModelForm):
    """
    Form for populating the junction table between food registration and food preparation equipment
    """
    food_prep_equipment = ModelChoiceField(
        queryset=FoodPrepEquipment.objects.all(),
        empty_label='Please Select',
        label='Type of Food Preparation Equipment',
        required=True,
        widget=Select(attrs={
            'class': "form-select",
            'style': 'max-width: 300px;',
        })
    )

    class Meta:
        model = FoodPrepEquipReq
        exclude = ['food_registration']
        fields = [
            'food_registration',
            'food_prep_equipment',
            'how_powered',
            'equipment_quantity'
        ]
        widgets = {
            'how_powered': RadioSelect(attrs={
                'style': 'display: inline-block',
            })
        }
        error_messages = {
            'text': {'required': "You can't have an empty list item"}
        }


class AdditionalSiteReqForm(ModelForm):
    """
    Form for populating the AdditionalSiteReq model
    """
    site_size = ModelChoiceField(
        queryset=InventoryItem.objects.filter(item_type=1),
        empty_label='Show All',
        label='Site Size',
        required=True,
        widget=Select(attrs={
            'class': 'form-control',
            'style': 'max-width: 300px;',
        })
    )

    class Meta:
        model = AdditionalSiteRequirement
        exclude = ['stall_registration']
        fields = [
            'site_quantity',
            'site_size',
            'location_choice'
        ]
        widgets = {
            'location_choice': RadioSelect(attrs={
                'style': 'display: inline-block',
            })
        }
        error_messages = {
            'text': {'required': "You can't have an empty list item"}
        }


class CommentFilterForm(Form):
    """
    Filter form to enable historical and archived comments to be viewed
    """
    fair = ModelChoiceField(
        queryset=Fair.objects.all(),
        required=False,
        widget=Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 300px;',
            'hx-trigger': 'change',
            'hx-post': 'comments/',
            'hx-target': '#comment_data',
        })
    )
    is_archived = BooleanField(
        required=False,
        widget=CheckboxInput(attrs={
            'class': 'form-check-input',
            'hx-trigger': 'change',
            'hx-post': 'comments/',
            'hx-target': '#comment_data',
            'checked': False
        })
    )

    class Meta:
        fields = [
            'fair',
            'is_archived'
        ]
        labels = {
            'fair':'Select Past Fairs',
            'is_archived': 'Show Archived Comments'
        }


class RegistrationCommentForm(ModelForm):
    """
    Form for capturing Stallholder comments typically associated with stall registration
    """

    comment_type = ModelChoiceField(
        queryset=CommentType.objects.filter(is_active=True),
        empty_label='Please Select',
        label='Comment Type',
        required=True,
        widget=Select(attrs={'class': "form-select", 'style': 'max-width: 300px;', })
    )

    class Meta:
        model = RegistrationComment
        fields = [
            'comment_type',
            'comment'
        ]
        labels = {
            'comment_type': 'Comment Type'
        }
        widgets = {
            'comment': Textarea(attrs={
                'class': "form-control",
                'style': 'max-width: 400px;',
                'placeholder': 'Detail your query / request or comment'
            }),
        }


class CommentReplyForm(ModelForm):
    """
    Form for capturing replies to comments typically associated with stall registration
    """

    class Meta:
        model = RegistrationComment
        fields = [
            'comment'
        ]
        widgets = {
            'comment': Textarea(attrs={
                'class': "form-control",
                'style': 'max-width: 400px;',
                'placeholder': 'Detail your reply'
            }),
        }


class StallRegistrationFilterForm(Form):
    """
    Filter form for listing stall registrations by Fair
    """
    fair = ModelChoiceField(
        queryset=Fair.objects.all(),
        empty_label='Show All',
        label='Fairs',
        required=False,
        widget=Select(attrs={
            'class': 'form-control',
            'style': 'max-width: 300px;',
            'hx-trigger': 'change',
            'hx-post': '.',
            'hx-target': '#stallregistration_data',
        })
    )
    site_size = ModelChoiceField(
        queryset=InventoryItem.objects.filter(item_type=1),
        empty_label='Show All',
        label='Site Size',
        required=False,
        widget=Select(attrs={
            'class': 'form-control',
            'style': 'max-width: 300px;',
            'hx-trigger': 'change',
            'hx-post': '.',
            'hx-target': '#stallregistration_data',
        })
    )

