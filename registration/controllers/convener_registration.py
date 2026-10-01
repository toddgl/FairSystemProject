# registration/controllers/convener_registration.py

import decimal

from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404

from django_fsm import can_proceed

from registration.models import (
    StallRegistration,
    FoodRegistration,
    AdditionalSiteRequirement,
    FoodPrepEquipReq,
    RegistrationComment,
)

from payment.models import (
    DiscountItem
)
from foodlicence.models import (
    FoodLicence
)

from registration.services.billing import (
    RegistrationBillingService,
)

from registration.forms import (
    StallRegistrtionConvenerEditForm,
    FoodRegistrationConvenerEditForm,
    CommentFilterForm,
    RegistrationCommentForm,
    CommentReplyForm,
    RegistrationDiscountForm,
    AdditionalSiteReqForm,
)

from accounts.models import Profile

from emails.backend import (
    single_registration_email,
)

from emails.forms import (
    CreateStallholderEmailForm,
)

from payment.models import PaymentHistory

from fairs.models import Fair


class ConvenerRegistrationController:

    # ==================================================
    # INITIALISATION
    # ==================================================

    def __init__(self, request, registration_id):

        self.request = request

        self.registration = get_object_or_404(
            StallRegistration,
            id=registration_id
        )

        self.current_fair = (
            Fair.currentfairmgr.all().last()
        )

    # ==================================================
    # STALLHOLDER
    # ==================================================

    def build_stallholder_detail(self):

        self.request.session["stallholder_id"] = (
            self.registration.stallholder.id
        )

        return Profile.objects.get(
            user=self.registration.stallholder
        )

    # ==================================================
    # COMMENTS
    # ==================================================

    def build_comments(self):

        return RegistrationComment.objects.filter(
            stallholder=self.registration.stallholder.id,
            is_archived=False,
            convener_only_comment=False,
            comment_parent__isnull=True,
            fair=self.current_fair.id,
        )

    def build_comment_forms(self):

        return {
            "commentfilterform": CommentFilterForm(
                self.request.POST or None
            ),

            "commentform": RegistrationCommentForm(
                self.request.POST or None
            ),

            "replyform": CommentReplyForm(
                self.request.POST or None
            ),
        }

    # ==================================================
    # PAYMENT HISTORY
    # ==================================================

    def build_payment_history(self):

        return (
            PaymentHistory.paymenthistorycurrentmgr
            .get_stallholder_payment_history(
                stallholder=self.registration.stallholder.id
            )
        )

    # ==================================================
    # FOOD REGISTRATION
    # ==================================================

    def build_food_data(self):

        try:

            return FoodRegistration.objects.get(
                registration=self.registration
            )

        except FoodRegistration.DoesNotExist:

            return None

    def build_food_form(self, post_data=False):
        """
        Build the food registration form.

        post_data=False:
            Return an unbound form for the existing
            FoodRegistration.

        post_data=True:
            Return a bound form using POST/FILES data.

        Returns None if this registration has no
        FoodRegistration.
        """

        try:

            food_registration = (
                FoodRegistration.objects.get(
                    registration=self.registration
                )
            )

        except FoodRegistration.DoesNotExist:

            return None

        if post_data:

            return FoodRegistrationConvenerEditForm(
                self.request.POST,
                self.request.FILES,
                instance=food_registration,
            )

        return FoodRegistrationConvenerEditForm(
            instance=food_registration
        )

    def build_food_equipment(
        self,
        food_registration
    ):

        if not food_registration:

            return FoodPrepEquipReq.objects.none()

        return FoodPrepEquipReq.objects.filter(
            food_registration=food_registration
        )

    def build_food_licence(
        self,
        food_registration
    ):

        if not food_registration:

            return None

        return FoodLicence.objects.filter(
            food_registration=food_registration
        ).first()

    # ==================================================
    # EMAIL
    # ==================================================

    def build_email_form(self):

        return CreateStallholderEmailForm(
            self.request.POST or None
        )

    # ==================================================
    # DISCOUNTS
    # ==================================================

    def build_discount_data(self):

        discounts = DiscountItem.objects.filter(
            stall_registration=self.registration
        )

        if discounts:

            total_discount = sum(
                discounts.values_list(
                    "discount_amount",
                    flat=True
                )
            )

        else:

            total_discount = decimal.Decimal(
                "0.00"
            )

        return discounts, total_discount

    def build_discount_form(self):

        return RegistrationDiscountForm(
            self.request.POST or None
        )

    # ==================================================
    # ADDITIONAL SITES
    # ==================================================

    def build_additional_sites(self):

        return AdditionalSiteRequirement.objects.filter(
            stall_registration=self.registration
        )

    def build_additional_site_form(self):

        return AdditionalSiteReqForm(
            self.request.POST or None
        )

    # ==================================================
    # CONTEXT
    # ==================================================

    def get_context(
        self,
        form=None,
        foodregistrationform=None,
        billing=None,
        createstallholderemailform=None,
        applydiscountform=None,
        additionalsiteform=None,
    ):
        """
        Build the complete context required by the
        convener stall registration detail template.

        Optional form arguments allow us to return a
        bound form containing validation errors.
        """

        # ----------------------------------------------
        # Registration form
        # ----------------------------------------------

        if form is None:

            form = StallRegistrtionConvenerEditForm(
                instance=self.registration
            )

        # ----------------------------------------------
        # Food registration form
        # ----------------------------------------------

        if foodregistrationform is None:

            foodregistrationform = (
                self.build_food_form()
            )

        # ----------------------------------------------
        # Email form
        # ----------------------------------------------

        if createstallholderemailform is None:

            createstallholderemailform = (
                self.build_email_form()
            )

        # ----------------------------------------------
        # Discount form
        # ----------------------------------------------

        if applydiscountform is None:

            applydiscountform = (
                self.build_discount_form()
            )

        # ----------------------------------------------
        # Additional site form
        # ----------------------------------------------

        if additionalsiteform is None:

            additionalsiteform = (
                self.build_additional_site_form()
            )

        # ----------------------------------------------
        # Data
        # ----------------------------------------------

        payment_histories = (
            self.build_payment_history()
        )

        food_registration = (
            self.build_food_data()
        )

        stallholder_detail = (
            self.build_stallholder_detail()
        )

        comments = (
            self.build_comments()
        )

        comment_forms = (
            self.build_comment_forms()
        )

        discounts, total_discount = (
            self.build_discount_data()
        )

        additional_sites = (
            self.build_additional_sites()
        )

        equipment_list = (
            self.build_food_equipment(
                food_registration
            )
        )

        foodlicence_data = (
            self.build_food_licence(
                food_registration
            )
        )

        # ----------------------------------------------
        # Complete context
        # ----------------------------------------------

        context = {

            # Registration
            "stall_registration":
                self.registration,

            "registrationform":
                form,

            "billing":
                billing,

            # Payment
            "payment_histories":
                payment_histories,

            # Food
            "foodregistrationupdateform":
                foodregistrationform,

            "food_data":
                food_registration,

            "equipment_list":
                equipment_list,

            "foodlicence_data":
                foodlicence_data,

            # Stallholder
            "stallholder_detail":
                stallholder_detail,

            # Comments
            "commentfilterform":
                comment_forms[
                    "commentfilterform"
                ],

            "comments":
                comments,

            "commentform":
                comment_forms[
                    "commentform"
                ],

            "replyform":
                comment_forms[
                    "replyform"
                ],

            "comment_filter":
                "Showing current comments "
                "of the current fair",

            # Email
            "createstallholderemailform":
                createstallholderemailform,

            # Discounts
            "applydiscountform":
                applydiscountform,

            "discounts":
                discounts,

            "total_discount":
                total_discount,

            # Additional sites
            "site_requirement_list":
                additional_sites,

            "additionalsiteform":
                additionalsiteform,
        }

        # The existing template uses this separately
        # when the registration is multi-site.
        if self.registration.multi_site:

            context["additional_sites"] = (
                additional_sites
            )

        return context

    # ==================================================
    # DISPATCH
    # ==================================================

    def dispatch(self):

        # ----------------------------------------------
        # POST requests
        # ----------------------------------------------

        if self.request.method == "POST":

            # Registration / food update
            if "update" in self.request.POST:

                return self.handle_post()

            # Discount
            if "discount" in self.request.POST:

                return self.handle_discount()

            # Email
            if "stallholderemail" in self.request.POST:

                return self.handle_email()

        # ----------------------------------------------
        # HTMX requests
        # ----------------------------------------------

        if self.request.htmx:

            return self.handle_htmx()

        # ----------------------------------------------
        # Normal GET
        # ----------------------------------------------

        return self.render()

    # ==================================================
    # EMAIL
    # ==================================================

    def handle_email(self):

        form = CreateStallholderEmailForm(
            self.request.POST
        )

        # ----------------------------------------------
        # Validation failure
        # ----------------------------------------------

        if not form.is_valid():

            return self.render(
                createstallholderemailform=form
            )

        # ----------------------------------------------
        # Email data
        # ----------------------------------------------

        subject_type = (
            form.cleaned_data[
                "subject_type"
            ]
        )

        body = (
            form.cleaned_data[
                "body"
            ]
        )

        subject = (
            f"Martinborough Fair "
            f"{self.registration.fair.fair_year} - "
            f"{subject_type}"
        )

        stallholder_detail = (
            self.build_stallholder_detail()
        )

        recipient = (
            stallholder_detail.user.email
        )

        # ----------------------------------------------
        # Send email
        # ----------------------------------------------

        single_registration_email(
            self.registration.stallholder.id,
            subject_type,
            recipient,
            subject,
            body,
        )

        # ----------------------------------------------
        # Refresh complete detail page
        # ----------------------------------------------

        response = HttpResponse()

        response["HX-Refresh"] = "true"

        return response

    # ==================================================
    # DISCOUNT
    # ==================================================

    def handle_discount(self):

        form = RegistrationDiscountForm(
            self.request.POST
        )

        # ----------------------------------------------
        # Validation failure
        # ----------------------------------------------

        if not form.is_valid():

            return self.render(
                applydiscountform=form
            )

        # ----------------------------------------------
        # Create discount
        # ----------------------------------------------

        discount = form.save(
            commit=False
        )

        discount.stall_registration = (
            self.registration
        )

        discount.created_by = (
            self.request.user
        )

        discount.save()

        # ----------------------------------------------
        # Registration is no longer invoiced
        # ----------------------------------------------

        self.registration.is_invoiced = False

        self.registration.save()

        # ----------------------------------------------
        # Return registration to amended status
        # ----------------------------------------------

        if can_proceed(
            self.registration
            .to_booking_status_amended
        ):

            self.registration.to_booking_status_amended()

            self.registration.save()

        # ----------------------------------------------
        # Refresh complete detail page
        # ----------------------------------------------

        response = HttpResponse()

        response["HX-Refresh"] = "true"

        return response

    # ==================================================
    # HTMX LIVE FORM PROCESSING
    # ==================================================

    def handle_htmx(self):

        form = StallRegistrtionConvenerEditForm(
            self.request.POST,
            self.request.FILES,
            instance=self.registration,
        )

        food_form = (
            self.build_food_form(
                post_data=True
            )
        )

        billing = None

        # ----------------------------------------------
        # Calculate billing preview
        # ----------------------------------------------

        if form.is_valid():

            preview = (
                form.build_registration_preview()
            )

            billing = (
                RegistrationBillingService(
                    preview.fair
                ).calculate(
                    preview
                )
            )

        # ----------------------------------------------
        # Return dynamic form
        # ----------------------------------------------

        return self.render_partial(
            form,
            billing,
            food_form
        )

    # ==================================================
    # SAVE REGISTRATION
    # ==================================================

    def handle_post(self):

        form = StallRegistrtionConvenerEditForm(
            self.request.POST,
            self.request.FILES,
            instance=self.registration,
        )

        food_form = (
            self.build_food_form(
                post_data=True
            )
        )

        # ----------------------------------------------
        # Registration validation
        # ----------------------------------------------

        if not form.is_valid():

            return self.render_partial(
                form,
                None,
                food_form
            )

        # ----------------------------------------------
        # Save registration
        # ----------------------------------------------

        registration = form.save(
            commit=False
        )

        # ----------------------------------------------
        # FSM transition
        # ----------------------------------------------

        try:

            registration.to_booking_status_amended()

        except Exception as e:

            print(
                f"Transition failed: {e}"
            )

        # ----------------------------------------------
        # Save registration and M2M data
        # ----------------------------------------------

        registration.save()

        form.save_m2m()

        # ----------------------------------------------
        # Save food registration
        # ----------------------------------------------

        if food_form:

            if food_form.is_valid():

                food_form.save()

            else:

                return self.render_partial(
                    form,
                    None,
                    food_form
                )

        # ----------------------------------------------
        # Refresh complete detail page
        # ----------------------------------------------

        response = HttpResponse()

        response["HX-Refresh"] = "true"

        return response

    # ==================================================
    # FULL DETAIL PAGE
    # ==================================================

    def render(self, **kwargs):

        context = self.get_context()

        context.update(kwargs)

        return TemplateResponse(
            self.request,
            "stallregistration/"
            "convener_stall_registration_detail.html",
            context,
        )

    # ==================================================
    # HTMX DYNAMIC PARTIAL
    # ==================================================

    def render_partial(
        self,
        form,
        billing,
        food_form=None,
    ):

        return TemplateResponse(
            self.request,
            "stallregistration/"
            "convener_stallregistration_dynamic.html",
            self.get_context(
                form=form,
                billing=billing,
                foodregistrationform=food_form,
            ),
        )
