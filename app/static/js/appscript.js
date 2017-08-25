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

        // re-activate clickable icon
        socket.on('reactivateImg', function(msg) {
            $('img[alt="'+msg.alt+'"]').removeClass('busy').addClass('active');
            $("#spinner").hide();
        });

        // spinner show/hide here
});
