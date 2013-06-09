from bambu.formatrules.formatters import FormatterBase

class BookmarkFormatter(FormatterBase):
	rules = (
		(r'^[Ss]ection\: ([\w-]+)$', 'section'),
	)
	
	def section(self, value, name, *args, **kwargs):
		while value.startswith('\n'):
			value = value[1:]
		
		while value.startswith('\r'):
			value = value[1:]
		
		lines = value.splitlines()
		if lines[0].startswith('#'):
			space = lines[0].find(' ')
			if space > -1:
				heading = u"'%s'" % lines[0][space + 1:]
			else:
				heading = u'section'
			
			lines[0] += ' <a class="section-anchor" href="#%s" title="Permalink to %s">&para;</a>' % (name, heading)
		
		return '\n<a name="%s"></a>\n%s' % (name, '\n'.join(lines))