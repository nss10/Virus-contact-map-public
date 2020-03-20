// Global objects
let map = null;         // Mapbox GL object
let geojson = null;     // geojson object
let positions = null;   // 2D array of longitude and latitude

// initializer functions -------------------------------------------------------
// main initializer
function mainInit() {
    positions = [[-74.006042, 40.712769],[-74.005811, 40.713033],[-74.005505, 40.713399]];
    initGeo();
    initMap(positions[0]);
}

// initializes map
function initMap(pos) {
    mapboxgl.accessToken = 'pk.eyJ1IjoiemFjaGFyeTgxNiIsImEiOiJjazd6NXN2eWwwMml0M2tvNGo2c3JkcGFpIn0.aB1upejZ61JQjb_z2g1NuA';
    map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/mapbox/streets-v11',
        center: [pos[0], pos[1]],
        zoom: 9
    });

    map.addControl(new mapboxgl.NavigationControl());

    // init of map with blank geojson
    map.on('load', function() {
        map.addSource('line', {
            'type': 'geojson',
            'data': geojson
        });
        map.addLayer({
            'id': 'line-animation',
            'type': 'line',
            'source': 'line',
            'layout': {
                'line-cap': 'round',
                'line-join': 'round'
            },
            'paint': {
                'line-color': '#F7455D',
                'line-width': 3
            }
        });
    });
}

// initializes geojson
function initGeo() {
    // init for geojson
    geojson = {
        'type': 'FeatureCollection',
        'features': [
            {
                'type': 'Feature',
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [[0, 0]]
                }
            }
        ]
    };
    // Test data load
    geojson.features[0].geometry.coordinates = [];
    positions.forEach(pos => geojson.features[0].geometry.coordinates.push(pos));
}

// function functions -------------------------------------------------------------
// populates the geojson object with points
function populateLines(json) {
    console.log("Populating lines");
    positions = new Array(0);
    for (var i = 0; i < json.timelineObjects.length; i++) {
        if (i % 2 == 1) {
            console.log(json.timelineObjects[i].placeVisit);
            positions.push([json.timelineObjects[i].placeVisit[0].location.longitudeE7 / 1000000,
                json.timelineObjects[i].placeVisit.location.latitudeE7 / 1000000]);
        }
    }
    console.log(positions);
    // reload map
    console.log("Reloading map with new positional data.");
    initGeo();
    initMap(positions[0]);
}

// load JSON function called from button press
function loadJSON() {
    var input = document.getElementById("json-script").value;
    console.log("Attempting to load: " + input);
    // retreives json object from http and https sources only
    fetch(input).then(response => response.json()).then(json => {
        populateLines(json);
    });
}

// call methods -------------------------------------------
mainInit();