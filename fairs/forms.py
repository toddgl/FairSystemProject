# fairs/forms.py

from django.contrib.admin.widgets import AdminSplitDateTime, AdminDateWidget
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
from fairs.models import (
    Zone,
    Site,
    Fair,
    Event,
    InventoryItem,
    EventSite,
    InventoryItemFair,
    PowerBox,
    EventPower,
)
from datetime import datetime
from django.utils.timezone import make_aware
from django.forms import MultiWidget, DateTimeField, DateField, DateInput, DateTimeInput


# nightmare discussion here https://stackoverflow.com/questions/38601/using-django-time-date-widgets-in-custom-form
class MinimalSplitDateTimeMultiWidget(MultiWidget):

    def __init__(self, widgets=None, attrs=None):
        if widgets is None:
            if attrs is None:
                attrs = {}
            date_attrs = attrs.copy()
            time_attrs = attrs.copy()

            date_attrs['type'] = 'date'
            time_attrs['type'] = 'time'

            widgets = [
                TextInput(attrs=date_attrs),
                TextInput(attrs=time_attrs),
            ]
        super().__init__(widgets, attrs)

    # Nabbed from https://docs.djangoproject.com/en/3.1/ref/forms/widgets/#django.forms.MultiWidget.decompress
    def decompress(self, value):
        if value:
            return [value.date(), value.strftime('%H:%M')]
        return [None, None]

    def value_from_datadict(self, data, files, name):
        date_str, time_str = super().value_from_datadict(data, files, name)
        # DateField expects a single string that it can parse into a date.

        if date_str == time_str == '':
            return None

        if time_str == '':
            time_str = '00:00'

        my_datetime = datetime.strptime(date_str + ' ' + time_str, "%Y-%m-%d %H:%M")
        # making timezone aware
        return make_aware(my_datetime)


class UserFullName(ModelForm):

    def __unicode__(self):
        return self.get_full_name()


class FairCreateForm(ModelForm):
    """
    Form for creating a new Fair
    """

    class Meta:
        model = Fair
        fields = ['fair_year', 'fair_name', 'fair_description',
                  'activation_date', 'is_activated']
        widgets = {
            'fair_year': TextInput(attrs={
                'class': "form-control",
                'size': '4',
                'placeholder': 'Fair Year'
            }),
            'fair_name': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 500px;',
                'placeholder': 'Fair Name'
            }),
            'fair_description': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 750px;',
                'placeholder': 'Fair Description'
            }),
            # 'activation_date': AdminSplitDateTime(),
            'activation_date': MinimalSplitDateTimeMultiWidget(),
            "is_activated": CheckboxInput(attrs={
                'class': 'form-check-input',
                'readonly': 'readonly'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.created_by = kwargs.pop('created_by', None)
        super(FairCreateForm, self).__init__(*args, **kwargs)

    def clean_fair_name(self):
        fair_name = self.cleaned_data['fair_name']
        if Fair.objects.filter(created_by=self.created_by, fair_name=fair_name).exists():
            raise forms.ValidationError("This fair has already been created.")
        return fair_name


class FairDetailForm(ModelForm):
    """
    Form for viewing and updating the Fair model
    """

    class Meta:
        model = Fair
        fields = ['fair_year', 'fair_name', 'date_cancelled', 'fair_description', 'is_cancelled',
                  'activation_date', 'is_activated']
        widgets = {
            'fair_year': TextInput(attrs={
                'class': "form-control",
                'size': '4',
                'placeholder': 'Fair Year'
            }),
            'fair_name': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 500px;',
                'placeholder': 'Fair Name'
            }),
            'fair_description': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 750px;',
                'placeholder': 'Fair Description'
            }),
            'date_cancelled': DateInput(attrs={
                'class': "form-control",
                'readonly': 'readonly'
            }),
            # 'activation_date': AdminSplitDateTime(),
            'activation_date': MinimalSplitDateTimeMultiWidget(),
            "is_activated": CheckboxInput(attrs={
                'class': 'form-check-input',
                'readonly': 'readonly'
            }),
            'is_cancelled': CheckboxInput(attrs={
                'class': 'form-check-input',
                'readonly': 'readonly'
            }),

        }


