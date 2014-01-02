from django.template import Library
from django.utils.safestring import mark_safe
from django.utils.safestring import SafeString, SafeUnicode
from django.conf import settings
from django.utils.encoding import smart_str
from bambu.attachments import ATTACHMENT_REGEX
from bambu.attachments.models import Attachment
from shlex import split

WIDTH = getattr(settings, 'ATTACHMENT_WIDTH', 640)
register = Library()

@register.filter()
def attachments(value, obj, width = WIDTH):
	match = ATTACHMENT_REGEX.search(value)
	safe = isinstance(value, (SafeString, SafeUnicode))
	
	while not match is None and match.end() <= len(value):
		start = match.start()
		end = match.end()
		groups = match.groups()
		
		if len(groups) > 0:
			index = groups[0]
			options = None
			
			if len(groups) > 1:
				options = groups[1]
				if options:
					options = options.strip()
					if options:
						try:
							options = split(smart_str(options))
						except:
							options = None
			
			args = []
			kwargs = {
				'width': width
			}
			
			if options:
				for option in options:
					key, equals, val = option.partition('=')
					if equals != '=':
						if key and not val:
							args.append(key)
						continue
					
					kwargs[key] = val
			
			try:
				if isinstance(obj, dict):
					inner = Attachment(
						**obj['attachments__attachment'][int(index) - 1]
					).render(*args, **kwargs)
				else:
					inner = obj.attachments.all()[int(index) - 1].render(*args, **kwargs)
			except:
				inner = ''
		else:
			inner = ''
		
		value = value[:start] + inner + value[end:]
		match = ATTACHMENT_REGEX.search(value, start + len(inner))
	
	if safe:
		return mark_safe(value)
	else:
		return value