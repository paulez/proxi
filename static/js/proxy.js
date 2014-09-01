// setup X-CSFR Django cookie

// using jQuery
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
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$(document).ready( function(){
    if(navigator.geolocation){
        navigator.geolocation.getCurrentPosition(
            geo_success, geo_error, {maximumAge:300000, timeout:2000}
        );
    } else {
        alert("geolocation not enabled");
    }
});

function cancelButton(){
    clearWatch(watchId);
}

function geo_success(position){
    $.post("/set_position/", JSON.stringify({
        "type": "Point",
        "coordinates": [
            position.coords.longitude,
            position.coords.latitude
        ]
    }));
}

function geo_error(error){
    alert("geo error");
}
