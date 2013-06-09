from django.template import Library
from django.utils.safestring import mark_safe

register = Library()

@register.filter()
def prettyjson(value):
	output = ''
	in_quotes = False
	previous = ''
	tabs = 0
	
	for c in value:
		if c == ' ' and previous == ',' and not in_quotes:
			continue
		
		if not in_quotes:
			if c == '[' or c == '{':
				output += c
				tabs += 1
				output += '\n' + ('&nbsp;&nbsp;' * tabs)
			elif c == ']' or c == '}':
				tabs -= 1
				output += '\n'
				if tabs > 0:
					output += '&nbsp;&nbsp;' * tabs
				
				output += c
			elif c == ',':
				output += c + '\n' + ('&nbsp;&nbsp;' * tabs)
			else:
				output += c
		elif c == '"':
			output += c
			if previous != '\\':
				in_quotes = not in_quotes
		else:
			output += c
		
		previous = c
	
	return mark_safe(output)