# fairs/forms.py

from django.contrib.admin.widgets import AdminSplitDateTime, AdminDateWidget
from django import forms
from django.forms import (
    BooleanField,
    Form,
    ModelForm,
    ChoiceField,
    DateInput,
    DateTimeInput,
    ModelChoiceField,
    ModelMultipleChoiceField,
    IntegerField,
    Textarea,
    TextInput,
    FileInput,
    CheckboxInput,
    MultiWidget,
    NumberInput,
    RadioSelect,
    Select,
    SelectMultiple,
    SelectDateWidget
)
from fairs.models import (
    Location,
    Zone,
    ZoneMap,
    Site,
    Fair,
    Event,
    InventoryItem,
    EventSite,
    InventoryItemFair,
    PowerBox,
    EventPower,
    SiteAllocation,
)
from accounts.models import CustomUser
from registration.models import (
    StallRegistration,
    RegistrationComment,
    CommentType
)
from datetime import datetime
from django.utils.timezone import make_aware


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
            'is_activated': CheckboxInput(attrs={
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
                  'activation_date', 'allocation_email_date', 'is_activated', 'is_open']
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
            'allocation_email_date': MinimalSplitDateTimeMultiWidget(),
            "is_activated": CheckboxInput(attrs={
                'class': 'form-check-input',
                'readonly': 'readonly'
            }),
            'is_cancelled': CheckboxInput(attrs={
                'class': 'form-check-input',
                'readonly': 'readonly'
            }),
            'is_open': CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }


class EventCreateForm(ModelForm):
    """
    Form for create a new Fair Event
    """

    class Meta:
        model = Event
        fields = ['fair', 'event_name', 'event_description', 'event_sequence',
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
            'event_sequence': Select(attrs={
                'class': 'form-select',
                'style': 'max-width: 300px;',
            }),
            'original_event_date': DateInput(attrs={'type': 'date'}),

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
        labels = {
            'postponement_event_date': 'Postponed Event Date'
        }
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
            'event_sequence': Select(attrs={
                'class': 'form-select',
                'style': 'max-width: 300px;',
            }),
            'original_event_date': DateInput(attrs={
                'type': 'date',
                'style': 'max-width: 300px;',
                'readonly': 'readonly'
            }),
            'date_cancelled': MinimalSplitDateTimeMultiWidget(),
            'is_cancelled': CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'postponement_event_date': DateInput(attrs={
                'type': 'date',
                'min': datetime.now().date(),
            }),
            "is_postponed": CheckboxInput(attrs={
                'class': 'form-check-input'
            }),

        }


class SiteListFilterForm(Form):
    """
    Filter form for to list the sites by Zones
    """
    zone = ModelChoiceField(
        queryset=Zone.objects.all(),
        empty_label='Show All',
        label='Site Zones',
        required=False,
        widget=Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 300px;',
            'hx-trigger': 'change',
            'hx-post': '.',
            'hx-target': '#site_data',
        })
    )
    site_size = ModelChoiceField(
        queryset=InventoryItem.objects.filter(item_type=1),
        empty_label='Show All',
        label='Site Size',
        required=False,
        widget=Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 300px;',
            'hx-trigger': 'change',
            'hx-post': '.',
            'hx-target': '#site_data',
        })
    )

    class Meta:
        fields = [
            'zone',
            'site_size'
        ]


