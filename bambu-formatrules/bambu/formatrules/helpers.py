from bambu.formatrules import FORMATTERS
from django.utils.importlib import import_module
import re

FORMATTER_CACHE = {}

def get_formatter(rule):
	rule = rule.replace('\r', '').replace('\n', '')
	tried = []
	
	for formatter in FORMATTERS:
		module, dot, klass = formatter.rpartition('.')
		module = import_module(module)
		klass = getattr(module, klass)
		
		for r, fn in klass.rules:
			match = re.match(r, rule)
			if match:
				if klass in FORMATTER_CACHE:
					obj = FORMATTER_CACHE[klass]
				else:
					obj = klass()
					FORMATTER_CACHE[klass] = obj
				
				return obj, getattr(obj, fn), match.groups(), match.groupdict()
			
			tried.append(r)
	
	return None, None, [], {}