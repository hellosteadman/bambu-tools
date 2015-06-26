from django.core.urlresolvers import reverse
from django.core.urlresolvers import RegexURLResolver
from django.http import HttpResponse, HttpResponseRedirect
from functools import update_wrapper

def argument(name, type = 'str', description = '', **kwargs):
	def decorator(f):
		def wrapper(*a, **k):
			return f(*a, **k)
		
		required = kwargs.pop('required', True)
		kwargs.update(
			{
				'type': type,
				'description': description,
				'required': required
			}
		)
		
		if isinstance(f, RegexURLResolver):
			def u(pattern):
				if getattr(pattern, 'callback'):
					w = update_wrapper(wrapper, pattern.callback)
					args = getattr(w, 'api_args', [])
					if not name in dict(args):
						args.insert(0, (name, kwargs))
						w.api_args = args
				else:
					for p in pattern.url_patterns:
						p = u(p)
				
				return pattern
			
			for pattern in f.url_patterns:
				pattern = u(pattern)
			
			return f
		
		w = update_wrapper(wrapper, f)
		args = getattr(w, 'api_args', [])
		if not name in dict(args):
			args.insert(0, (name, kwargs))
			w.api_args = args
		
		return w
	
	return decorator

def returns(name_or_dict, type = 'str', description = '', **kwargs):
	def decorator(f):
		def wrapper(*a, **k):
			return f(*a, **k)
		
		if isinstance(name_or_dict, dict):
			returns = {}
			for n, a in name_or_dict.items():
				a = list(a)
				
				if not any(a):
					a.append('str')
				
				if len(a) < 2:
					a.append('')
				
				if len(a) < 3:
					a.append({})
				else:
					a[2] = {
						'keys': a[2]
					}
				
				returns[n] = a
		else:
			returns = {
				name_or_dict: (type, description, kwargs)
			}
		
		w = update_wrapper(wrapper, f)
		values = getattr(w, 'api_return_values', {})
		for (name, (t, d, kw)) in returns.items():
			if isinstance(type, str):
				if t == 'dict' and not 'keys' in kw:
					raise TypeError('Return value \'%s\' set to dict type, but no keys specified' % name)
			
			if 'keys' in kw:
				if isinstance(kw['keys'], (str, unicode)):
					if kw['keys'] != 'dynamic':
						raise TypeError('keys argument for return value \'%s\' must be a dict, or the word \'dynamic\'' % name)
				elif not isinstance(kw['keys'], dict):
					raise TypeError('keys argument for return value \'%s\' must be a dict, or the word \'dynamic\'' % name)
				else:
					k = {}
					for n, a in kw['keys'].items():
						a = list(a)
						
						if not any(a):
							a.append('str')
						
						if len(a) < 2:
							a.append('')
						
						if len(a) < 3:
							a.append({})
						else:
							a[2] = {
								'keys': a[2]
							}
						
						k[n] = {
							'type': a[0],
							'description': a[1]
						}
						
						k[n].update(a[2])
					
					kw['keys'] = k
			
			kw.update(
				{
					'type': t,
					'description': d
				}
			)
			
			if not name in values:
				values[name] = kw
		
		w.api_return_values = values
		return w
	
	return decorator

def named(name):
	def decorator(f):
		def wrapper(*a, **k):
			return f(*a, **k)
		
		w = update_wrapper(wrapper, f)
		w.api_verbose_name = name
		return w
	
	return decorator