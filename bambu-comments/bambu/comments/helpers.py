from pyquery import PyQuery
from html2text import HTML2Text
from markdown import markdown as md

UNCLEAN_TAGS = (
	'audio', 'video', 'iframe', 'object', 'form', 'input', 'select', 'textarea', 'script', 'style'
)

UNCLEAN_ATTRS = (
	'onabort', 'onafterprint', 'onbeforeprint', 'onbeforeunloa', 'onblur', 'oncanplay', 'oncanplaythrough',
	'onchange', 'onclick', 'oncontextmenu', 'ondblclick', 'ondrag', 'ondragend', 'ondragenter', 'ondragleave',
	'ondragover', 'ondragstart', 'ondrop', 'ondurationchange', 'onemptiedNew', 'onendedNew', 'onerro', 'onerrorNew',
	'onfocus', 'onformchange', 'onforminput', 'onhaschange', 'oninput', 'oninvalid', 'onkeydown', 'onkeypress',
	'onkeyup', 'onload', 'onloadeddataNew', 'onloadedmetadataNew', 'onloadstartNew', 'onmessage', 'onmousedown',
	'onmousemove', 'onmouseout', 'onmouseover', 'onmouseup', 'onmousewheel', 'onoffline', 'ononline', 'onpagehide',
	'onpageshow', 'onpauseNew', 'onplayNew', 'onplaying', 'onpopstate', 'onprogressNew', 'onratechangeNew',
	'onreadystatechangeNew', 'onredo', 'onreset', 'onresize', 'onscroll', 'onseekedNew', 'onseekingNew', 'onselect',
	'onstalledNew', 'onstorage', 'onsubmit', 'onsuspendNew', 'ontimeupdateNew', 'onundo', 'onunload', 'onvolumechangeNew',
	'onwaiting'
)

def sanitise(text, markdown = False):
	if markdown:
		text = md(text)
	
	dom = PyQuery(text)
	
	for a in dom.find('a[href^="javascript:"]'):
		a = PyQuery(a)
		a.replaceWith(a.text())
	
	for obj in UNCLEAN_TAGS:
		dom.find(obj).remove()
	
	for attr in UNCLEAN_ATTRS:
		dom.find('[%s]' % attr).removeAttr(attr)
	
	text = dom.outerHtml()
	if markdown:
		dom = HTML2Text()
		text = dom.handle(text)
	
	return text