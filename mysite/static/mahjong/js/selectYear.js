window.onload = function setSelectYear() {
    var cookies = document.cookie;
    var keystr = "selectYear=";
    var matchPos = cookies.indexOf(keystr);

    var cookieValue = "";

    if (matchPos != -1) {
        var valueStart = matchPos + keystr.length
        var valueEnd = cookies.indexOf(";", valueStart);
        if (valueEnd != -1) {
            cookieValue = cookies.substring(valueStart, valueEnd);
        } else {
            cookieValue = cookies.substring(valueStart);
        }
        cookieValue = unescape(cookieValue);

    }
    if (cookieValue == 'allYear') {
      cookieValue = '通算'
    }
    document.getElementById("select-show").innerHTML = cookieValue;

    var checkOption = document.getElementsByName('selectYear');

    checkOption.forEach(function (e) {
        e.addEventListener("click", function () {
            val = document.querySelector("input:checked[name=selectYear]").value;
            document.cookie = "selectYear=" + val + "; path=/;"
            if (val == 'allYear') {
              val = '通算'
            }
            document.getElementById("select-show").innerHTML = val;
        });
    });
}
