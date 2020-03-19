function initMap() {
    mapboxgl.accessToken = 'pk.eyJ1IjoiemFjaGFyeTgxNiIsImEiOiJjazd6NXN2eWwwMml0M2tvNGo2c3JkcGFpIn0.aB1upejZ61JQjb_z2g1NuA';
    var map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/mapbox/streets-v11',
        center: [-74.0060, 40.7128],
        zoom: 9
    });

    map.addControl(new mapboxgl.NavigationControl());
}

function addMarker(lat, lng) {
    var marker = new google.maps.Marker({
        position:{lat:lat,lng:lng}
    });
}

function loadJSON() {
    var input = document.getElementById("json-script").value;
    console.log("Attempting to load: " + input);
    fetch("json/sinha_2020_FEBRUARY.json").then(response => response.json()).then(json => {
        console.log(json);
    });
}

function loadedJSON(json) {

}

initMap();