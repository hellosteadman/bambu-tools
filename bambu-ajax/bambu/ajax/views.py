from bambu.ajax import site
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.response import TemplateResponse

try:
    import json
except:
    from django.utils import simplejson as json

def utility(request):
    return TemplateResponse(
        request,
        'ajax/utils.js',
        {
        },
        content_type = 'text/javascript'
    )

def endpoint(request):
    if not 'f' in request.GET:
        return HttpResponse(
            json.dumps(site._registry.keys()),
            content_type = 'application/json'
        )

    kwargs = {}
    for key, value in request.GET.items():
        if key == 'f':
            funchash = value
        else:
            kwargs[key] = value

    if funchash in site._registry:
        response = site._registry[funchash](request, **kwargs)

        if isinstance(response, HttpResponse):
            return response

        if isinstance(response, (list, tuple, dict)):
            return HttpResponse(
                response,
                content_type = 'application/json'
            )

    return HttpResponseBadRequest(
        json.dumps(
            {
                'error': 'Function with hash not found'
            }
        ),
        content_type = 'application/json'
    )
