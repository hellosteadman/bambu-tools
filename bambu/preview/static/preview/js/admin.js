(
	function($) {
		$(document).ready(
			function() {
				$('.object-tools a.previewlink').bind('click',
					function(e) {
						var modelForm = $('form');
						var attr = modelForm.attr('data-og-action');
						
						if (typeof attr == 'undefined') {
							modelForm.attr('data-og-action', modelForm.attr('action'));
							modelForm.attr('data-og-target', modelForm.attr('target'));
							
							modelForm.attr('action', 'preview/');
							modelForm.attr('target', '_blank');
						}
						
						modelForm.submit();
						e.preventDefault();
					}
				).closest('li').show();
				
				$('form :input[type="submit"]').bind('click',
					function(e) {
						var modelForm = $(this).closest('form');
						var attr = modelForm.attr('data-og-action');
						
						if (typeof attr !== 'undefined') {
							modelForm.attr('action', modelForm.attr('data-og-action'));
							modelForm.attr('target', modelForm.attr('data-og-target'));
							
							modelForm.removeAttr('data-og-action');
							modelForm.removeAttr('data-og-target');
						}
					}
				);
			}
		);
	}
)(django.jQuery);