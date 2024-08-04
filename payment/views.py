# payment/views.py

import stripe
import time
from django.views.decorators.csrf import csrf_exempt
import decimal
from weasyprint import HTML, CSS
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from accounts.models import Profile
from .models import (
	Invoice,
	InvoiceItem,
	DiscountItem,
	PaymentHistory,
	PaymentType
)
@login_required()
def stripe_payment(request, id):
	stripe.api_key = settings.STRIPE_SECRET_KEY
	print('Stripe payment method called')
	if request.method == 'POST':
		payment_history = PaymentHistory.objects.get(id=id)
		checkout_session = stripe.checkout.Session.create(
			payment_method_types=['card'],
			line_items=[{
				'price_data': {
					'currency': 'nzd',
					'product_data': {
						'name': 'Fair Stall Application',
					},
					'unit_amount': int(payment_history.amount_to_pay - payment_history.amount_paid) * 100,
				},
				'quantity': 1,
			}],
			mode='payment',
			metadata={'product_history_id': id},
			customer_creation='always',
			success_url=settings.REDIRECT_DOMAIN + '/payment/payment_successful/?session_id={CHECKOUT_SESSION_ID}',
			cancel_url=settings.REDIRECT_DOMAIN + '/payment/payment_cancelled',
		)
		return redirect(checkout_session.url, code=303)
	return render(request, 'myfair_dashboard.html')


def payment_successful(request):
	stripe.api_key = settings.STRIPE_SECRET_KEY
	checkout_session_id = request.GET.get('session_id')
	print("Checkout Session id", checkout_session_id)
	session = stripe.checkout.Session.retrieve(checkout_session_id)

	customer = stripe.Customer.retrieve(session.customer)
	payment_type = PaymentType.objects.get(payment_type_name='Stripe')
	payment_history = PaymentHistory.objects.get(id=session.metadata['product_history_id'])
	payment_history.payment_type = payment_type
	payment_history.stripe_checkout_id = checkout_session_id
	payment_history.save()
	return render(request, 'user_payment/payment_successful.html', {'customer': customer, 'session': session})

def payment_cancelled(request):
	stripe.api_key = settings.STRIPE_SECRET_KEY
	return render(request, 'user_payment/payment_cancelled.html')

@csrf_exempt
def stripe_webhook(request):
	print('Stripe webhook called')
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
		return HttpResponse(status=400)
	except stripe.error.SignatureVerificationError as e:
		return HttpResponse(status=400)

	if event['type'] == 'checkout.session.completed':
		session = event['data']['object']
		session_id = session.get('id', None)
		time.sleep(15)
		amount_paid = session.get('amount_total') / 100
		payment_history = PaymentHistory.objects.get(stripe_checkout_id=session_id)
		payment_history.update_payment(decimal.Decimal(amount_paid))
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
		amount_to_pay =invoice.total_cost - total_payments
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