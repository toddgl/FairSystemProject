# payment/views.py

import stripe
import time
import logging
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
from django.core.paginator import Paginator
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

db_logger = logging.getLogger('db')

@login_required()
def stripe_payment(request, id):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if request.method == 'POST':
        payment_history = PaymentHistory.objects.get(id=id)
        try:
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
            )
        except Exception as e:  # It will catch other errors related to the cancel call.
            db_logger.error('There was an error making the stripe payment.' + str(e),
                            extra={'custom_category': 'Stripe Payment'})
            print(str(e))
        return redirect(checkout_session.url, code=303)
    return render(request, 'myfair/myfair_dashboard.html')


@csrf_exempt
def payment_successful(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    checkout_session_id = request.GET.get('session_id')
    session = stripe.checkout.Session.retrieve(checkout_session_id)

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
        amount_to_pay = invoice.total_cost - total_payments
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
    Description: view for displaying payments in a table with filter based on payment_status and providing
    functionality to change the status from Pending to Cancelled, Completed to Reconciled, and Pending to Failed.
    """
    payment_history_status_filter_dict = {}
    template_name = 'paymenthistory_list.html'
    filterform = PaymentHistoryStatusFilterForm(request.POST or None)
    updateform = UpdatePaymentHistoryForm(request.POST or None)
    payment_status = request.GET.get('payment_status', '')

    if payment_status:
        payment_history_list = PaymentHistory.paymenthistorycurrentmgr.filter(payment_status=payment_status).all().order_by('id')
        alert_message = 'There are no Payment Histories of status ' + str(payment_status) + ' created yet'
    else:
        payment_history_list = PaymentHistory.paymenthistorycurrentmgr.all().order_by('id')
        alert_message = 'There are no Payment Histories created yet.'

    # Apply pagination
    paginator = Paginator(payment_history_list, 10)  # Show 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.htmx:
        template_name = 'paymenthistory_list_partial.html'
        return TemplateResponse(request, template_name, {
            'page_obj': page_obj,
            'payment_status': payment_status,
            'alert_mgr': alert_message,
        })
    else:
        return TemplateResponse(request, template_name, {
            'filterform': filterform,
            'updateform': updateform,
            'page_obj': page_obj,
            'payment_status': payment_status,
            'alert_mgr': alert_message,
        })


def payment_dashboard_view(request):
    """
    Populate the Payments Dashboard with counts of the various payment statuses
    """
    total_counts = PaymentHistory.paymenthistorycurrentmgr.get_all_except_superceded().count()
    pending_counts = PaymentHistory.paymenthistorycurrentmgr.get_pending().count()
    cancelled_counts = PaymentHistory.paymenthistorycurrentmgr.get_cancelled().count()
    completed_counts = PaymentHistory.paymenthistorycurrentmgr.get_completed().count()
    failed_counts = PaymentHistory.paymenthistorycurrentmgr.get_failed().count()
    reconciled_counts = PaymentHistory.paymenthistorycurrentmgr.get_reconciled().count()

    return TemplateResponse(request, 'dashboards/dashboard_payments.html', {
        'total_counts': total_counts,
        'pending_counts': pending_counts,
        'cancelled_counts': cancelled_counts,
        'completed_counts': completed_counts,
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

