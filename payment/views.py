# payment/views.py

import stripe
import time
import logging
import uuid  # For generating unique idempotency keys
from django.views.decorators.csrf import csrf_exempt
import decimal
from weasyprint import HTML, CSS
from django.urls import reverse_lazy, reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required,permission_required
from django.template.loader import get_template
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django.core.exceptions import PermissionDenied
from django_fsm import can_proceed
from django.http import HttpResponse
from accounts.models import Profile
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Sum, Count, Q

from .models import (
    Invoice,
    InvoiceItem,
    DiscountItem,
    PaymentHistory,
    PaymentType
)
from .forms import (
    PaymentHistoryStatusFilterForm,
    UpdatePaymentHistoryForm
)
from fairs.models import (
    InventoryItem
)

db_logger = logging.getLogger('db')


@login_required()
def stripe_payment(request, id):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if request.method == 'POST':
        payment_history = PaymentHistory.objects.get(id=id)
        try:
            # Generate a unique idempotency key for this request
            idempotency_key = f"stripe_payment_{id}_{uuid.uuid4()}"

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'nzd',
                        'product_data': {
                            'name': 'Fair Stall Application',
                        },
                        'unit_amount': int(payment_history.amount_to_pay * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                metadata={'product_history_id': id},
                customer_creation='always',
                success_url=settings.REDIRECT_DOMAIN + '/payment/payment_successful/?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=settings.REDIRECT_DOMAIN + '/payment/payment_cancelled',
                idempotency_key=idempotency_key,  # Pass the idempotency key to Stripe
            )
        except stripe.error.StripeError as e:
            db_logger.error('Error creating Stripe checkout session: ' + str(e),
                            extra={'custom_category': 'Stripe Payment'})
            return render(request, 'error_page.html', {'error': 'An error occurred while processing your payment.'})
        return redirect(checkout_session.url, code=303)
    return render(request, 'myfair/myfair_dashboard.html')


