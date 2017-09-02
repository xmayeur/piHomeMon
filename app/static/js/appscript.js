$(document).ready(function () {

        var socket = io.connect();

        // request updates every 30 sec
        setInterval(function() {
            socket.emit('refresh', 'refresh devices state')
        }, 30000);

        // handle refresh response
        socket.on('refreshResponse', function(msg) {
            $('img[alt="'+msg.alt+'"]').attr('src', msg.pict);

        });

        // handle click on node's image
        $('div.device img').click(function(){

            if ( $(this).hasClass('active') ) {
                socket.emit('clickEvent', {name: $(this).attr('alt')});
                $(this).removeClass('active').addClass('busy');
                $("#spinner").show();
            }

        });

        // re-activate a clickable icon
        socket.on('reactivateImg', function(msg) {
            $('img[alt="'+msg.alt+'"]').removeClass('busy').addClass('active');
            $("#spinner").hide();
        });

        // spinner show/hide here
        socket.on('spinnerShow', function() {
            $("#spinner").show();
        });
        socket.on('spinnerHide', function() {
            $("#spinner").hide();
        });

        // slider function
        $( function() {
            var handle = $( "#sliderHandle" );


            $( "#slider" ).slider({

            range: "min",
            max: 100,

            create: function(event, ui) {
                // expected to have a hidden <input> tag with the initial value
                $(this).slider("value", $("#sliderVal").val() );
                handle.text( $( this ).slider( "value" ));
                },

            slide: function(event, ui) {
                socket.emit('getSlider', {
                    value: ui.value,
                    name: $(this).closest('h3').text()
                    })
                handle.text( ui.value );

                }
            });

            // set slider value
            socket.on('setSlider', function(msg){
                $( "#slider" ).slider("value", msg.value);
                handle.text( msg.value );
            });

        });

});

