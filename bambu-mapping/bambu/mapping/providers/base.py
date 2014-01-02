class ProviderBase(object):
	settings = {}
	
	def __init__(self, container_id, *args, **kwargs):
		self.container_id = container_id
		
		for key, value in kwargs.items():
			self.settings[key] = value
	
	def add_container(self):
		style = {}
		
		if 'width' in self.settings:
			style['width'] = self.settings['width']
		else:
			style['width'] = '100%'
		
		if 'height' in self.settings:
			style['height'] = self.settings['height']
		
		ret = '<div id="%s"' % self.container_id
		
		if any(style):
			ret += ' style="%s" class="map-container"' % ';'.join(
				'%s: %s' % i for i in style.items()
			)
		
		ret += '></div>'
		return ret
	
	def init_map(self):
		raise NotImplementedError('Method not implemented.')
	
	def set_position(self, latitude, longitude):
		raise NotImplementedError('Method not implemented.')
	
	def add_marker(self, **kwargs):
		raise NotImplementedError('Method not implemented.')
	
	def get_map_varname(self):
		return 'map_%s' % self.container_id
	
	def add_map_callback(self, callback):
		return '%s(%s)' % (callback,
			self.get_map_varname()
		)

	def add_marker_callback(self, marker, callback):
		return '%s(%s)' % (callback, marker)
	
	def remove_marker(self):
		return ''
	
	def find_address(self):
		raise NotImplementedError('Method not implemented.')
	
	def find_coords(self):
		raise NotImplementedError('Method not implemented.')
	
	def set_centre(self):
		raise NotImplementedError('Method not implemented.')
	
	def get_image_url(self):
		raise NotImplementedError('Method not implemented.')
	
	class Media:
		js = ()