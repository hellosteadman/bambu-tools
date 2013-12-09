if(typeof bambu == 'undefined') {
	bambu = {};
}

if(!('_events' in bambu)) {
	bambu._events = {};
}

if(!('grids' in bambu._events)) {
	bambu._events.grids = {};
}

bambu.grids = {
	on: function(evt, func) {
		if(!(evt in bambu._events.grids)) {
			bambu._events.grids[evt] = [func];
		} else {
			bambu._events.grids[evt].push(func);
		}
	},
	fire: function(evt, data) {
		if(evt in bambu._events.grids) {
			for(var i = 0; i < bambu._events.grids[evt].length; i ++) {
				bambu._events.grids[evt][i](data);
			}
		}
	},                              
	init: function(id, pushState, basePath) {
		console && console.log('Setting up grid', id);
		
		if(!basePath) {
			basePath = '.';
		}
		
		function submitGrid(url) {
			if($(this).attr('disabled')) {
				return;
			}
			
			if(!url) {
				url = basePath;
			}
			
			var q = url.indexOf('?');
			if(q > -1) {
				var parts = url.substr(q + 1).split('&');
				
				url = url.substr(0, q + 1);
				for(var i = 0; i < parts.length; i ++) {
					var split = parts[i].split('=');
					var key = split[0];
					var value = unescape(split[1]);
					
					if(key == '_bambu_grid') {
						if(value == id) {
							continue;
						}
						
						console && console.log('Abandon ship. We seem to have some cross-grid contamination.');
						return;
					}
					
					url += key + '=' + escape(value);
					if(i < parts.length - 1) {
						url += '&';
					}
				}
			}
			
			if (pushState && window.history && window.history.pushState) {
				var data = {
					grid: id
				};
				
				console && console.log('Pushing state');
				window.history.pushState(data, '', url);
			}
			
			bambu.grids.push(id, url, pushState);
		}
		
		$('#grid_' + id).find('.pagination a').bind('click',
			function(e) {
				console && console.log('Responding to AJAX link');
				e.preventDefault();
				submitGrid($(this).attr('href'));
			}
		);
		
		$('#grid_' + id).find('.bambu-grid-filter-form').bind('submit',
			function(e) {
				var url = $(this).attr('action');
				
				e.preventDefault();
				if($(this).data('submitting')) {
					return;
				}
				
				console && console.log('Responding to AJAX form action');
				
				$(this).data('submitting', true);
				if(!url) {
					url = '';
				}
				
				if(url.indexOf('?') > -1) {
					url += '&';
				} else {
					url += '?';
				}
				
				url += $(this).find(':input').serialize();
				submitGrid(url);
			}
		);
	},
	push: function(id, url, pushState) {
		if(typeof pushState == 'undefined') {
			pushState = true;
		}
		
		if(!url) {
			url = '';
		}
		
		if(url.indexOf('?') > -1) {
			url += '&';
		} else {
			url += '?';
		}
		
		$('#grid_' + id).find('a, :input').attr('disabled', 'disabled');
		
		url += '_bambu_grid=' + id;
		$.ajax(
			{
				url: url,
				dataType: 'html',
				success: function(html) {
					var dom = $(html);
					var grid = dom.find('#grid_' + id);
					
					console && console.log('Got AJAX response');
					if(grid.length > 0) {
						dom.filter('script').each(
							function() {
								$.globalEval(this.text || this.textContent || this.innerHTML || '');
							}
						);                             
						
						console && console.log('Replacing grid with AJAXed version');
						
						$('#grid_' + id).replaceWith(grid);
						bambu.grids.init(id, pushState);
						bambu.grids.fire('rebound', grid);
						
						grid.find('.bambu-grid-filter-form :input').bind('change',
							function(e) {
								$(this).closest('.bambu-grid-filter-form').submit();
							}
						);
					} else {
						console && console.log('Can\'t find the same grid in this response');
						document.location = url;
					}
				}
			}
		);
	}
}