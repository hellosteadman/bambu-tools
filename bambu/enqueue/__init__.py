from bambu.enqueue.helpers import enqueue

def enqueue_script_file(request, url):
	enqueue(request, 'js', url, True)

def enqueue_script_block(request, script):
	enqueue(request, 'js', script, False)

def enqueue_css_file(request, url, media = 'all'):
	enqueue(request, 'css', url, True, media = media)

def enqueue_css_block(request, styles, media = 'all'):
	enqueue(request, 'css', styles, False, media = media)