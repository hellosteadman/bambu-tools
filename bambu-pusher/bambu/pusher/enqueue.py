from bambu.pusher import KEY
from bambu.enqueue import enqueue_script_file, enqueue_script_block

def script(request):
	enqueue_script_file(request, 'https://d3dy5gmtp8yhk7.cloudfront.net/2.0/pusher.min.js')
	enqueue_script_block(request,
		"""Pusher.log = function(message) { if (window.console && window.console.log) window.console.log(message); };
		var pusher = new Pusher('%s');""" % KEY
	)