class EventCreateForm(ModelForm):
    """
    Form for create a new Fair Event
    """

    class Meta:
        model = Event
        fields = ['fair', 'event_name', 'event_description',
                  'original_event_date']
        widgets = {
            'fair': Select(),
            'event_name': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 500px;',
                'placeholder': 'Event Name'
            }),
            'event_description': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 750px;',
                'placeholder': 'Fair Description'
            }),
            'original_event_date': NumberInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.created_by = kwargs.pop('created_by', None)
        super(EventCreateForm, self).__init__(*args, **kwargs)

    def clean_event_name(self):
        event_name = self.cleaned_data['event_name']
        if Event.objects.filter(created_by=self.created_by, event_name=event_name).exists():
            raise forms.ValidationError("This Event has already been created.")
        return event_name


class EventDetailForm(ModelForm):
    """
    Form for viewing and updating the Event model
    """

    class Meta:
        model = Event
        exclude = ('created_by', 'updated_by', 'date_created', 'date_updated', 'sites', 'fair',)
        # fields = '__all__'
        widgets = {
            'fair': Select(),
            'event_name': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 500px;',
                'placeholder': 'Event Name'
            }),
            'event_description': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 750px;',
                'placeholder': 'Fair Description'
            }),
            'original_event_date': DateInput(attrs={
                'class': "form-control",
                'readonly': 'readonly'
            }),
            'date_cancelled': MinimalSplitDateTimeMultiWidget(),
            'is_cancelled': CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'postponement_event_date': SelectDateWidget(),
            "is_postponed": CheckboxInput(attrs={
                'class': 'form-check-input'
            }),

        }


class SiteCreateForm(ModelForm):
    """
    Form for Creating a new site
    """

    class Meta:
        model = Site
        exclude = ('created_by', 'updated_by', 'date_created', 'date_updated',)
        widgets = {
            'zone': Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px;'
            }),
            'site_name': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Site Name'
            }),
            'site_size': Select(attrs={
                'class': "form-select`",
                'style': 'max-width: 300px;',
            })
        }

    def __init__(self, *args, **kwargs):
        self.created_by = kwargs.pop('created_by', None)
        super(SiteCreateForm, self).__init__(*args, **kwargs)

    def clean_site_name(self):
        site_name = self.cleaned_data['site_name']
        if Site.objects.filter(site_name=site_name).exists():
            raise forms.ValidationError("This Site has already been created.")
        return site_name


class SiteDetailForm(ModelForm):
    """
    Form for updating a site
    """

    class Meta:
        model = Site
        exclude = ('created_by', 'updated_by', 'date_created', 'date_updated',)
        widgets = {
            'site_name': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 100px;',
                'placeholder': 'Site Name'
            }),
            'site_size': Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px;',
            }),
            'zone': Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px;',
            })
        }


class ZoneCreateForm(ModelForm):
    """
    Form for Creating a new zone
    """

    class Meta:
        model = Zone
        fields = ['zone_name', 'zone_code', 'map_pdf', 'trestle_source']
        widgets = {
            'zone_name': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Zone Name'
            }),
            'zone_code': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 100px; text-transform: uppercase;',
                'placeholder': 'XX'
            }),
            'map_pdf': FileInput(),
            'trestle_source': CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.created_by = kwargs.pop('created_by', None)
        super(ZoneCreateForm, self).__init__(*args, **kwargs)

    def clean_zone_name(self):
        zone_name = self.cleaned_data['zone_name']
        if Zone.objects.filter(zone_name=zone_name).exists():
            raise forms.ValidationError("This Zone has already been created.")
        return zone_name