class SiteCreateForm(ModelForm):
    """
    Form for Creating a new site
    """

    zone = ModelChoiceField(
        queryset=Zone.objects.all(),
        empty_label='Please Select',
        label='Site Zones',
        required=False,
        widget=Select(attrs={'class': 'form-select', 'style': 'max-width: 300px;'})
    )

    site_size = ModelChoiceField(
        queryset=InventoryItem.objects.filter(item_type=1),
        empty_label='Please Select',
        label='Site Size',
        required=False,
        widget=Select(attrs={'class': 'form-select', 'style': 'max-width: 300px;'})
    )
    site_note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class':'form-control', 'style': 'max-width: 400px;','placeholder':'Please enter a note if required'})
    )

    class Meta:
        model = Site
        fields = [
            'site_name',
            'zone',
            'site_size',
            'site_note',
            'is_active',
        ]
        widgets = {
            'site_name': TextInput(attrs={
                'placeholder': 'Site Name',
                'class': "form-select`",
                'style': 'max-width: 300px;',
            }),
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

    zone = ModelChoiceField(
        queryset=Zone.objects.all(),
        empty_label='Please Select',
        label='Site Zones',
        required=False,
        widget=Select(attrs={'class': 'form-select', 'style': 'max-width: 300px;'})
    )

    site_size = ModelChoiceField(
        queryset=InventoryItem.objects.filter(item_type=1),
        empty_label='Please Select',
        label='Site Size',
        required=False,
        widget=Select(attrs={'class': 'form-select', 'style': 'max-width: 300px;'})
    )
    site_note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class':'form-control', 'style': 'max-width: 400px;','placeholder':'Please enter a note if required'})
    )

    class Meta:
        model = Site
        fields = [
            'site_name',
            'zone',
            'site_size',
            'site_note',
            'is_active',
        ]
        widgets = {
            'site_name': TextInput(attrs={
                'placeholder': 'Site Name',
                'class': "form-control",
                'style': 'max-width: 300px;',
            })
        }


class ZoneCreateForm(ModelForm):
    """
    Form for Creating a new zone
    """

    class Meta:
        model = Zone
        fields = ['location', 'zone_name', 'zone_code', 'trestle_source']
        widgets = {
            'location': Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px;'
            }),
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
            'trestle_source': Select(attrs={
                'class': 'form-select',
                'style': 'max-width: 300px;',
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
        fields = ['location', 'zone_name', 'zone_code', 'trestle_source']
        widgets = {
            'location': Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px;'
            }),
            'zone_name': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Zone Name'
            }),
            'zone_code': TextInput(attrs={
                'class': "form-control",
                'style': 'text-transform: uppercase;',
                'placeholder': 'XX'
            }),
            'trestle_source': Select(attrs={
                'class': 'form-select',
                'style': 'max-width: 300px;',
            }),
        }


class ZoneMapCreateForm(ModelForm):
    """
    Form for loading a new zone map
    """

    class Meta:
        model = ZoneMap
        fields = ['zone', 'map_pdf']
        widgets = {
            'map_pdf': FileInput(),
        }


class ZoneMapDetailForm(ModelForm):
    """
    Form for updating an existing zone map
    """

    class Meta:
        model = ZoneMap
        fields = ['zone', 'year', 'map_pdf']
        widgets = {
            'year': TextInput(attrs={
                'class': "form-control",
                'size': '4',
                'placeholder': 'Year'
            }),
            'map_pdf': FileInput(),
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
                'class': "form-control",
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
                'class': "form-control",
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
        fields = ['event', 'site', 'site_status', 'notes']
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
            'notes': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 750px;',
                'placeholder': 'Notes'
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
            'notes': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 750px;',
                'placeholder': 'Notes'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(EventSiteCreateForm, self).__init__(*args, **kwargs)


class EventSiteListFilterForm(Form):
    """
    Filter form for restricting the  dropdown lists Site Allocation, creation and updating
    """

    event = ModelChoiceField(
        queryset=Event.currenteventfiltermgr.all(),
        empty_label='Show All',
        label='Event',
        required=False,
        widget=Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 300px;',
            'hx-trigger': 'change',
            'hx-post': '.',
            'hx-target': '#event_site_data',
        })
    )
    zone = ModelChoiceField(
        queryset=Zone.objects.all(),
        empty_label='Show All',
        label='Site Zones',
        required=False,
        widget=Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 300px;',
            'hx-trigger': 'change',
            'hx-post': '.',
            'hx-target': '#event_site_data',
        })
    )
    site_status = ChoiceField(
        label='Site Status',
        choices=[
            ('', 'Show All'),
            (1, 'Available'),
            (2, 'Allocated'),
            (3, 'Pending'),
            (4, 'Booked'),
            (5, 'Unavailable'),
            (6, 'Archived')
        ],
        required=False,
        widget=Select(
            attrs={
                'class': 'form-select',
                'style': 'max-width: 300px;',
                'hx-trigger': 'change',
                'hx-post': '.',
                'hx-target': '#event_site_data',
            })
    )
    form_purpose = forms.CharField(widget=forms.HiddenInput(), initial='filter')

    class Meta:
        fields = [
            'event',
            'zone',
            'site_status',
            'notes',
        ]


