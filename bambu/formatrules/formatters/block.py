from bambu.formatrules.formatters import FormatterBase
from markdown import markdown

FRACTIONS = {
	'whole': 12,
	'two thirds': 8,
	'two-thirds': 8,
	'half': 6,
	'third': 4,
	'quarter': 3,
	'sixth': 2,
	'twelfth': 1
}

NUMBER_NAMES = {
	'one': 12,
	'two': 6,
	'three': 4,
	'four': 3,
	'six': 2,
	'twelve': 1
}

NUMBER_DIGITS = {
	'1': 12,
	'2': 6,
	'3': 4,
	'4': 3,
	'6': 2,
	'12': 1
}

class BlockFormatter(FormatterBase):
	rules = (
		(r'^[Bb]lock of (\w+)$', 'block'),
		(r'^[Ee]nd (?:of )?blocks$', 'endblocks'),
		(r'^(.+) block$', 'block')
	)
	
	def __init__(self, *args, **kwargs):
		super(BlockFormatter, self).__init__(*args, **kwargs)
		self.rows = 0
	
	def block(self, value, number, *args, **kwargs):
		number = unicode(number).lower()
		
		if number in NUMBER_NAMES:
			number = NUMBER_NAMES[number]
		elif number in FRACTIONS:
			number = FRACTIONS[number]
		elif number in NUMBER_DIGITS:
			number = NUMBER_DIGITS[number]
		else:
			return value
		
		html = ''
		if self.rows == 0:
			self.rows += 1
			html = '<div class="row"><!-- Start row -->'
		
		html += u'<div class="span%d"><! -- Column -->%s<!-- End column --></div>\n' % (
			number, markdown(value)
		)
		
		return html
	
	def endblocks(self, value, *args, **kwargs):
		while self.rows > 0:
			value = u'<!-- End row --></div>\n' + value
			self.rows -= 1
		
		return value
	
	def cleanup(self, value):
		return value + self.endblocks('')