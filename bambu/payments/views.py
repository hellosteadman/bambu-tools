from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from bambu.payments.models import Payment
from bambu.payments import site

@csrf_exempt
def callback(request, payment = None, gateway = None):
	if payment:
		payment = get_object_or_404(Payment, pk = payment)
		return payment.process_view(request)
	else:
		for g in site._gateways.values():
			if g.shortname == gateway:
				return g.callback_view(request)
	
	raise Http404('Gateway %s not found.' % gateway)

@csrf_exempt
def cancel(request, payment):
	payment = get_object_or_404(Payment, pk = payment)
	return payment.process_view(request, cancel = True)