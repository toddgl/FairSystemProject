# registration/models.py

import datetime
from django.db.models import Q
from django.conf import settings  # new
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_fsm import FSMField, transition

from fairs.models import (
    Fair,
    Event,
    InventoryItem
)

import magic

PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]

# Global Variables
current_year = datetime.datetime.now().year
next_year = current_year + 1


class FoodPrepEquipment(models.Model):
    """
    Description: A reference table for storing electrical food preparation equipment and the electrical load that
    each will place on the fair electrical network
    """
    equipment_name = models.CharField(max_length=40)
    power_load_maximum = models.DecimalField(max_digits=10, decimal_places=2)
    power_load_minimum = models.DecimalField(max_digits=10, decimal_places=2)
    power_load_factor = models.DecimalField(max_digits=3, decimal_places=0, default=70, validators=PERCENTAGE_VALIDATOR)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='food_prep_equipment_created_by',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='food_prep_equipment_updated_by',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.equipment_name

    class Meta:
        verbose_name_plural = "FoodPrepEquipments"


class FoodSaleType(models.Model):
    """
    Description; Model that holds the definition of the various food sale types
    """
    food_sale_type = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='food_stall_type_created_by',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='food_stall_type_updated_by',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.food_sale_type

    class Meta:
        verbose_name_plural = "FoodStallTypes"