class InventoryItemFairDetailForm(ModelForm):
    """
    Form for updating an InventoryItemFair
    """

    class Meta:
        model = InventoryItemFair
        fields = ['fair', 'inventory_item', 'price_rate', 'is_percentage', 'price', 'is_refundable']
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
            'is_percentage': CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'price': NumberInput(attrs={
                    'class': "form-control",
                    'style': 'max-width: 100px;',
                    'placeholder': 'Item Price'
                }),
            'is_refundable': CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }


class InventoryItemFairCreateForm(ModelForm):
    """
        Form for Creating a new inventory item fair relationship including setting the item price
    """

    class Meta:
        model = InventoryItemFair
        fields = ['fair', 'inventory_item', 'price_rate', 'is_percentage', 'price', 'is_refundable']
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
            'is_percentage': CheckboxInput(attrs={
                'class': 'form-check-input',
                'checked': False
            }),
            'price': NumberInput(attrs={
                'class': "form-control",
                'style': 'max-width: 100px;',
                'placeholder': 'Item Price'
            }),
            'is_refundable': CheckboxInput(attrs={
                'class': 'form-check-input',
                'checked': True
            }),
        }

    def __init__(self, *args, **kwargs):
        super(InventoryItemFairCreateForm, self).__init__(*args, **kwargs)


class DashboardSiteFilterForm(Form):
    """
    Form for selecting filters for the site dashboard
    """

    event = ModelChoiceField(
        queryset=Event.currenteventfiltermgr.all(),
        empty_label='Show All',
        label='Events',
        required=False,
        widget=Select(attrs={'class': 'form-control'})
    )
    zone = ModelChoiceField(
        queryset=Zone.objects.all(),
        empty_label='Show All',
        label='Site Zones',
        required=False,
        widget=Select(attrs={'class': 'form-control'})
    )
    site_size = ModelChoiceField(
        queryset=InventoryItem.objects.filter(item_type=1),
        empty_label='Show All',
        label='Site Size',
        required=False,
        widget=Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = EventSite
        fields = ['event', 'site']


class PowerBoxCreateForm(ModelForm):
    """
    Form for Creating a new zone
    """

    class Meta:
        model = PowerBox
        fields = ['power_box_name', 'power_box_description', 'socket_count', 'max_load', 'zone']
        widgets = {
            'power_box_name': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Powerbox Name'
            }),
            'power_box_description': Textarea(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Powerbox Description'
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
        fields = ['power_box_name', 'power_box_description', 'socket_count', 'max_load', 'zone']
        widgets = {
            'power_box_name': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Powerbox Name'
            }),
            'power_box_description': Textarea(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Powerbox Description'
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
            'sockets_used': NumberInput(attrs={
                'class': "form-select",
                'style': 'max-width: 300px;',
                'placeholder': 'Count'
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
            'sockets_used': NumberInput(attrs={
                'class': "form-select",
                'style': 'max-width: 300px;',
                'placeholder': 'Count'
            }),
            'power_load': NumberInput(attrs={
                'class': "form-select",
                'style': 'max-width: 300px;',
                'placeholder': 'Kilowatts'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(EventPowerCreateForm, self).__init__(*args, **kwargs)


class LocationCreateForm(ModelForm):
    """
    Form for creating a new location
    """

    class Meta:
        model = Location
        fields = ['location_name', ]
        widgets = {
            'location_name': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 400px;',
                'placeholder': 'Location Name'
            }),
        }

    def clean_location_name(self):
        location_name = self.cleaned_data['location_name']
        if Location.objects.filter(location_name=location_name).exists():
            raise forms.ValidationError("This Location has already been created.")
        return location_name


class LocationUpdateForm(ModelForm):
    """
    Form for updating or amending a location
    """

    class Meta:
        model = Location
        exclude = ()
        widgets = {
            'location_name': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 400px;',
                'placeholder': 'Location Name'
            }),
        }


class SiteAllocationCreateForm(ModelForm):
    """
    Form used to create new site allocations
    """

    event_site = ModelChoiceField(
        queryset=EventSite.site_available,
        empty_label='Please Select',
        label='Event Sites',
        required=False,
        widget=Select(attrs={
            'class': "form-select",
            'style': 'max-width: 300px;',
        })
    )

    class Meta:
        model = SiteAllocation
        fields = ('event_site',)
        widgets = {
            'event_site': Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px;',
            }),

        }

    def __init__(self, *args, **kwargs):
        self.created_by = kwargs.pop('created_by', None)
        super(SiteAllocationCreateForm, self).__init__(*args, **kwargs)


