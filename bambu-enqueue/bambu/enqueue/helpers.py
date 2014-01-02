def enqueue(request, kind, data, is_file, **kwargs):
	if not data:
		return
	
	queues = getattr(request, 'queues', {})
	queue = queues.get(kind, [])
	
	if callable(data):
		data = data()
	
	if kind == 'css':
		if is_file:
			html = '<link rel="stylesheet"'
			if 'media' in kwargs:
				html += ' media="%s"' % kwargs['media']
			
			html += ' href="%s"' % data
		else:
			html = '<style'
			if 'media' in kwargs:
				html += ' media="%s"' % kwargs['media']
			
			html += '>%s</style>' % data
	elif kind == 'js':
		html = '<script'
		if is_file:
			html += ' src="%s"></script>' % data
		else:
			html += '>%s</script>' % data
	else:
		raise Exception('Unknown queue type')
	
	queue.append(html)
	queues[kind] = queue
	request.queues = queues