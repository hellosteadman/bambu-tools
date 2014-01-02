from markdown import markdown

class FormatterBase(object):
	def cleanup(self, value):
		return value