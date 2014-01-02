(
	function($) {
		$(document).ready(
			function() {
				var editor = CodeMirror.fromTextArea(
					document.forms[0].css,
					{
						mode: 'text/css',
						lineNumbers: false,
						matchBrackets: true,
						indentUnit: 4,
						indentWithTabs: true,
						enterMode: 'keep',
				        tabMode: 'shift'
					}
				);
			}
		);
	}
)(django.jQuery);