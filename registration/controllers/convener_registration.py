# registration/controllers/convener_registration.py

from django.template.response import TemplateResponse, HttpResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404

from registration.models import StallRegistration, FoodRegistration
from registration.services.billing import RegistrationBillingService

from registration.forms import StallRegistrtionConvenerEditForm, FoodRegistrationConvenerEditForm
from payment.models import PaymentHistory

class ConvenerRegistrationController:

    def __init__(self, request, registration_id):
        self.request = request
        self.registration = get_object_or_404(
            StallRegistration,
            id=registration_id
        )

    def build_payment_history(self):
        return (
            PaymentHistory.paymenthistorycurrentmgr
            .get_stallholder_payment_history(
                stallholder=self.registration.stallholder.id
            )
        )

    def build_food_data(self):
        try:
            food_registration = FoodRegistration.objects.get(
                registration=self.registration
            )
            return food_registration
        except FoodRegistration.DoesNotExist:
            return None

    def build_food_form(self, post_data=False):
        """
        Build the food registration form.

        post_data=True → bind POST data
        post_data=False → instance only (GET render)
        """
        try:
            food_registration = FoodRegistration.objects.get(
                registration=self.registration
            )


            if post_data:
                return FoodRegistrationConvenerEditForm(
                    self.request.POST,
                    self.request.FILES,
                    instance=food_registration,
                )

            return FoodRegistrationConvenerEditForm(
                instance=food_registration
            )
        except FoodRegistration.DoesNotExist:
            return None

    def get_context(self, form=None, foodregistrationform=None, billing=None):

        if form is None:
            form = StallRegistrtionConvenerEditForm(
                instance=self.registration
            )

        payment_histories = self.build_payment_history()

        if foodregistrationform is None:
            foodregistrationform = self.build_food_form()

        food_registration = self.build_food_data()

        return {
            "stall_registration": self.registration,
            "registrationform": form,
            "billing": billing,
            "payment_histories": payment_histories,
            "foodregistrationupdateform": foodregistrationform,
            "food_data": food_registration,
        }

    def dispatch(self):
        if self.request.htmx:
            if "update" in self.request.POST:
                return self.handle_post()
            return self.handle_htmx()

        return self.render()

    def handle_htmx(self):

        form = StallRegistrtionConvenerEditForm(
            self.request.POST,
            self.request.FILES,
            instance=self.registration,
        )

        food_form = self.build_food_form(post_data=True)

        billing = None
        if form.is_valid():
            preview = form.build_registration_preview()
            billing = RegistrationBillingService(
                preview.fair
            ).calculate(preview)

        return self.render_partial(form, billing, food_form)

    def handle_post(self):
        form = StallRegistrtionConvenerEditForm(
            self.request.POST,
            self.request.FILES,
            instance=self.registration,
        )
        food_form = self.build_food_form(post_data=True)

        if not form.is_valid():
            return self.render_partial(form, None, food_form)

        # 1. Get the instance without committing to DB
        registration = form.save(commit=False)

        # 2. Trigger the FSM transition
        # This will set the target status AND set is_invoiced = False
        try:
            registration.to_booking_status_amended()
        except Exception as e:
            # Handle cases where the transition might not be allowed
            # (e.g., if the current status isn't in the source list)
            print(f"Transition failed: {e}")

        # 3. Save the instance and M2M data
        registration.save()
        form.save_m2m()
        food_form.save()

        return HttpResponse(headers={
            "HX-Redirect": reverse(
                "registration:convener-stall-food-registration-detail",
                args=[registration.id],
            )
        })

    def render(self):
        return TemplateResponse(
            self.request,
            "stallregistration/convener_stall_registration_detail.html",
            self.get_context(),
        )

    def render_partial(self, form, billing, food_form=None):
        return TemplateResponse(
            self.request,
            "stallregistration/convener_stallregistration_dynamic.html",
            self.get_context(
                form=form,
                billing=billing,
                foodregistrationform=food_form,
            ),
        )
