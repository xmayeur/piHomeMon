$(document).ready(function () {
        $('ul.nav > li').click(function (e) {
            $('ul.nav > li').removeClass('active');
            $(this).addClass('active');
            $('div.active').removeClass('active').hide();
            var id = $(this).attr("id");
            $('#'+id+'Div').addClass('active').show()
        });
    });