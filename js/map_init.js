// Global objects
let map = null;         // Mapbox GL object
let geojson = null;     // geojson object
let positions = null;   // 2D array of longitude and latitude

// initializer functions -------------------------------------------------------
// main initializer
function mainInit() {
    positions = [[-74.006042, 40.712769], [-74.005811, 40.713033], [-74.005505, 40.713399]];
    initGeo();
    initMap(positions[0]);
    $("#uploadForm").submit(loadJSON)
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
    map.on('load', function () {
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
function populateLines(json_data) {
    console.log("Populating lines");
    positions = new Array(0);
    console.log(json_data.length + " location objects found.");
    for (var i = 0; i < json_data.length; i++) {
        var nearby = json_data[i].nearby;
        if (nearby) {
            for (var place in nearby) {
                coords = nearby[place]["coordinates"]
                if (coords) {
                    positions.push([coords['lon'], coords['lat']]);
                }
            }
        }
    }
    // reload map
    console.log("Reloading map with new positional data.");
    initGeo();
    initMap(positions[0]);
    document.getElementById("response-div").innerHTML = contributeForm;
    $("#loginModal")[0].style.display="none";

}

// load JSON function called from button press
function loadJSON(e) {
    formdata = new FormData();
    file = $("#file").prop('files')[0];
    formdata.append('jsonFile', file);
    console.log("Calling ajax! with " + $("#file").prop('files').length + " file");
    $.ajax({
        method: "POST",
        url: "http://173.28.146.185:5000/handleUpload",
        data: formdata,
        processData: false,
        contentType: false,
        success: function (data) {
            // console.log(data);
            json_data = JSON.parse(data);
            populateLines(json_data);
        }
    });
    e.preventDefault();

}

// call methods -------------------------------------------
mainInit();