class StallCategory(models.Model):
    """
    Description: Model that holds the definition of Stall Categories
    """
    category_name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    has_inventory_item = models.BooleanField(default=False)
    inventory_item = models.ForeignKey(
        InventoryItem,
        related_name='category_inventory_item',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='stall_category_created_by',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='stall_category_updated_by',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name_plural = "StallCategories"


# StallRegistration Managers

class RegistrationCurrentAllManager(models.Manager):
    """
    Queryset of Stall Registrations for current Fairs
    """

    def get_queryset(self):
        return super().get_queryset().filter(fair__fair_year__in=[current_year, next_year],
                                             fair__is_activated=True)


class RegistrationCurrentManager(models.Manager):
    """
    Queryset of Stall Registrations for current Fairs excluded cancelled stall registrations
    """

    def get_queryset(self):
        return super().get_queryset().filter(fair__fair_year__in=[current_year, next_year],
                                             fair__is_activated=True).exclude(is_cancelled=True)


class RegistrationSellingFoodManager(models.Manager):
    """
    Queryset of Stall Registrations for current fairs that are selling food
    """

    def get_queryset(self):
        return super().get_queryset().filter(fair__fair_year__in=[current_year, next_year],
                                             fair__is_activated=True, selling_food=True)


class RegistrationCreatedManager(models.Manager):
    """
    Queryset of Stall Registrations for current fairs that the booking status is created
    """

    def get_queryset(self):
        return super().get_queryset().filter(fair__fair_year__in=[current_year, next_year],
                                             fair__is_activated=True, booking_status='Created')


class RegistrationSubmittedManager(models.Manager):
    """
    Queryset of Stall Registrations for current fairs that the booking status is submitted
    """

    def get_queryset(self):
        return super().get_queryset().filter(fair__fair_year__in=[current_year, next_year],
                                             fair__is_activated=True, booking_status='Submitted')


class RegistrationInvoicedManager(models.Manager):
    """
    Queryset of Stall Registrations for current fairs that the booking status is invoiced
    """

    def get_queryset(self):
        return super().get_queryset().filter(fair__fair_year__in=[current_year, next_year],
                                             fair__is_activated=True, booking_status='Invoiced')


class RegistrationBookedManager(models.Manager):
    """
    Queryset of Stall Registrations for current fairs that the booking status is booked
    """

    def get_queryset(self):
        return super().get_queryset().filter(fair__fair_year__in=[current_year, next_year],
                                             fair__is_activated=True, booking_status='Booked')


class RegistrationCancelledManager(models.Manager):
    """
    Queryset of Stall Registrations for current fairs that the booking status is cancelled
    """

    def get_queryset(self):
        return super().get_queryset().filter(fair__fair_year__in=[current_year, next_year],
                                             fair__is_activated=True, booking_status='Cancelled')


class VehiclesOnSiteManager(models.Manager):
    """
    Queryset of StallRegistration for current fairs and the specified stallholder that that has inddicated that they
    have a vehicle on site and that it sze has been defined and it is not over 6 metres in length and an image of the
    vehicle has been uploaded.  Used to determine if the Stallregistration can be submitted for payment use something
    like to get ta True / False response has_size = StallRegistration.vehicleonsitemgr.has_size(registration_id)
    not_oversize = StallRegistration.vehicleonsitemgr.not_oversize(registration_id) has_image =
    StallRegistration.vehicleonsitemgr.has_image(registration_id)
    """

    def get_queryset(self):
        current_fair = Fair.currentfairmgr.all().last()
        return super().get_queryset().filter(fair=current_fair.id, vehicle_on_site=True)

    def has_size(self, registration_id):
        return self.get_queryset().filter(id=registration_id, vehicle_length__gt=0).exists()

    def not_oversize(self, registration_id):
        return self.get_queryset().filter(id=registration_id, vehicle_length__lte=6).exists()

    def has_image(self, registration_id):
        return self.get_queryset().filter(id=registration_id, vehicle_image__isnull=False).exists()


class IsMultiSiteRegistrationManager(models.Manager):
    """
    Queryset of Stall Application  for current fairs and the specified stall application that
    is a multisite request.  Used to determine if the Stallregistration can be submitted for payment
    use something like to get ta True ? False response
    is_multi_site = StallRegistration.ismultisiteregistrationmgr.filter_by_stallregistration(stallregistration_id)
    """

    def get_queryset(self):
        current_fair = Fair.currentfairmgr.all().last()
        return super().get_queryset().filter(fair=current_fair.id, multi_site=True)

    def filter_by_stallregistration(self, stallregistration_id):
        return self.get_queryset().filter(stallholder=stallregistration_id).exists()


class StallRegistration(models.Model):
    """
    Description: Model to capture stall registrations
    """
    CREATED = 'Created'
    SUBMITTED = 'Submitted'
    INVOICED = 'Invoiced'
    PAYMENTCOMPLETED = 'Payment Completed'
    ALLOCATIONREVIEW = 'Allocation Review'
    ALLOCATIONPENDING = 'Allocation Pending'
    ALLOCATIONAPPROVED = 'Allocation Approved'
    ALLOCATIONCANCELLED = 'Allocation Cancelled'
    REFUNDREVIEW = 'Refund Review'
    REFUNDDONATED = 'Refund Donated'
    REFUNDREJECTED = 'Refund Rejected'
    REFUNDAPPROVED = 'Refund Approved'
    BOOKED = 'Booked'
    CANCELLED = 'Cancelled'

    REGISTRATION_STATUS_CHOICES = [
        (CREATED, _('Created')),
        (SUBMITTED, _('Submitted')),
        (INVOICED, _('Invoiced')),
        (PAYMENTCOMPLETED, _('Payment Completed')),
        (ALLOCATIONREVIEW, _('Allocation Review')),
        (ALLOCATIONPENDING, _('Allocation Pending')),
        (ALLOCATIONAPPROVED, _('Allocation Approved')),
        (ALLOCATIONCANCELLED, _('Allocation Rejected')),
        (REFUNDREVIEW, _('Refund Review')),
        (REFUNDDONATED, _('Refund Donated')),
        (REFUNDREJECTED, _('Refund Rejected')),
        (REFUNDAPPROVED, _('Refund Approved')),
        (BOOKED, _('Booked')),
        (CANCELLED, _('Cancelled')),
    ]
    booking_status = FSMField(
        default=CREATED,
        verbose_name='Registration State',
        choices=REGISTRATION_STATUS_CHOICES,
        protected=False,
    )
    fair = models.ForeignKey(Fair, on_delete=models.CASCADE)
    stallholder = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # new
        on_delete=models.CASCADE
    )
    stall_manager_name = models.CharField(max_length=150)
    manager_vehicle_registration = models.CharField(null=True, blank=True, max_length=7)
    stall_category = models.ForeignKey(
        StallCategory,
        related_name='stall_registrations',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    stall_description = models.TextField()
    products_on_site = models.TextField()
    site_size = models.ForeignKey(
        InventoryItem,
        related_name='site_size_requirement',
        on_delete=models.SET_NULL,
        null=True
    )
    trestle_required = models.BooleanField(default=False)
    trestle_quantity = models.IntegerField(default=0)
    stall_shelter = models.TextField(null=True, blank=True)
    power_required = models.BooleanField(default=False)
    total_charge = models.DecimalField(max_digits=8, decimal_places=2)
    selling_food = models.BooleanField(default=False)
    vehicle_on_site = models.BooleanField(default=False)
    vehicle_width = models.FloatField(default=0)
    vehicle_length = models.FloatField(default=0)
    vehicle_image = models.ImageField(blank=True, null=True, upload_to='vehicles/' + str(current_year))
    multi_site = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    is_invoiced = models.BooleanField(default=False)

    objects = models.Manager()
    registrationcurrentallmgr = RegistrationCurrentAllManager()
    registrationcurrentmgr = RegistrationCurrentManager()
    sellingfoodmgr = RegistrationSellingFoodManager()
    registrationcreatedmgr = RegistrationCreatedManager()
    registrationsubmittedmgr = RegistrationSubmittedManager()
    registrationinvoicedmgr = RegistrationInvoicedManager()
    registrationbookedmgr = RegistrationBookedManager()
    registrationcancelledmgr = RegistrationCancelledManager()
    vehicleonsitemgr = VehiclesOnSiteManager()
    ismultisiteregistrationmgr = IsMultiSiteRegistrationManager()

    class Meta:
        verbose_name = "stallregistration"
        verbose_name_plural = "stallregistrations"

    def __str__(self):
        return str(self.booking_id)

    def get_absolute_url(self):
        return reverse('stallregistration-detail', args=[str(self.id)])

    @property
    def booking_id(self):
        return self.id

    def save(self, *args, **kwargs):
        # Identify whether a new file has been uploaded
        if self.vehicle_image:
            # Delete existing file
            try:
                this = StallRegistration.objects.get(id=self.id)
                if this.vehicle_image != self.vehicle_image:
                    this.vehicle_image.delete()
            except:
                pass
        super(StallRegistration, self).save(*args, **kwargs)

    @transition(field=booking_status, source="Created", target="Cancelled")
    def to_booking_status_cancelled(self):
        pass

    @transition(field=booking_status, source="Created", target="Submitted")
    def to_booking_status_submitted(self):
        pass

    @transition(field=booking_status, source=["Created", "Submitted", "Payment Completed", "Booked"], target="Invoiced")
    def to_booking_status_invoiced(self):
        pass

    @transition(field=booking_status, source=["Invoiced"], target="Payment Completed")
    def to_booking_status_payment_completed(self):
        pass

    @transition(field=booking_status, source=["Payment Completed"], target="Booked")
    def to_booking_status_booked(self):
        pass

    @transition(field=booking_status, source=["Submitted", "Invoiced", "Payment Completed"], target="Cancelled")
    def to_booking_status_cancelled(self):
        pass

    @transition(field=booking_status, source=["Cancelled"], target="Refund Review")
    def to_booking_status_payment_refund_review(self):
        pass

    @transition(field=booking_status, source=["Cancelled", "Refund Review"], target="Refund Donated")
    def to_booking_status_payment_refund_donated(self):
        pass

    @transition(field=booking_status, source=["Refund Review"], target="Refund Rejected")
    def to_booking_status_payment_refund_rejected(self):
        pass

    @transition(field=booking_status, source=["Refund Review"], target="Refund Approved")
    def to_booking_status_payment_refund_approved(self):
        pass


class CommentType(models.Model):
    """
    Description of a Model to set Comment Types these types are used to make it easier for the Convener
    to identify comments for action, e.g. Site move request
    """
    type_name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.type_name

    class Meta:
        # sort comments in alphabetical order by default
        ordering = ('type_name',)
        verbose_name_plural = "CommentTypes"


class HasUnactionedCommentsManager(models.Manager):
    """
    Queryset of Application comments for current fairs and the specified stallholder that has unactioned comments.
    Used to determine if the Stallregistration can be submitted for payment use something like to get ta True ? False
    response has_unactioned_comments = RegistrationComment.hasunactionedcommentsmgr.filter_by_stallholder(
    stallholder_id).exists()
    """

    def get_queryset(self):
        current_fair = Fair.currentfairmgr.all().last()
        return super().get_queryset().filter(fair=current_fair.id, is_done=False)

    def filter_by_stallholder(self, stallholder_id):
        return self.get_queryset().filter(stallholder=stallholder_id)


class CreateRegistrationCommentManager(models.Manager):
    """
    Used to create a comment to advise the Stall holder if there are any issues with their efforts to submit
    a stall application for payment.
    """

    def create_comment(self, stallholder, current_fair, comment_type, comment, is_done=False):
        obj = RegistrationComment.objects.create(stallholder=stallholder, fair=current_fair,
                                                 comment_type=comment_type, comment=comment, is_done=is_done)
        return obj


class RegistrationComment(models.Model):
    """
    Description a model to capture stallholder and convener comments related to a Stall Application instance.
    Convener comments can be made private so cannot be seen by Stallholders if required
    """
    stallholder = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # new
        null=True,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    comment_type = models.ForeignKey(
        CommentType,
        on_delete=models.CASCADE,
        null=True,
        related_name='comment_types'
    )
    comment = models.TextField(null=True)
    convener_only_comment = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='registration_comment_created_by',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    comment_parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    fair = models.ForeignKey(Fair, on_delete=models.CASCADE)
    is_done = models.BooleanField(default=False)
    objects = models.Manager()
    hasunactionedcommentsmgr = HasUnactionedCommentsManager()
    createregistrationcommentmgr = CreateRegistrationCommentManager()

    class Meta:
        # sort comments in chronological order by default
        ordering = ('date_created',)

    def __str__(self):
        return 'Comment by {}'.format(str(self.created_by))


class CertificateValidityManager(models.Manager):

    def get_queryset(self):
        current_fair = Fair.currentfairmgr.all().last()
        return super().get_queryset().filter(registration__fair=current_fair.id)

    def has_certificate(self, registration_id):
        return self.get_queryset().filter(registration=registration_id,
                                          food_registration_certificate__isnull=False).exists()

    def not_expiring(self, registration_id):
        current_event = Event.currenteventfiltermgr.all().last()
        food_registration = self.get_queryset().filter(registration=registration_id)
        if current_event.postponement_event_date:
            return food_registration.filter(certificate_expiry_date__gt=current_event.postponement_event_date).exists()
        else:
            return food_registration.filter(certificate_expiry_date__gt=current_event.original_event_date).exists()


class FoodRegistration(models.Model):
    """
    Description: An extension of the StallRegistration model that captures via and one-to-one relationship the details
    regarding the food preparation / sale that is needed for the food licence application.
    """
    registration = models.OneToOneField(
        StallRegistration,
        related_name='food_registration',
        on_delete=models.CASCADE,
    )
    food_display_method = models.TextField(blank=True, null=True)
    has_food_certificate = models.BooleanField(null=True, default=False)
    food_registration_certificate = models.FileField(blank=True, null=True,
                                                     upload_to='food_certificates/' + str(current_year))
    certificate_expiry_date = models.DateField(blank=True, null=True)
    food_fair_consumed = models.BooleanField(null=True, default=False)
    food_prep_equipment = models.ManyToManyField(
        FoodPrepEquipment,
        related_name='food_registration',
        through='FoodPrepEquipReq',
        blank=True,
    )
    food_stall_type = models.ForeignKey(
        FoodSaleType,
        related_name='food_registration',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    food_source = models.TextField(blank=True, null=True)
    food_storage_prep = models.TextField(blank=True, null=True)
    has_food_prep = models.BooleanField(blank=True, null=True)
    food_storage_prep_method = models.TextField(blank=True, null=True)
    hygiene_methods = models.TextField(blank=True, null=True)
    is_valid = models.BooleanField(blank=True, null=True)
    cert_filetype = models.CharField(default="image", blank=True, null=True, max_length=50)
    objects = models.Manager()
    certificatevaliditymgr = CertificateValidityManager()

    class Meta:
        verbose_name = "foodregistration"
        verbose_name_plural = "foodregistrations"

    @property
    def title(self):
        return self.name

    def get_absolute_url(self):
        return reverse("registration:food-registration", kwargs={"id": self.id})

    def get_edit_url(self):
        return reverse("registration:foodregistration-update", kwargs={"id": self.id})

    def get_delete_url(self):
        return reverse("registration:foodregistration-delete", kwargs={"id": self.id})

    def get_equipment_children(self):
        return self.foodprepequiprequired_set.all()

    def save(self, *args, **kwargs):
        # Identify whether the certificated uploaded is an image or pdf
        if self.food_registration_certificate:
            # Delete existing file
            try:
                this = FoodRegistration.objects.get(id=self.id)
                if this.food_registration_certificate != self.food_registration_certificate:
                    this.food_registration_certificate.delete()
            except:
                pass
            cert_file = self.food_registration_certificate.read(1000)
            self.food_registration_certificate.seek(0)
            mime = magic.from_buffer(cert_file, mime=True)
            if "pdf" in mime:
                self.cert_filetype = "pdf"
        super(FoodRegistration, self).save(*args, **kwargs)


class AdditionalSiteRequirementManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().all()

    def filter_by_stallregistration(self, stallregistration):
        return self.get_queryset().filter(stall_registration=stallregistration)


class AdditionalSiteRequirement(models.Model):
    """
    Description of a StallRegistration related table that can be used to store additional site requirements
    over and above the single site that is automatically associiated with the registration
    """
    JOINED = "1"
    SEPARATE = "2"

    LOCATION_CHOICE = [
        (JOINED, _('Joined')),
        (SEPARATE, _('Separate'))
    ]

    stall_registration = models.ForeignKey(
        StallRegistration,
        on_delete=models.CASCADE,
        verbose_name='AdditionalSitesRequired',
        related_name='additional_sites_required',
        blank=True,
        null=True
    )
    site_size = models.ForeignKey(
        InventoryItem,
        related_name='Additional_site_size_requirement',
        on_delete=models.SET_NULL,
        null=True
    )
    location_choice = models.CharField(
        choices=LOCATION_CHOICE,
        max_length=11,
        default=JOINED,
    )
    site_quantity = models.IntegerField(default=1)
    objects = models.Manager()
    additionalsiterequirementmgr = AdditionalSiteRequirementManager()

    class Meta:
        verbose_name = "addiitionalsiterequired"
        verbose_name_plural = "addiitionalsiterequirements"

    def get_absolute_url(self):
        return self.stall_registration.get_absolute_url()

    def get_delete_url(self):
        kwargs = {
            "parent_id": self.stall_registration.id,
            "id": self.id
        }
        return reverse("registration:remove-site", kwargs=kwargs)


class FoodPrepEquipReq(models.Model):
    """
    Description a junction table joining FoodRegistration with FoodPrepEquipment used to capture whether the equipment
    the stallholder is using is gas or electrical powered.  The electrical equipment count will be used to calculate the
    likely load on teh Fairs electrical network
    """
    ELECTRICAL = "1"
    GAS = "2"

    POWERED_CHOICE = [
        (ELECTRICAL, _('Electric Powered')),
        (GAS, _('Gas Powered'))
    ]
    food_registration = models.ForeignKey(
        FoodRegistration,
        on_delete=models.CASCADE,
        verbose_name='FoodPrepEquipmentRequired',
        related_name='food_prep_equip_req',
        blank=True,
        null=True
    )
    food_prep_equipment = models.ForeignKey(
        FoodPrepEquipment,
        on_delete=models.CASCADE,
        verbose_name='FoodPrepEquipment',
        related_name='food_prep_equip',
        blank=True,
        null=True
    )
    how_powered = models.CharField(
        choices=POWERED_CHOICE,
        max_length=11,
        default=ELECTRICAL,
    )
    equipment_quantity = models.IntegerField(default=1)

    class Meta:
        verbose_name = "foodprepequiprequired"
        verbose_name_plural = "foodprepequiprequirements"

    def get_absolute_url(self):
        return self.food_registration.get_absolute_url()

    def get_delete_url(self):
        kwargs = {
            "parent_id": self.food_registration.id,
            "id": self.id
        }
        return reverse("registration:remove-equipment", kwargs=kwargs)


@receiver(post_save, sender=StallRegistration)
def create_food_registration(sender, instance, created, **kwargs):
    if created and instance.selling_food:
        FoodRegistration.objects.create(registration=instance)


@receiver(pre_save, sender=StallRegistration)
def remove_food_registration(sender, instance, **kwargs):
    if instance.pk:
        original_instance = StallRegistration.objects.get(pk=instance.pk)
        if not original_instance.selling_food and instance.selling_food:
            FoodRegistration.objects.create(registration=instance)
        elif original_instance.selling_food and not instance.selling_food:
            FoodRegistration.objects.filter(registration=instance).delete()
