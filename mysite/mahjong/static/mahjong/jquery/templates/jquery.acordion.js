$(function () {
    $('.js-menu__item__link').each(function () {
        $(this).on('click', function () {
            $("+.submenu", this).slideToggle();
            return false;
        });
    });
});
