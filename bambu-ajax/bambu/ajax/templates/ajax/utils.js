if(typeof(bambu) == 'undefined') {
    bambu = {};
}

bambu.ajax = (
    function() {
        var self = {};

        self.url = function(name, params) {
            var url = '{% url 'ajax_endpoint' %}?f=' + name;

            if(typeof(params) == 'object') {
                for(var key in params) {
                    url += '&' + escape(key) + '=' + escape(params[key]);
                }
            }

            return url;
        };

        self.get = function(urlname, params, success, error) {
            if(typeof(success) == 'undefined') {
                success = function(data) {
                    if(typeof(console) != 'undefined') {
                        console.log(data);
                    }
                };
            }

            if(typeof(error) == 'undefined') {
                error = function(data) {
                    if(typeof(console) != 'undefined') {
                        console.error(data);
                    }
                };
            }

            if(typeof(params) == 'function') {
                success = params;
                params = {};
            } else if(typeof(params) == 'undefined') {
                params = {};
            }

            if(typeof(jQuery) != 'undefined') {
                jQuery.ajax(
                    {
                        method: 'GET',
                        url: self.url(urlname, params),
                        success: success,
                        error: function(xhr, status, err) {
                            error(xhr.responseText);
                        }
                    }
                );
            }
        };

        return self;
    }
)();