class SiteAllocationUpdateForm(ModelForm):
    """
    Form used to update existing Site Allocations
    """

    class Meta:
        model = SiteAllocation
        fields = ('stallholder', 'event_site', 'stall_registration', 'event_power', 'on_hold')
        widgets = {
            'stallholder': Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px;',
                'readonly': 'readonly'
            }),
            'event_site': Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px;',
            }),
            'stall_registration': Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px;'
            }),
            'event_power': Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px;',
            }),
        }


class SiteAllocationListFilterForm(Form):
    """
    Filter form for restricting the  dropdown lists Site Allocation, creation and updating
    """

    event = ModelChoiceField(
        queryset=Event.currenteventfiltermgr.all(),
        empty_label='Show All',
        label='Event',
        required=False,
        widget=Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 300px;',
            'hx-trigger': 'change',
            'hx-post': '.',
            'hx-target': '#list_data',
        })
    )
    zone = ModelChoiceField(
        queryset=Zone.objects.all(),
        empty_label='Show All',
        label='Site Zones',
        required=False,
        widget=Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 300px;',
            'hx-trigger': 'change',
            'hx-post': '.',
            'hx-target': '#list_data',
        })
    )
    on_hold = BooleanField(
        required=False,
        widget=CheckboxInput(attrs={
            'class': 'form-check-input',
            'hx-trigger': 'change',
            'hx-post': '.',
            'hx-target': '#list_data',
            'checked': False
        })
    )
    form_purpose = forms.CharField(widget=forms.HiddenInput(), initial='filter')

    class Meta:
        fields = [
            'event',
            'zone',
            'on_hold'
        ]


class SiteAllocationFilterForm(Form):
    """
    Filter form for restricting the  dropdown lists Site Allocation, creation and updating
    """

    event = ModelChoiceField(
        queryset=Event.currenteventfiltermgr.all(),
        empty_label='Show All',
        label='Event',
        required=False,
        widget=Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 300px;',
            'hx-trigger': 'change',
            'hx-post': '.',
            'hx-target': '#list_data',
        })
    )
    zone = ModelChoiceField(
        queryset=Zone.objects.all(),
        empty_label='Show All',
        label='Site Zones',
        required=False,
        widget=Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 300px;',
            'hx-trigger': 'change',
            'hx-post': '.',
            'hx-target': '#list_data',
        }),
    )
    site_size = ModelChoiceField(
        queryset=InventoryItem.objects.filter(item_type=1),
        empty_label='Show All',
        label='Site Size',
        required=False,
        widget=Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 300px;',
            'hx-trigger': 'change',
            'hx-post': '.',
            'hx-target': '#list_data',
        })
    )

    form_purpose = forms.CharField(widget=forms.HiddenInput(), initial='filter')

    class Meta:
        fields = [
            'event',
            'zone',
            'site_size',
        ]


class StallHolderIDForm(Form):
    """"
    Form for capturing Stallholder ID  from the Stallholder search function
    """

    stallholder_id = forms.CharField(
        label="Selected Stall holder ID",
        widget=forms.TextInput(attrs={
            'class': "form-control",
            'style': 'max-width: 300px;',
            'required': False,
            'placeholder': 'No Stallholder Selected',
            'readonly': 'readonly'
        }),
    )

