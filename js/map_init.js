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
        map.addSource('point', {
            'type': 'geojson',
            'data': geojson
        });
        map.addLayer({
            'id': 'user-position',
            'type': 'circle',
            'source': 'point',
            'paint': {
                'circle-radius': {
                    'base': 3.75,
                    'stops': [[18, 3], [33, 270]]
                },
                'circle-color': '#F7455D'
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
            var placeVisit = json['timelineObjects'][i]['placeVisit'];
            if (placeVisit)
                positions.push([placeVisit['location']['longitudeE7'] / 10000000, placeVisit['location']['latitudeE7'] / 10000000]);
        }
    }
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