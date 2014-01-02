from django.utils.http import urlencode
from bambu.mapping.providers.base import ProviderBase

class GoogleMapsProvider(ProviderBase):
	def init_map(self):
		controls = self.settings.get('controls', ('ZOOM', 'ATTRIBUTION'))
		
		return """%(varname)s = new google.maps.Map(
			document.getElementById('%(id)s'),
			{
				center: new google.maps.LatLng(%(lat)s, %(lon)s),
				zoom: %(zoom)d,
				mapTypeId: google.maps.MapTypeId.ROADMAP,
				disableDefaultUI: true,
				panControl: %(pancontrol)s,
				zoomControl: %(zoomcontrol)s,
				mapTypeControl: %(typecontrol)s,
				scaleControl: %(scalecontrol)s,
				streetViewControl: %(streetviewcontrol)s,
				overviewMapControl: %(overviewcontrol)s
			}
		);""" % {
			'varname': self.get_map_varname(),
			'id': self.container_id,
			'lat': self.settings.get('lat', 'null'),
			'lon': self.settings.get('lon', 'null'),
			'zoom': self.settings.get('zoom', 10),
			'controls': ', '.join(
				["'%s'" % c for c in controls]
			),
			'pancontrol': 'PAN' in controls and 'true' or 'false',
			'zoomcontrol': 'ZOOM' in controls and 'true' or 'false',
			'typecontrol': 'TYPE' in controls and 'true' or 'false',
			'scalecontrol': 'SCALE' in controls and 'true' or 'false',
			'streetviewcontrol': 'STREETVIEW' in controls and 'true' or 'false',
			'overviewcontrol': 'OVERVIEW' in controls and 'true' or 'false',
		}
	
	def add_marker(self):
		return """function(options) {
			var marker = new google.maps.Marker(
				{
					map: %(map_varname)s,
					position: new google.maps.LatLng(options.lat, options.lon),
					title: options.title,
					icon: options.icon,
					draggable: options.draggable
				}
			);
			
			if(options.content) {
				var infowindow = new google.maps.InfoWindow(
					{
						content: options.content,
						maxWidth: 200
					}
				);
				
				google.maps.event.addListener(
					marker, 'click', function() {
						infowindow.open(%(map_varname)s, marker);
					}
				);
			}
			
			if(options.draggable) {
				google.maps.event.addListener(marker, 'dragend',
					function() {
						if(typeof bambu !== 'undefined') {
							if('mapping' in bambu) {
								var pos = marker.getPosition();
								bambu.mapping.fire('markerDragged',
									{
										marker: marker,
										latitude: pos.lat(),
										longitude: pos.lng()
									}
								);
							}
						}
					}
				);
			}
			
			return marker;
		}""" % {
			'map_varname': self.get_map_varname()
		}
	
	def remove_marker(self):
		return 'function(marker) { marker.setMap(null); }'
	
	def find_address(self):
		return """function(latitude, longitude, callback) {
			new google.maps.Geocoder().geocode(
				{
					latLng: new google.maps.LatLng(latitude, longitude)
				},
				function(responses) {
					if (responses && responses.length > 0) {
						if(typeof callback !== 'undefined') {
							callback(
								{
									latitude: responses[0].geometry.location.lat(),
									longitude: responses[0].geometry.location.lng(),
									address: responses[0].formatted_address
								}
							);
						}
					} else {
						alert("Sorry, it's not possible to find an address for this location.");
					}
				}
			);
		}"""
	
	def find_coords(self):
		return """function(address, callback) {
			new google.maps.Geocoder().geocode(
				{
					address: address
				},
				function(responses) {
					if (responses && responses.length > 0) {
						if(typeof callback !== 'undefined') {
							callback(
								{
									latitude: responses[0].geometry.location.lat(),
									longitude: responses[0].geometry.location.lng(),
									address: responses[0].formatted_address
								}
							);
						}
					} else {
						alert("Sorry, it's not possible to find this address.");
					}
				}
			);
		}"""
	
	def set_centre(self):
		return """function(latitude, longitude) {
			%s.setCenter(new google.maps.LatLng(latitude, longitude));
		}""" % self.get_map_varname()
	
	def get_image_url(self):
		kwargs = {
			'sensor': 'false'
		}
		
		if 'zoom' in self.settings:
			kwargs['zoom'] = self.settings['zoom']
		
		if 'lat' in self.settings and 'lon' in self.settings:
			kwargs['center'] = ','.join(
				(
					self.settings['lat'],
					self.settings['lon']
				)
			)
		
		if 'width' in self.settings and 'height' in self.settings:
			kwargs['size'] = '%dx%d' % (
				self.settings['width'], self.settings['height']
			)
		
		if self.settings.get('marker'):
			kwargs['markers'] = '|%s,%s' % (
				self.settings['lat'],
				self.settings['lon']
			)
		
		return '//maps.googleapis.com/maps/api/staticmap?%s' % urlencode(kwargs)
	
	class Media:
		js = ('//maps.googleapis.com/maps/api/js?key=%(api_key)s&amp;sensor=false',)