class DashboardRegistrationFilterForm(Form):
    """
    Form for selecting filters for the Application dashboard
    """
    fair = ModelChoiceField(
        queryset=Fair.objects.all(),
        empty_label='Show All',
        label='Fairs',
        required=False,
        widget=Select(attrs={'class': 'form-control'})
    )
    site_size = ModelChoiceField(
        queryset=InventoryItem.objects.filter(item_type=1),
        empty_label='Show All',
        label='Site Size',
        required=False,
        widget=Select(attrs={'class': 'form-control'})
    )


class MessageFilterForm(Form):
    """
    Filter form to enable historical and archived comments to be viewed
    """
    fair = ModelChoiceField(
        queryset=Fair.objects.all(),
        required=False,
        label = 'Select Fairs',
        widget=Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 300px;',
            'hx-trigger': 'change',
            'hx-post': '.',
            'hx-target': '#message_data',
        })
    )
    comment_type = ModelChoiceField(
        queryset=CommentType.objects.all(),
        required=False,
        label = 'Select Message Type',
        widget=Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 300px;',
            'hx-trigger': 'change',
            'hx-post': '.',
            'hx-target': '#message_data',
        })
    )
    is_active = BooleanField(
        required=False,
        label = 'Show messages under action',
        widget=CheckboxInput(attrs={
            'class': 'form-check-input',
            'hx-trigger': 'change',
            'hx-post': '.',
            'hx-target': '#message_data',
            'checked': False
        })
    )
    is_done = BooleanField(
        required=False,
        label = 'Show messages that have been resolved',
        widget=CheckboxInput(attrs={
            'class': 'form-check-input',
            'hx-trigger': 'change',
            'hx-post': '.',
            'hx-target': '#message_data',
            'checked': False
        })
    )
    is_archived = BooleanField(
        required=False,
        label = 'Show Archived Comments',
        widget=CheckboxInput(attrs={
            'class': 'form-check-input',
            'hx-trigger': 'change',
            'hx-post': '.',
            'hx-target': '#message_data',
            'checked': False
        })
    )

    class Meta:
        fields = [
            'fair',
            'comment_type',
            'is_active',
            'is_done',
            'is_archived',
        ]


class MessageReplyForm(ModelForm):
    """
    Form for capturing replies to comments typically associated with stall Application
    """
    convener_only_comment = BooleanField(
        required=False,
        label="Convener Only Note",
        widget=forms.CheckboxInput(attrs={
            'class': "form-check-input",
            'checked': False,
        })
    )

    class Meta:
        model = RegistrationComment
        fields = (
            'convener_only_comment',
            'comment'
        )
        labels = {
            'convener_only_comment' : 'Reply or convener note',
        }
        widgets = {
            'comment': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 400px;',
                'placeholder': 'Detail your reply or note'
            }),
        }

class SiteHistoryFilerForm(Form):

    zone = ModelChoiceField(
        queryset=Zone.objects.all(),
        empty_label='Show All',
        label='Site Zones',
        required=False,
        widget=Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 300px;',
            'hx-trigger': 'change',
            'hx-post': '.',
            'hx-target': '#site_history_data',
        }),
    )
    class Meta:
        fields = [
            'zone',
        ]

class SiteAllocationFilerForm(Form):

    event = ModelChoiceField(
        queryset=Event.currenteventfiltermgr.all(),
        empty_label='Show All',
        label='Event',
        required=False,
        widget=Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 300px;',
            'hx-trigger': 'change',
            'hx-post': '.',
            'hx-target': '#site_allocation_data',
        })
    )
    zone = ModelChoiceField(
        queryset=Zone.objects.all(),
        empty_label='Show All',
        label='Site Zones',
        required=False,
        widget=Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 300px;',
            'hx-trigger': 'change',
            'hx-post': '.',
            'hx-target': '#site_allocation_data',
        }),
    )
    site_size = ModelChoiceField(
        queryset=InventoryItem.objects.filter(item_type=1),
        empty_label='Show All',
        label='Site Size',
        required=False,
        widget=Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 300px;',
            'hx-trigger': 'change',
            'hx-post': '.',
            'hx-target': '#site_allocation_data',
        })
    )
    class Meta:
        fields = [
            'zone',
            'event',
            'site_size'
        ]

