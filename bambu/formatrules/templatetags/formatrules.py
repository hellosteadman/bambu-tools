from django.template import Library
from bambu.formatrules import FORMATTERS, helpers
import re

register = Library()

@register.filter
def formatting(value):
	used_formatters = []
	
	while True:
		result = re.search(r'^\/\/ ?(.+)$', value, re.MULTILINE)
		if not result:
			for formatter in used_formatters:
				value = formatter.cleanup(value)
			
			return value
		
		start, end = result.start(), result.end()
		before = value[:start]
		after = value[end:]
		
		next_result = re.search(r'^\/\/ ?(.+)$', after, re.MULTILINE)
		if next_result:
			before_next = after[:next_result.start()]
		else:
			before_next = after
		
		for group in result.groups():
			formatter, function, args, kwargs = helpers.get_formatter(group)
			if not formatter:
				replacement = '<!-- Unknown format rule: "%s" -->' % group
			else:
				replacement = function(before_next, *args, **kwargs)
				if not formatter in used_formatters:
					used_formatters.append(formatter)
			
			value = before + replacement + after[len(before_next):]
	
	return value