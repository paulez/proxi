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

var geo_options = {
    enableHighAccuracy: false,
    // 1 minute
    maximumAge: 60000,
};

var low_geo_options = {
    enableHighAccuracy: false,
    // 3 minutes
    maximumAge: 180000,
    // 20 seconds
    timeout: 20000,
}

$(document).ready( function(){
    if(navigator.geolocation){
        navigator.geolocation.getCurrentPosition(
            first_geo_success, geo_error, low_geo_options
        );
    } else {
        console.warn('Geolocation not enabled');
    }
    var $container = $("#main");
    var refreshId = setInterval(function()
            {
                $container.load('ajax_messages');
            }, 60 * 1000);
});

function first_geo_success(position){
    geo_success(position);
    // retry now with high accuracy
    geo_accurate();
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

function geo_accurate(){
    //retrying wih high accuracy
    navigator.geolocation.getCurrentPosition(
        geo_success, geo_error, geo_options
    );
}

function geo_error(error){
    console.warn('ERROR(' + error.code + '): ' + error.message);
}
