$(function () {
    $('.js-menu__item__link').each(function () {
        $(this).on('click', function () {
            $("+.submenu", this).slideToggle();
            return false;
        });
    });
});
//
// $(function () {
//     $('.-hora').each(function () {
//         $(this).addEventListener('click', function () {
//             $(".submenu", this).slideToggle();
//             return false;
//         });
//     });
// });