class ZoneDetailForm(ModelForm):
    """
    Form for updating a zone
    """

    class Meta:
        model = Zone
        fields = ['zone_name', 'zone_code', 'map_pdf', 'trestle_source']
        widgets = {
            'zone_name': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Site Name'
            }),
            'zone_code': TextInput(attrs={
                'class': "form-control",
                'style': 'text-transform: uppercase;',
                'placeholder': 'XX'
            }),
            'map_pdf': FileInput(),
            'trestle_source': CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class InventoryItemCreateForm(ModelForm):
    """
    Form for creating a new InventoryItem
    """
    class Media:
        js = ('js/item_type.js',)

    class Meta:
        model = InventoryItem
        fields = ['item_name', 'item_type', 'item_description', 'item_quantity', 'site_size', ]
        labels = {
            'item_type': 'Inventory Item Type'
        }
        widgets = {
            'item_name': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Item Name'
            }),
            'item_type': Select(attrs={
                'class': "form-check",
            }),
            'item_description': Textarea(attrs={
                'class': "form-control",
                'style': 'max-width: 400px;',
                'placeholder': 'Please enter the description'
            }),
            'item_quantity': NumberInput(attrs={
                'class': "form_control",
                'style': 'max-width: 400px;',
                'placeholder': 'Number of Items',
                'label': 'Total Number Available'
            }),
            'site_size': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 100px;',
                'placeholder': 'Site Size'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.created_by = kwargs.pop('created_by', None)
        super(InventoryItemCreateForm, self).__init__(*args, **kwargs)

    def clean_item_name(self):
        item_name = self.cleaned_data['item_name']
        if InventoryItem.objects.filter(item_name=item_name).exists():
            raise forms.ValidationError("This Inventory Item has already been created.")
        return item_name


class InventoryItemDetailForm(ModelForm):
    """
    Form for updating an InventoryItem
    """
    class Media:
        js = ('js/item_type.js',)

    class Meta:
        model = InventoryItem
        fields = ['item_name', 'item_type', 'item_description', 'item_quantity', 'site_size']
        labels = {
            'item_type': 'Inventory Item Type'
        }
        widgets = {
            'item_name': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Item Name'
            }),
            'item_type': Select(attrs={
                'class': "form-check",
            }),
            'item_description': Textarea(attrs={
                'class': "form-control",
                'style': 'max-width: 400px;',
                'placeholder': 'Please enter the  description'
            }),
            'item_quantity': NumberInput(attrs={
                'class': "form_control",
                'style': 'max-width: 400px;',
                'placeholder': 'Number of Items',
                'label': 'Total Number Available'
            }),
            'site_size': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 100px;',
                'placeholder': 'Site Size'
            }),
        }


class EventSiteDetailForm(ModelForm):
    """
    Form for updating an EventSite
    """

    class Meta:
        model = EventSite
        fields = ['event', 'site', 'site_status']
        widgets = {
            'event': Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px;',
            }),
            'site': Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px;',
            }),
            'site_status': Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px;',
            }),
        }


class EventSiteCreateForm(ModelForm):
    """
    Form for Creating a new event site relationship
    """

    class Meta:
        model = EventSite
        exclude = ()
        widgets = {
            'event': Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px;',
            }),
            'site': Select(attrs={
                'class': "form-select`",
                'style': 'max-width: 300px;',
            }),
            'site_status': Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px;',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(EventSiteCreateForm, self).__init__(*args, **kwargs)


class InventoryItemFairDetailForm(ModelForm):
    """
    Form for updating an InventoryItemFair
    """

    class Meta:
        model = InventoryItemFair
        fields = ['fair', 'inventory_item', 'price_rate', 'price']
        widgets = {
            'fair': Select(attrs={
                'class': 'form-select',
                'style': 'max-width: 300px;',
            }),
            'inventory_item': Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px;',
            }),
            'price_rate': Select(attrs={
                'class': 'form-select',
                'style': 'max-width: 300px;',
            }),
            'price': NumberInput(attrs={
                'class': "form-control",
                'style': 'max-width: 100px;',
                'placeholder': 'Item Price'
            }),
        }


