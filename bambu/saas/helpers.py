# encoding: utf-8

from django.conf import settings
from django.utils.importlib import import_module
from inspect import getargspec

def get_currencies():
	return [
		(x, y) for (x, y, z) in getattr(settings, 'CURRENCIES', ())
	]

def get_currency_symbol(currency = None):
	d = {}
	
	for (x, y, z) in getattr(settings, 'CURRENCIES', ()):
		d[x] = z
	
	return d.get(
		currency or getattr(settings, 'DEFAULT_CURRENCY', 'GBP'),
		u'£'
	)

def separate_thousands(value):
	result = ''
	x = value
	
	while x >= 1000:
		x, r = divmod(x, 1000)
		result = ",%03d%s" % (r, result)
	
	return "%d%s" % (x, result)

def format_price(symbol, price):
	if price == 0:
		return 0
	else:
		units = str(int(price * 100))
		last = int(units[-2:])
		first = int(units[:-2])
		
		if last > 0:
			result = '%s.%d' % (separate_thousands(first), last)
		else:
			result = separate_thousands(int(price))
			
		return symbol + result

def feature_has_arguments(feature):
	parts = feature.test_function.split('.')
	mod = '.'.join(parts[:-1])
	func = parts[-1]
	
	mod = import_module(mod)
	func = getattr(mod, func)
	args = getargspec(func).args
	
	return len(args) > 1

def feature_usage(feature, user, **kwargs):
	parts = feature.test_function.split('.')
	mod = '.'.join(parts[:-1])
	func = parts[-1]
	
	mod = import_module(mod)
	func = getattr(mod, func)
	usage = func(user, **kwargs)
	
	if feature.is_boolean:
		return usage == True
	else:
		return usage

def test_feature(feature, user, value, **kwargs):
	usage = feature_usage(feature, user, **kwargs)
	
	if feature.is_boolean:
		return usage == True
	else:
		return usage < value
	
def fix_discount_code(code):
	if not code:
		return ''
	
	from bambu.saas.models import Discount
	try:
		return Discount.objects.get(code__iexact = code).code
	except Discount.DoesNotExist:
		return ''