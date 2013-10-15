from bambu.mapping.providers.base import ProviderBase
from django.utils.http import urlencode
from django.conf import settings
from django.core.urlresolvers import reverse

class OpenStreetMapProvider(ProviderBase):
	def init_map(self):
		controls = self.settings.get('controls', ('ZOOM', 'ATTRIBUTION'))
		
		return """%(varname)s = new L.Map('%(id)s',
			{
				zoomControl: %(zoomControl)s,
				attributionControl: %(attributionControl)s
			}
		);
		
		%(varname)s.setView(
			new L.LatLng(%(lat)s, %(lon)s), %(zoom)d
		).addLayer(
			new L.TileLayer('http://{s}.tile.cloudmade.com/%(api_key)s/997/256/{z}/{x}/{y}.png',
				{
					attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery &copy; <a href="http://cloudmade.com">CloudMade</a>',
					maxZoom: 30
				}
			)
		);
		""" % {
			'varname': self.get_map_varname(),
			'id': self.container_id,
			'api_key': self.settings.get('api_key'),
			'lat': self.settings.get('lat', 'null'),
			'lon': self.settings.get('lon', 'null'),
			'zoom': self.settings.get('zoom', 10),
			'zoomControl': ('ZOOM' in controls) and 'true' or 'false',
			'attributionControl': ('ATTRIBUTION' in controls) and 'true' or 'false'
		}
	
	def add_marker(self):
		return """function(options) {
			var pos = new L.LatLng(options.lat, options.lon);
			var marker = new L.Marker(pos,
				{
					draggable: options.draggable
				}
			);
			
			%(map_varname)s.addLayer(marker);
			
			if(options.content) {
				var infowindow = new L.Popup(
					{
						autoPan: true,
						offset: new L.Point(0, -16)
					}
				);
				
				infowindow.setContent(options.content);
				infowindow.setLatLng(pos);
				
				marker.on('click',
					function() {
						%(map_varname)s.openPopup(infowindow);
					}
				);
			}
			
			if(options.draggable) {
				marker.on('dragend',
					function() {
						if(typeof bambu !== 'undefined') {
							if('mapping' in bambu) {
								var pos = marker.getLatLng();
								bambu.mapping.fire('markerDragged',
									{
										marker: marker,
										latitude: pos.lat,
										longitude: pos.lng
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
		return 'function(marker) { %s.removeLayer(marker); }' % self.get_map_varname()
	
	def find_address(self):
		url = reverse('bambu_mapping_json_funnel')
		return """function(latitude, longitude, callback) {
			$.getJSON(
				'""" + url + """?url=' + escape(
					'http://nominatim.openstreetmap.org/reverse?lat=' + latitude +
					'&lon=' + longitude + '&format=json'
				) + '&json_callback=?',
				function(data) {
					if(data.lat && data.lon) {
						if(typeof callback !== 'undefined') {
							callback(
								{
									latitude: parseFloat(data.lat),
									longitude: parseFloat(data.lon),
									address: data.display_name
								}
							);
						}
					} else {
						alert("Sorry, it's not possible to find an address for this location.");
					}
				}
			)
		}"""
	
	def find_coords(self):
		url = reverse('bambu_mapping_json_funnel')
		return """function(address, callback) {
			$.getJSON(
				'""" + url + """?url=' + escape(
					'http://nominatim.openstreetmap.org/search?q=' + address +
					'&format=json'
				) + '&json_callback=?',
				function(data) {
					if(data.length > 0) {
						if(typeof callback !== 'undefined') {
							callback(
								{
									latitude: parseFloat(data[0].lat),
									longitude: parseFloat(data[0].lon),
									address: data[0].display_name
								}
							);
						}
					} else {
						alert("Sorry, it's not possible to find this address.");
					}
				}
			)
		}"""
	
	def set_centre(self):
		return """function(latitude, longitude) {
			%s.panTo(new L.LatLng(latitude, longitude));
		}""" % (
			self.get_map_varname(),
		)
	
	def get_image_url(self):
		kwargs = {}
		
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
			kwargs['marker'] = '%s,%s' % (
				self.settings['lat'],
				self.settings['lon']
			)
		
		return '//staticmaps.cloudmade.com/%s/staticmap?%s' % (
			self.settings['api_key'],
			urlencode(kwargs)
		)
	
	class Media:
		js = (settings.STATIC_URL + 'mapping/leaflet/leaflet.js'),
		css = (settings.STATIC_URL + 'mapping/leaflet/leaflet.css',)