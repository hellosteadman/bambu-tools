if(typeof(bambu) == 'undefined') {
    bambu = {};
}

if(typeof(bambu.analytics) == 'undefined') {
    bambu.analytics = (
        function() {
            var callbacks = {};

            function fire(evt, data) {
                if(typeof(callbacks[evt]) != 'undefined') {
                    for(var i = 0; i < callbacks[evt].length; i ++) {
                        callbacks[evt][i](data);
                    }
                }
            }

            return {
                PAGE: 'page',
                EVENT: 'event',
                TRANSACTION: 'transaction',
                TRANSACTION_ITEM: 'transaction_item',
                on: function(evt, callback) {
                    if(typeof(callbacks[evt]) == 'undefined') {
                        callbacks[evt] = [];
                    }

                    callbacks[evt].push(callback);
                },
                track: function(evt, args) {
                    fire('track',
                        {
                            'event': evt,
                            'args': args
                        }
                    );
                }
            }
        }
    )();
}
