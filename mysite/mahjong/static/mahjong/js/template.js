window.onload = function getHeader() {
    // $.ajax({
    //     url : '/static/mahjong/templates/templateHeader.html',
    //     dataType: 'html',
    //     success : function (data) {
    //         $('#header').html(data);
    //     }
    // });
    $.ajax({
        url: '/static/mahjong/templates/templateFooter.html',
        dataType: 'html',
        success: function (data) {
            $('#footer').html(data);
        }
    });
}
