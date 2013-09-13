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
	init: function(id, pushState, basePath) {
		try {
			console.log('Setting up grid', id);
		} catch (err) {
			// Can't log to console
		}
		
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
						
						try {
							console.log('Abandon ship. We seem to have some cross-grid contamination.');
						} catch (err) {
							// Can't log to console
						}
						
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
				
				console.log('Pushing state');
				window.history.pushState(data, '', url);
			}
			
			bambu.grids.push(id, url, pushState);
		}
		
		$('#grid_' + id).find('.pagination a').bind('click',
			function(e) {
				try {
					console.log('Responding to AJAX link');
				} catch(err) {
					// Can't log to console
				}
				
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
				
				try {
					console.log('Responding to AJAX form action');
				} catch(err) {
					// Can't log to console
				}
				
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
					
					try {
						console.log('Got AJAX response');
					} catch(err) {
						// Can't log to console
					}
					
					if(grid.length > 0) {
						dom.filter('script').each(
							function() {
								$.globalEval(this.text || this.textContent || this.innerHTML || '');
							}
						);
						
						try {
							console.log('Replacing grid with AJAXed version');
						} catch(err) {
							// Can't log to console
						}
						
						$('#grid_' + id).replaceWith(grid).find('.bambu-grid-filter-form :input').bind('change',
							function(e) {
								$(this).closest('.bambu-grid-filter-form').submit();
							}
						);
						
						bambu.grids.init(id, pushState);
					} else {
						try {
							console.log('Can\'t find the same grid in this response');
						} catch(err) {
							// Can't log to console
						}
						
						document.location = url;
					}
				}
			}
		);
	}
}