@csrf_exempt
def payment_successful(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    checkout_session_id = request.GET.get('session_id')
    session = stripe.checkout.Session.retrieve(checkout_session_id)

    # Check if this session has already been processed
    payment_history = PaymentHistory.objects.get(id=session.metadata['product_history_id'])
    if payment_history.stripe_checkout_id == checkout_session_id:
        # If already processed, just render success
        return render(request, 'user_payment/payment_successful.html',
                      {'customer': stripe.Customer.retrieve(session.customer), 'session': session})

    customer = stripe.Customer.retrieve(session.customer)
    payment_type = PaymentType.objects.get(payment_type_name='Stripe')
    payment_history = PaymentHistory.objects.get(id=session.metadata['product_history_id'])
    amount_already_paid = payment_history.amount_paid
    payment_history.payment_type = payment_type
    amount_paid = session.get('amount_total') / 100
    amount_to_pay = payment_history.amount_to_pay - decimal.Decimal(amount_paid)
    payment_history.stripe_checkout_id = checkout_session_id
    payment_history.amount_to_pay = amount_to_pay
    payment_history.amount_paid = decimal.Decimal(amount_paid) + amount_already_paid
    if amount_to_pay < 0.00:
        payment_history.to_payment_status_credit()
    else:
        payment_history.to_payment_status_completed()
    payment_history.save()
    # Update StallRegistration instance to Payment Completed if amount to pay is zero
    if payment_history.amount_to_pay == 0.00:
        stall_registration = payment_history.invoice.stall_registration
        stall_registration.to_booking_status_payment_completed()
        stall_registration.save()

    return render(request, 'user_payment/payment_successful.html', {'customer': customer, 'session': session})


def payment_cancelled(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return render(request, 'user_payment/payment_cancelled.html')


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    time.sleep(10)
    payload = request.body
    signature_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, signature_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        db_logger.error('There was an error with processing the webhook. ' + str(e),
                        extra={'custom_category': 'Payments'})
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        db_logger.error('There was an error with processing the webhook. ' + str(e),
                        extra={'custom_category': 'Payments'})
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        session_id = session.get('id', None)
        time.sleep(15)
        webhook_amount = session.get('amount_total') / 100
        payment_history = PaymentHistory.objects.get(stripe_checkout_id=session_id)
        payment_history.webhook_amount = decimal.Decimal(webhook_amount)
        payment_history.save()

    return HttpResponse(status=200)


def invoice_pdf_generation(request, id, seq):
    invoice = get_object_or_404(Invoice, id=id, invoice_sequence=seq)
    invoice_items = InvoiceItem.objects.filter(invoice=id)
    profile = get_object_or_404(Profile, user=invoice.stallholder)
    payments = PaymentHistory.paymenthistorycurrentmgr.get_registration_payment_history(invoice.stall_registration)
    # Determine if there are any payments, if so sum them and add it to the context
    if payments:
        total_payments = payments.amount_paid
        total_credits = payments.amount_credited
        if total_credits:
            amount_to_pay = invoice.total_cost - total_payments + total_credits
        else:
            amount_to_pay = invoice.total_cost - total_payments
            total_credits = decimal.Decimal(0.00)
    else:
        total_payments = decimal.Decimal(0.00)
    # Determine if there are any discounts, if so sum them and add it to the context
    discounts = DiscountItem.objects.filter(stall_registration=invoice.stall_registration)
    if discounts:
        total_discount = sum(discounts.values_list('discount_amount', flat=True))
    else:
        total_discount = decimal.Decimal(0.00)
    # Render the template with the context
    context = {
        'invoice': invoice,
        'invoice_items': invoice_items,
        'total_payments': total_payments,
        'total_discount': total_discount,
        'total_credits' : total_credits,
        'amount_to_pay': amount_to_pay,
        'profile': profile
    }
    html_template = get_template('invoice.html').render(context)
    pdf_file = HTML(string=html_template, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'filename="MB_Fair_Invoice.pdf"'
    return response


def mark_payment_as_cancelled(request, id):
    """
    Description: Called from payment history list to set the status of the Payment History  to cancelled.
    """
    success_url = reverse_lazy('payment:payment-list')
    paymenthistory = get_object_or_404(PaymentHistory, pk=id)
    if not can_proceed(paymenthistory.to_payment_status_cancelled):
        raise PermissionDenied
    paymenthistory.to_payment_status_cancelled()
    paymenthistory.save()
    return HttpResponseRedirect(success_url)


def mark_payment_as_reconciled(request, id):
    """
    Description: Called from payment history list to set the status of the Payment History  to reconciled.
    """
    success_url = reverse_lazy('payment:payment-list')
    paymenthistory = get_object_or_404(PaymentHistory, pk=id)
    if not can_proceed(paymenthistory.to_payment_status_reconciled):
        raise PermissionDenied
    paymenthistory.to_payment_status_reconciled()
    paymenthistory.save()
    return HttpResponseRedirect(success_url)


def paymenthistory_listview(request):
    """
    View for displaying payments in a table with filtering based on payment_status.
    Filters are remembered within a session but reset when the page is refreshed.
    """
    template_name = 'paymenthistory_list.html'
    cards_per_page = 10

    # Session management for filters
    if "clear_filters" in request.GET:
        # Clear session filters on page refresh or when explicitly cleared
        request.session.pop("paymenthistory_filters", None)
        return redirect("payment:payment-list")

    # Initialize or retrieve session filter dict
    paymenthistory_filter_dict = request.session.get("paymenthistory_filters", {})

    # Initialize forms
    filterform = PaymentHistoryStatusFilterForm(request.POST or None)
    updateform = UpdatePaymentHistoryForm(request.POST or None)
    alert_message = "There are no Payment Histories created yet."

    # Filter based on licence_status from GET (initial load)
    payment_status = request.GET.get('payment_status', '')
    if payment_status:
        paymenthistory_filter_dict['payment_status'] = payment_status
        # Save filters to session
        request.session["paymenthistory_filters"] = paymenthistory_filter_dict
        alert_message = f'There are no payments of status {payment_status} created yet.'

    # HTMX-specific logic
    if request.htmx:
        template_name = 'paymenthistory_list_partial.html'

        # Get stallholder from POST request
        stallholder_id = request.POST.get('selected_stallholder')
        if stallholder_id:
            paymenthistory_filter_dict['invoice__stallholder'] = stallholder_id
            alert_message = f"There are no payment histories for stallholder {stallholder_id}."

        # Process filter form
        form_purpose = filterform.data.get('form_purpose', '') if filterform.is_bound else None
        if form_purpose == 'filter' and filterform.is_valid():
            payment_status = filterform.cleaned_data.get('payment_status')
            if payment_status:
                paymenthistory_filter_dict['payment_status'] = payment_status
                alert_message = f"There are no payment histories with status {payment_status}."
            if stallholder_id and payment_status:
                alert_message = f"There are no payment histories for stallholder {stallholder_id} with status {payment_status}."

        # Update session filters
        request.session["paymenthistory_filters"] = paymenthistory_filter_dict

    # Query filtered data
    payment_history_list = PaymentHistory.paymenthistorycurrentmgr.filter(
        **paymenthistory_filter_dict
    ).order_by('-date_created')

    # Apply pagination
    page_list, page_range = pagination_data(cards_per_page, payment_history_list, request)

    # Prepare context and return response
    return TemplateResponse(request, template_name, {
        'filterform': filterform,
        'updateform': updateform,
        'page_obj': page_list,
        'alert_mgr': alert_message,
        'page_range': page_range,
    })


def payment_dashboard_view(request):
    """
    Populate the Payments Dashboard with counts of the various payment statuses
    """
    total_counts = PaymentHistory.paymenthistorycurrentmgr.get_all_except_superceded().count()
    pending_counts = PaymentHistory.paymenthistorycurrentmgr.get_pending().count()
    cancelled_counts = PaymentHistory.paymenthistorycurrentmgr.get_cancelled().count()
    completed_counts = PaymentHistory.paymenthistorycurrentmgr.get_completed().count()
    credit_counts = PaymentHistory.paymenthistorycurrentmgr.get_credit().count()
    failed_counts = PaymentHistory.paymenthistorycurrentmgr.get_failed().count()
    reconciled_counts = PaymentHistory.paymenthistorycurrentmgr.get_reconciled().count()

    return TemplateResponse(request, 'dashboards/dashboard_payments.html', {
        'total_counts': total_counts,
        'pending_counts': pending_counts,
        'cancelled_counts': cancelled_counts,
        'completed_counts': completed_counts,
        'credit_counts': credit_counts,
        'failed_counts': failed_counts,
        'reconciled_counts': reconciled_counts
    })


def load_update_form(request, id):
    '''
    Load the UpdatePaymentHistoryForm prepopulated with the instance of payment history
    '''
    payment_history = get_object_or_404(PaymentHistory, id=id)
    updateform = UpdatePaymentHistoryForm(instance=payment_history)
    return render(request, 'update_payment_form.html', {'updateform': updateform, 'payment_id': id})


def update_payment_history(request, id):
    """
    Conveners function to update an existing payment history.
    """
    # Retrieve the payment history instance or return 404 if not found
    obj = get_object_or_404(PaymentHistory, id=id)
    updateform = UpdatePaymentHistoryForm(request.POST or None, instance=obj)
    context = {
        'updateform': updateform,
        'payment_id': id
    }

    # Check if form is submitted and valid
    if request.method == 'POST':
        if updateform.is_valid():
            # Save the updated instance
            obj = updateform.save(commit=False)
            obj.is_valid = True  # Set additional attributes if necessary
            obj.save()
            # Render the success message HTML snippet
            context = {
                'alert_mgr': 'Payment history updated successfully'
            }
            return render(request, "paymenthistory_list_partial.html", context)

        else:
            # Render the error message
            context = {
                'alert_mgr': 'Payment history updated failed'
            }
            return render(request, "paymenthistory_list_partial.html", context)

    # If the request is GET, render the update form
    return render(request, "payment/update_payment_form.html", context)

def pagination_data(cards_per_page, queryset, request):
    """
    Handles pagination of a queryset
    """
    paginator = Paginator(queryset, cards_per_page)  # Paginate with the specified number of items per page
    page_number = request.GET.get('page', 1)  # Get the current page number
    page_list = paginator.get_page(page_number)  # Get the paginated data for the current page

    try:
        page_obj = paginator.get_page(page_number)  # Get the paginated data for the current page
    except PageNotAnInteger:
        # If page is not an integer, deliver the first page
        page_obj = paginator.get_page(1)
    except EmptyPage:
        # If the page is out of range, deliver the last page
        page_obj = paginator.get_page(paginator.num_pages)

    page_range = list(paginator.get_elided_page_range(
        page_number,
        on_each_side=1,
        on_ends=2
    ))  # Custom range for pagination links

    return page_list, page_range


def financial_performance_view(request):
    # Income Summary
    inventory_summary = (
        InvoiceItem.objects
        .filter(
            invoice__stall_registration__booking_status='Booked'
        )
        .values("inventory_item__item_name")
        .annotate(
            total_count=Sum("item_quantity"),
            total_paid=Sum(
                "invoice__payment_history__amount_paid",
                filter=Q(invoice__payment_history__payment_status__in=["Completed", "Reconciled"])
            )
        )
    )

    # Calculate grand total for income
    total_income = sum(item["total_paid"] or 0 for item in inventory_summary)

    # Expenses Summary
    total_discounts = DiscountItem.objects.aggregate(total_discount=Sum("discount_amount"))["total_discount"] or 0
    total_credits = PaymentHistory.objects.filter(payment_status="Credit").aggregate(
        total_credit=Sum("amount_credited")
    )["total_credit"] or 0

    # Calculate grand total for expenses
    total_expenses = total_discounts + total_credits

    # Context
    context = {
        "inventory_summary": inventory_summary,
        "total_discounts": total_discounts,
        "total_credits": total_credits,
        "total_income": total_income,
        "total_expenses": total_expenses,
    }
    return render(request, "dashboards/financial_performance.html", context)
