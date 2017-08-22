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
            socket.emit('clickEvent', {name: $(this).attr('alt')});
        });

});
