# registration/services/registration_update.py

from django.http import HttpResponseRedirect, HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse


from registration.models import (
    FoodRegistration,
    RegistrationComment,
    AdditionalSiteRequirement,
)

from fairs.models import (
    SiteAllocation,
)

from registration.forms import (
    StallRegistrationForm,
    RegistrationCommentForm,
    CommentFilterForm,
    CommentReplyForm,
    AdditionalSiteReqForm,
)

from registration.services.billing import RegistrationBillingService

def build_update_context(request, registration):

    stallholder = registration.stallholder
    fair = registration.fair

    allocations = (
        SiteAllocation.currentallocationsmgr
        .filter(stallholder_id=stallholder.id,
                stall_registration=registration.id)
    )

    comments = RegistrationComment.objects.filter(
        stallholder=request.user,
        is_archived=False,
        convener_only_comment=False,
        comment_parent__isnull=True,
        fair=fair.id,
    )

    additional_sites = AdditionalSiteRequirement.objects.filter(
        stall_registration=registration
    )

    return {
        "stallregistration": registration,
        "billing": registration.total_charge,
        "registrationform": StallRegistrationForm(
            instance=registration
        ),
        "additionalsiteform": AdditionalSiteReqForm(),
        "commentfilterform": CommentFilterForm(),
        "commentform": RegistrationCommentForm(),
        "replyform": CommentReplyForm(),
        "comments": comments,
        "filter": "Showing current comments of the current fair",
        "allocations": allocations if allocations.exists() else None,
        "site_requirement_list": additional_sites,
    }


def handle_successful_update(request, form, obj, success_url):
    form = StallRegistrationForm(
        request.POST or None,
        request.FILES or None,
        instance=obj,
        )

    billing = None

    billing = form.calculate_cost()

    registration = form.save(commit=False)
    registration.stallholder = obj.stallholder
    if billing:
        registration.total_charge = billing['total']
    registration.save()

    ensure_food_registration(registration)

    if registration.selling_food:
        # 1. Manually resolve the URL path
        target_url = reverse("registration:food-registration", args=[registration.id])

        # 2. Create an empty response and add the HTMX header
        response = HttpResponse()
        response["HX-Redirect"] = target_url
        return response

    if request.htmx:
        return HttpResponseRedirect(reverse("registration:stallregistration-dashboard"))

    return redirect(success_url)


def ensure_food_registration(registration):

    if not registration.selling_food:
        return

    FoodRegistration.objects.get_or_create(
        registration=registration,
        defaults={
            "has_food_certificate": False,
            "food_fair_consumed": False,
            "has_food_prep": False,
            "is_valid": False,
        },
    )

def update_registration(form, instance):

    # form already validated
    registration = form.save(commit=False)
    print("Got to update_registration")

    billing_service = RegistrationBillingService(
        registration.fair
    )

    billing = billing_service.calculate(registration)

    registration.total_charge = billing["total"]

    registration.save()
    form.save_m2m()

    return registration, billing