class InventoryItemFairCreateForm(ModelForm):
    """
        Form for Creating a new inventory item fair relationship including setting the item price
    """
    class Meta:
        model = InventoryItemFair
        fields = ['fair', 'inventory_item', 'price_rate', 'price']
        widgets = {
            'fair': Select(attrs={
                'class': 'form-select',
                'style': 'max-width: 300px;',
            }),
            'inventory_item': Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px;',
            }),
            'price_rate': Select(attrs={
                'class': 'form-select',
                'style': 'max-width: 300px;',
            }),
            'price': NumberInput(attrs={
                'class': "form-control",
                'style': 'max-width: 100px;',
                'placeholder': 'Item Price'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(InventoryItemFairCreateForm, self).__init__(*args, **kwargs)


class DashboardSiteFilterForm(Form):
    """
    Form for selecting filters for the site dashboard
    """

    event = ModelChoiceField(
        queryset=Event.objects.all(),
        empty_label='Show All',
        label='Events',
        required=False,
        widget=Select(attrs={'class': 'form-control'}))
    zone = ModelChoiceField(
        queryset=Zone.objects.all(),
        empty_label='Show All',
        label='Site Zones',
        required=False,
        widget=Select(attrs={'class': 'form-control'}))

    class Meta:
        model = EventSite
        fields = ['event', 'site']


class PowerBoxCreateForm(ModelForm):
    """
    Form for Creating a new zone
    """

    class Meta:
        model = PowerBox
        fields = ['power_box_name', 'socket_count', 'max_load', 'zone']
        widgets = {
            'power_box_name': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Powerbox Name'
            }),
            'socket_count': NumberInput(attrs={
                'class': "form-control",
                'style': 'max-width: 100px;',
                'placeholder': 'Number'
            }),
            'max_load': NumberInput(attrs={
                'class': 'form-control',
                'style': 'max-width: 100px;',
                'placeholder': 'Kilowatts'
            }),
            'zone': Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px;',
            })
        }

    def __init__(self, *args, **kwargs):
        self.created_by = kwargs.pop('created_by', None)
        super(PowerBoxCreateForm, self).__init__(*args, **kwargs)

    def clean_power_box_name(self):
        power_box_name = self.cleaned_data['power_box_name']
        if PowerBox.objects.filter(power_box_name=power_box_name).exists():
            raise forms.ValidationError("This Powerbox has already been created.")
        return power_box_name


class PowerBoxUpdateDetailForm(ModelForm):
    """
    Form for updating a powerbox
    """

    class Meta:
        model = PowerBox
        fields = ['power_box_name', 'socket_count', 'max_load', 'zone']
        widgets = {
            'power_box_name': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Powerbox Name'
            }),
            'socket_count': NumberInput(attrs={
                'class': "form-control",
                'style': 'max-width: 100px;',
                'placeholder': 'Number'
            }),
            'max_load': NumberInput(attrs={
                'class': 'form-control',
                'style': 'max-width: 100px;',
                'placeholder': 'Kilowatts'
            }),
            'zone': Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px;',
            })
        }


class EventPowerUpdateDetailForm(ModelForm):
    """
    Form for updating an EventPower Junction table and record power load
    """

    class Meta:
        model = EventPower
        fields = ['event', 'power_box', 'power_load']
        widgets = {
            'event': Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px;',
            }),
            'power_box': Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px;',
            }),
            'power_load': NumberInput(attrs={
                'class': "form-select",
                'style': 'max-width: 300px;',
                'placeholder': 'Kilowatts'
            }),
        }


class EventPowerCreateForm(ModelForm):
    """
    Form for Creating a new event powerbox  relationship
    """

    class Meta:
        model = EventPower
        exclude = ()
        widgets = {
            'event': Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px;',
            }),
            'power_box': Select(attrs={
                'class': "form-select`",
                'style': 'max-width: 300px;',
            }),
            'power_load': NumberInput(attrs={
                'class': "form-select",
                'style': 'max-width: 300px;',
                'placeholder': 'Kilowatts'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(EventPowerCreateForm, self).__init__(*args, **kwargs)

