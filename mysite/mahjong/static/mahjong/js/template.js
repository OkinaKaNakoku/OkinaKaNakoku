window.onload = function getHeader(){
    $.ajax({
        url : '/static/mahjong/templates/templateHeader.html',
        dataType: 'html',
        success : function (data) {
            $('#header').html(data);//A
        }
    });
}