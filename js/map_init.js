// Global objects
let map = null;         // Mapbox GL object
let geojson = null;     // geojson object
let positions = null;   // 2D array of longitude and latitude

// initializer functions -------------------------------------------------------
// main initializer
function mainInit() {
    positions = [{address:"City Hall",location:[-74.006042, 40.712769], start: "2020-02-01 00:28:58",
            end: "2020-02-01 00:40:40", timeDifference: 0}];
    initGeo();
    initMap(positions[0].location);
    $("#uploadForm").submit(loadJSON)
    $("#isInfected").change(checkBoxStatusChange)
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
                    'stops': [[18, 7], [33, 270]]
                },
                'circle-color': 'rgba(255, 50, 50, 0.8)'
            }
        });
        // Create a popup, but don't add it to the map yet.
        var popup = new mapboxgl.Popup({
            closeButton: false,
            closeOnClick: false
            });
            
            map.on('mouseenter', 'user-position', function(e) {
                // Change the cursor style as a UI indicator.
                map.getCanvas().style.cursor = 'pointer';
                
                var coordinates = e.features[0].geometry.coordinates;
                var description = e.features[0].properties.description;
                
                // Ensure that if the map is zoomed out such that multiple
                // copies of the feature are visible, the popup appears
                // over the copy being pointed to.
                while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
                    coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
                }
                // Populate the popup and set its coordinates
                // based on the feature found.
                popup.setLngLat(coordinates).setHTML(description).addTo(map);
            });
            
            map.on('mouseleave', 'user-position', function() {
            map.getCanvas().style.cursor = '';
            popup.remove();
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
                'properties': {
                    'description':
                    '<strong>Location Address</strong><p>Example inside information.</p>'
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [0, 0]
                }
            }
        ]
    };
    // Test data load
    geojson.features = [];

    positions.forEach(pos => {
        var startDate = new Date(pos.start);
        var endDate = new Date(pos.end);
        geojson.features.push({
                'type': 'Feature',
                'properties': {
                    'description':'<strong class=\"map-info-box\">' + pos.address +
                    '</strong><hr><p class=\"map-info-box\"><strong>Time Arrived:</strong> ' +
                    startDate.toLocaleTimeString() + ' (' + startDate.toLocaleDateString() + ')' +
                    '<br><strong>Time Left:</strong> '
                    + endDate.toLocaleTimeString() + ' (' + endDate.toLocaleDateString() + ')' +
                    '<br><strong>Time after an infected person was present at location:</strong> '
                    + pos.timeDifference + ' minutes.</p>'
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': pos.location
                }
            })
    }); 
}

// function functions -------------------------------------------------------------
// populates the geojson object with points
function populatePoints(json_data) {
    console.log("Looking to populate points");
    positions = new Array(0);
    console.log(json_data.length + " location objects found.");
    if (json_data.length > 0) {
        for (var i = 0; i < json_data.length; i++) {
            var nearby = json_data[i].nearby;
            if (nearby) {
                for (var place in nearby) {
                    coords = nearby[place]["coordinates"];
                    if (coords) {
                        positions.push({address:nearby[place]["Address"],location:[coords['lon'], coords['lat']],
                        start:nearby[place]["timestamp"]["startTimestampMs"],
                        end:nearby[place]["timestamp"]["endTimestampMs"],
                        timeDifference: nearby[place]["timeDifference"]});
                    }
                }
            }
        }
        // reload map
        console.log("Reloading map with new positional data.");
        initGeo();
        initMap(positions[0].location);
        document.getElementById("response-div").innerHTML = contributeForm;
        $("#loginModal")[0].style.display="none";
    } else {
        console.log("Welp. Looks like there's no location overlap data.");
    }
}

// load JSON function called from button press
function loadJSON(e) {
    formdata = new FormData();
    if($("#isInfected")[0].checked){
        if($("#file").prop('files').length!=2){
            alert("You were expected to upload exactly two files");
            return false;
        }
        fileList=$("#file").prop('files');
        formdata.append("jsonFile1",fileList[0]);
        formdata.append("jsonFile2",fileList[1]);
        console.log(fileList);
    }else{
        file = $("#file").prop('files')[0];
        formdata.append('jsonFile', file);
        console.log(file)
    }
    console.log("Calling ajax! with " + $("#file").prop('files').length + " file");
    $.ajax({
        method: "POST",
        url: config.server_remote,  // config.server_remote, config.server_local
        data: formdata,
        processData: false,
        contentType: false,
        encType:"multipart/form-data",
        success: function (data) {
            // console.log(data);
            if(data.toLowerCase().includes("message")){
                alert(data);
                if(data.toLowerCase().includes("error"))
                    return false;
            } else{
                json_data = JSON.parse(data);
                populatePoints(json_data);
            }
            $("#loginModal")[0].style.display="none";
        }
    });
    e.preventDefault();
}

function checkBoxStatusChange(){
    $("#file")[0].toggleAttribute("multiple");
    $("#2FileComment").toggle()
}
// call methods -------------------------------------------
mainInit();