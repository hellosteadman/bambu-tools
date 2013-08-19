from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from bambu.xmlrpc import dispatcher

@csrf_exempt
def dispatch(request):
	if request.method == 'POST':
		response = HttpResponse(mimetype = 'application/xml')
		response.write(
			dispatcher._marshaled_dispatch(
				getattr(request, 'body', request.raw_post_data)
			)
		)
	else:
		response = HttpResponse()
		response.write('<b>This is an XML-RPC Service.</b><br>')
		response.write('You need to invoke it using an XML-RPC Client!<br>')
		response.write('The following methods are available:<ul>')
		
		for method in dispatcher.system_listMethods():
			sig = dispatcher.system_methodSignature(method)
			help = dispatcher.system_methodHelp(method)
			
			response.write(
				'<li><b>%s</b>: [%s] %s' % (method, sig, help)
			)
		
		response.write('</ul>')
	
	response['Content-length'] = str(len(response.content))
	return response