from bambu.formatrules.formatters import FormatterBase
from django.conf import settings

FORMATTERS = getattr(settings, 'FORMATRULES_FORMATTERS',
	(
		'bambu.formatrules.formatters.block.BlockFormatter',
		'bambu.formatrules.formatters.bookmark.BookmarkFormatter',
	)
)