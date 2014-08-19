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
    alert("Found you at latitude " + position.coords.latitude +
          ", longitude " + position.coords.longitude);
    $.ajax({
        type: "POST",
        url: "/set_position",
        data: {
            "latitude": position.coords.latitude,
            "longitude": position.coords.longitude,
        },
    });
}

function geo_error(error){
    alert("geo error");
}
