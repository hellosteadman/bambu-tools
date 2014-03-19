if(typeof(bambu) == 'undefined') {
	bambu = {};
}

bambu.fileupload = {
	init: function(context, handlerURL, callback, deleteHandlerURL) {
		var zone = $('#' + context);
		var input = $('#' + context + '_input');
		var dropZoneTimeout = null;
		var originalHTML = zone.html();
		
		zone.data('bambu.fileupload.handler', handlerURL);
		if(typeof(deleteHandlerURL) != 'undefined') {
			zone.data('bambu.fileupload.handler.delete', deleteHandlerURL);
		}
		
		function getCookie(name) {
			var cookieValue = null;
			if (document.cookie && document.cookie != '') {
				var cookies = document.cookie.split(';');
				for (var i = 0; i < cookies.length; i++) {
					var cookie = $.trim(cookies[i]);
					if (cookie.substring(0, name.length + 1) == (name + '=')) {
						return decodeURIComponent(cookie.substring(name.length + 1));
					}
				}
			}
		}
		
		function createUploader() {
			var csrftoken = getCookie('csrftoken');
			
			input.fileupload(
				{
					dataType: 'json',
					url: handlerURL,
					dropZone: zone,
					pasteZone: zone,
					singleFileUploads: false,
					add: function(e, data) {
						var addFiles = 0;
						
						$.each(data.files,
							function(index, file) {
								if(typeof(file.size) == 'number' && file.size > 0) {
									addFiles ++;
								}
								
								if(addFiles == 1) {
									$(document).trigger('fileupload:start');
								}
							}
						);
						
						if(addFiles == 0) {
							return;
						}
						
						zone.addClass('full').removeClass('error').html(
							'<div class="progress"><div class="progress-bar"></div></div>' +
							'<small>Calculating time remaining</small>'
						);
						
						data.submit();
					},
					progressall: function(e, data) {
						if(!data.total) {
							return;
						}
						
						var progress = data.loaded / data.total * 100;
						var kbps = Math.round(
							data.bitrate / 1024, 0
						).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
						
						zone.find('.progress .progress-bar').css('width', progress + '%');
						if(progress >= 100) {
							zone.find('small').html('Finishing up');
						} else {
							zone.find('small').html('Uploading at ' + kbps + 'kbps');
						}
					},
					done: function(e, data) {
						zone.removeClass('full').html(originalHTML);
						$(document).trigger('fileupload:done');
						callback(data);
						
						input = $('#' + context + '_input');
						createUploader();
					},
					error: function(e, data) {
						zone.addClass('error').find('small').html(
							'Errors occurred during the upload. Please try again'
						);
					}
				}
			);
		}
		
		createUploader();
		
		$(document).bind('dragover',
			function(e) {
				if (!dropZoneTimeout) {
					zone.addClass('in');
				} else {
					clearTimeout(dropZoneTimeout);
				}
				
				if (e.target === zone[0]) {
					zone.addClass('hover');
				} else {
					zone.removeClass('hover');
				}
				
				dropZoneTimeout = setTimeout(
					function() {
						dropZoneTimeout = null;
						zone.removeClass('in hover');
					}, 100
				);
			}
		);
	},
	addAttachment: function(e) {
		var ul, modal, modalID, li, a, text, parts, extension, del;
		var id = e.dropZone.attr('id');
		var deleteHandler = e.dropZone.data('bambu.fileupload.handler.delete');
		var deleted = e.dropZone.data('bambu.fileupload.deleted');
		
		if(!e.dropZone.data('bambu.fileupload.filelist')) {
			ul = $('<ul class="fileupload-filelist"></ul>');
			e.dropZone.after(ul);
			e.dropZone.data('bambu.fileupload.filelist', ul);
		} else {
			ul = e.dropZone.data('bambu.fileupload.filelist');
		}
		
		for(var i = 0; i < e.result.length; i ++) {
			if(typeof(deleted) != 'undefined' && e.result[i].url in deleted) {
				continue;
			}
			
			text = e.result[i].name;
			parts = e.result[i].url.split('.');
			extension = parts[parts.length - 1];
			modalID = id + '-preview-modal-' + (ul.find('li').length + 1);
			li = $('<li></li>').addClass('file ' + extension);
			
			if(e.result[i].type && e.result[i].type.substr(0, 6) == 'image/') {
				modal = $(
					'<div id="' + modalID + '" class="modal fade fileupload-image-preview" role="dialog">' +
						'<div class="modal-dialog modal-lg">' +
							'<div class="modal-header">' +
								'<a class="close" data-dismiss="modal" href="javascript:;">x</a>' +
							'</div>' +
							'<div class="modal-content">' +
								'<div class="modal-body">' +
									'<img style="max-width: 100%; margin: 0 auto; display: block;">' +
								'</div>' +
							'</div>' +
						'</div>' +
					'</div>'
				);
				
				modal.find('img').attr('src', e.result[i].url);
				$(document).find('body').append(modal);
				a = $('<a class="download" href="#' + modalID + '" data-toggle="modal"></a>');
			} else {
				a = $('<a class="download" download></a>');
				a.attr('href', e.result[i].url);
			}
			
			a.html(text);
			li.attr('data-url', e.result[i].url);
			li.append(a);
			
			if(deleteHandler) {
				del = $('<a class="fileupload-delete" href="javascript:bambu.fileupload.deleteAttachment(\'' + escape(id) + '\', \'' + escape(e.result[i].url) + '\');"><small>&times;</small></a>');
				li.append(del);
			}
			
			ul.append(li);
		}
	},
	deleteAttachment: function(context, fileURL) {
		var guid = $('input[name="_bambu_fileupload_guid"]').val();
		var zone = $('#' + context);
		var handlerURL = zone.data('bambu.fileupload.handler.delete');
		
		$('.fileupload-filelist li[data-url="' + fileURL + '"] a').attr('disabled');
		jQuery.ajax(
			{
				url: handlerURL + '&f=' + fileURL,
				method: 'POST',
				dataType: 'json',
				context: zone,
				success: function() {
					var deleted = $(this).data('bambu.fileupload.deleted');
					
					if(typeof(deleted) == 'undefined') {
						deleted = [];
					}
					
					deleted.push(fileURL);
					$(this).data('bambu.fileupload.deleted', deleted);
					$('.fileupload-filelist li[data-url="' + fileURL + '"]').remove();
				}
			}
		);
	},
	list: function(context, handlerURL) {
		jQuery.ajax(
			{
				url: handlerURL,
				dataType: 'json',
				context: $('#' + context),
				success: function(files) {
					var zone = $(this);
					var context = zone.attr('id');
					var ul, modal, modalID, li, a, text, parts, extension, del;
					var deleteHandler = zone.data('bambu.fileupload.handler.delete');
					var deleted = zone.data('bambu.fileupload.deleted');
					
					if(!zone.data('bambu.fileupload.filelist')) {
						ul = $('<ul class="fileupload-filelist"></ul>');
						zone.after(ul);
						zone.data('bambu.fileupload.filelist', ul);
					} else {
						ul = zone.data('bambu.fileupload.filelist');
					}
					
					for(var i = 0; i < files.length; i ++) {
						if(typeof(deleted) != 'undefined' && files[i].url in deleted) {
							continue;
						}
						
						text = files[i].name;
						parts = files[i].url.split('.');
						extension = parts[parts.length - 1];
						modalID = context + '-preview-modal-' + (ul.find('li').length + 1);
						li = $('<li></li>').addClass('file ' + extension);
						
						if(files[i].type && files[i].type.substr(0, 6) == 'image/') {
							modal = $(
								'<div id="' + modalID + '" class="modal fade fileupload-image-preview" role="dialog">' +
									'<div class="modal-dialog modal-lg">' +
										'<div class="modal-header">' +
											'<a class="close" data-dismiss="modal" href="javascript:;">x</a>' +
										'</div>' +
										'<div class="modal-content">' +
											'<div class="modal-body">' +
												'<img style="max-width: 100%; margin: 0 auto; display: block;">' +
											'</div>' +
										'</div>' +
									'</div>' +
								'</div>'
							);
							
							modal.find('img').attr('src', files[i].url);
							$(document).find('body').append(modal);
							a = $('<a class="download" href="#' + modalID + '" data-toggle="modal"></a>');
						} else {
							a = $('<a class="download" download></a>');
							a.attr('href', files[i].url);
						}
						
						a.html(text);
						li.attr('data-url', files[i].url);
						li.append(a);
						
						if(deleteHandler) {
							del = $('<a class="fileupload-delete" href="javascript:bambu.fileupload.deleteAttachment(\'' + escape(context) + '\', \'' + escape(files[i].url) + '\');"><small>&times;</small></a>');
							li.append(del);
						}
						
						ul.append(li);
					}
				}
			}
		);
	}
};

jQuery(document).ready(
	function($) {
		$(document).on('drop dragover',
			function(e) {
				e.preventDefault();
			}
		);
	}
);