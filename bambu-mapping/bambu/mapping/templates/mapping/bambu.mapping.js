if(typeof bambu == 'undefined') {
	bambu = {};
}

if(!('_events' in bambu)) {
	bambu._events = {};
}

if(!('mapping' in bambu._events)) {
	bambu._events.mapping = {};
}

bambu.mapping = {
	findAddress: {{ provider.find_address|safe }},
	findCoords: {{ provider.find_coords|safe }},
	clearMap: function() {
		while(bambu.mapping.markers['{{ provider.container_id }}'].length > 0) {
			({{ provider.remove_marker|safe }})(
				bambu.mapping.markers['{{ provider.container_id }}'].pop()
			);
		}
	},
	markers: {},
	setCentre: function(latitude, longitude) {
		({{ provider.set_centre|safe }})(latitude, longitude);
	},
	on: function(evt, func) {
		if(!(evt in bambu._events.mapping)) {
			bambu._events.mapping[evt] = [func];
		} else {
			bambu._events.mapping[evt].push(func);
		}
	},
	fire: function(evt, data) {
		if(evt in bambu._events.mapping) {
			for(var i = 0; i < bambu._events.mapping[evt].length; i ++) {
				bambu._events.mapping[evt][i](data);
			}
		}
	},
	addMarker: function(options) {
		var callback = null;
		
		if('callback' in options) {
			callback = options['callback'];
			delete(options['callback']);
		}
		
		var marker = ({{ provider.add_marker|safe }})(options);
		
		bambu.mapping.markers['{{ provider.container_id }}'].push(marker);
		
		if(callback != null) {
			callback(marker);
		}
	}
}