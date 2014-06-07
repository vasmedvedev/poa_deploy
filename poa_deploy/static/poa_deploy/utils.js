//commentd
var $interceptForm = function(form, outputElem, additionalParams) { //Inputs are JQuery objects, add params is json
    form.submit(function( event ) {
        var csrftoken = getCookie('csrftoken');
        var postURL = $( this ).attr( "action" );
        var postData = $( this ).serializeArray();
        postData.push({name: 'csrfmiddlewaretoken', value: csrftoken});
        if (additionalParams !== "undefined") {
            postData.push(additionalParams);
        }
        $.ajax({
            url: postURL,
            type: "POST",
            data: postData,
            success: function(data) {
                if (data['status'] == 0) {
                    outputElem.html( data['result'] ).css("color", "green");
                } else {
                    outputElem.html( data['result'] ).css("color", "red");
                }
            } // success function
        }); // $.ajax
        event.preventDefault();
    }); // $( form )
}// var $interceptForm

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
         }
    }
    return cookieValue;
}
