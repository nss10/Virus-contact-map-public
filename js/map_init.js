// Global objects
let map = null;         // Mapbox GL object
let geojson = null;     // Geojson object
let positions = null;   // 2D array of longitude and latitude
let counties = null;    // Counties object
let erics = null;
let dateBins = null;

// initializer functions -------------------------------------------------------
// main initializer
function mainInit() {
    // load erics
    $.ajax({
        method: "GET",
        url: "https://eric.clst.org/assets/wiki/uploads/Stuff/gz_2010_us_050_00_20m.json",
        processData: false,
        contentType: false,
        encType: "multipart/form-data",
        success: loadEricData,
        error: ajaxErrorHandle
    });

    // load ours
    $.ajax({
        method: "GET",
        url: config.server_ip + "/countyLocationData",  // config.server_remote, config.server_local
        processData: false,
        contentType: false,
        encType: "multipart/form-data",
        success: loadInitialData,
        error: ajaxErrorHandle
    });

    displayFooterMessage("Loading initial county data, please wait...", false);

    $("#uploadForm").submit(loadJSON)
    $("input[name='data-consent']").change(checkBoxStatusChange)
}

// load erics while moving stuff around in the background
function loadEricData(data){
    erics = data;
    displayFooterMessage("Erics data loaded.", false);
    initMap(erics, [4, 11]);
}

// initial ajax call of data load
function loadInitialData(data){
    counties = JSON.parse(data);
    console.log(niceDate(getToday()));

    // hopefully erics data doesn't change
    for (var i = 0; i < counties.length; i++) {
        // cut out the first part of the geoid
        var geoid = erics.features[i].properties.GEO_ID.substring(9,);
        // our cases array that will change as we reconstruct the differential encoding
        var cases = counties[i].confirmed_cases;
        // make sure there are cases in the county
        if (cases.length > 0) {
            // current index
            var casesIndex = 0;
            // most recently changed date in the for current index
            var lastChangedDate = addToDate(startDate, cases[0].daysElapsed);
            // the number of days from our first case until now
            var daysFromFirst = date_diff_indays(lastChangedDate, getToday());
            // iterate from the first day in cases until today
            for (var j = 0; j < daysFromFirst; j++) {
                // if we're on the last array of the casses, we just need to copy it until todays date to display
                if ((casesIndex + 1) >= cases.length) {
                    cases.push({'daysElapsed':cases[casesIndex].daysElapsed,'date':addToDate(startDate, cases[casesIndex].daysElapsed + j),'count':cases[casesIndex].count});
                    casesIndex ++;
                } else {
                    cases[casesIndex]['date'] = addToDate(startDate, cases[casesIndex].daysElapsed);
                    if (cases[casesIndex].daysElapsed != cases[casesIndex + 1].daysElapsed) {
                        cases.splice(casesIndex + 1, 0, {'daysElapsed':cases[casesIndex].daysElapsed + j,'date':addToDate(startDate, cases[casesIndex].daysElapsed + j),'count':cases[casesIndex].count});
                    } else {
                        lastChangedDate = addToDate(startDate, cases[casesIndex].daysElapsed + j);
                        casesIndex ++;
                    }
                }
            }
        }
        // just a double check if theres an inconsitency in data, we really just wanna break out of the loop
        if (geoid == counties[i].GEO_ID) {
            erics.features[i].properties['confirmed_cases'] = counties[i].confirmed_cases;
            erics.features[i].properties['deaths'] = counties[i].deaths;
        } else {
            displayFooterMessage("An error occured with combining erics data.", true);
            console.log(geoid);
            break;
        }
    }
    displayFooterMessage("County data loaded.", false);
    console.log(erics);
}

// initializes map
function initMap(data, zoom) {
    mapboxgl.accessToken = 'pk.eyJ1IjoiemFjaGFyeTgxNiIsImEiOiJjazd6NXN2eWwwMml0M2tvNGo2c3JkcGFpIn0.aB1upejZ61JQjb_z2g1NuA';
    map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/mapbox/light-v10',
        center: [-89.651607, 39.781232],
        zoom: 7,
        minZoom: zoom[0],
        maxZoom: zoom[1]
    });

    map.addControl(new mapboxgl.NavigationControl());

    // init of map with blank geojson
    map.on('load', function () {
        map.addSource('county', {
            'type': 'geojson',
            'data': data
            //'data': geojson
        });
        // Heatmap
        // map.addLayer({
        //     id: 'user-heat',
        //     type: 'heatmap',
        //     source: 'point',
        //     maxzoom: 15,
        //     paint: {
        //       // increase weight as diameter breast height increases
        //       'heatmap-weight': {
        //         property: 'dbh',
        //         type: 'exponential',
        //         stops: [
        //           [1, 0],
        //           [62, 1]
        //         ]
        //       },
        //       // increase intensity as zoom level increases
        //       'heatmap-intensity': {
        //         stops: [
        //           [11, 1],
        //           [15, 3]
        //         ]
        //       },
        //       // assign color values be applied to points depending on their density
        //         'heatmap-color': [
        //             'interpolate',
        //             ['linear'],
        //             ['heatmap-density'],
        //             0, 'hsla(180, 100%, 80%, 0)',
        //             0.2, 'hsl(230, 100%, 80%)',
        //             0.4, 'hsl(275, 100%, 70%)',
        //             0.6, 'hsl(320, 100%, 60%)',
        //             0.8, 'hsl(360, 100%, 50%)',
        //         ],
        //       // increase radius as zoom increases
        //       'heatmap-radius': {
        //         stops: [
        //           [11, 15],
        //           [15, 20]
        //         ]
        //       },
        //       // decrease opacity to transition into the circle layer
        //       'heatmap-opacity': {
        //         default: 1,
        //         stops: [
        //           [14, 1],
        //           [15, 0]
        //         ]
        //       },
        //     }
        // }, 'waterway-label');
        // Adding circles
        // map.addLayer({
        //     id: 'user-position',
        //     type: 'circle',
        //     source: 'point',
        //     minzoom: 14,
        //     paint: {
        //         // increase the radius of the circle as the zoom level and dbh value increases
        //         'circle-radius': {
        //         property: 'dbh',
        //         type: 'exponential',
        //         stops: [
        //             [{ zoom: 15, value: 1 }, 5],
        //             [{ zoom: 15, value: 62 }, 10],
        //             [{ zoom: 22, value: 1 }, 20],
        //             [{ zoom: 22, value: 62 }, 50],
        //         ]
        //         },
        //         'circle-color': {
        //         property: 'dbh',
        //         type: 'exponential',
        //         stops: [
        //             [0, 'rgba(239,222,222,0)'],
        //             [10, 'rgb(255,222,222)'],
        //             [20, 'rgb(230,208,208)'],
        //             [30, 'rgb(219,166,166)'],
        //             [40, 'rgb(207,103,103)'],
        //             [50, 'rgb(153,28,28)'],
        //             [60, 'rgb(108,1,1)']
        //         ]
        //         },
        //         'circle-stroke-color': 'white',
        //         'circle-stroke-width': 1,
        //         'circle-opacity': {
        //              stops: [
        //                  [14, 0],
        //                  [15, 1]
        //              ]
        //         }
        //     }
        // }, 'waterway-label');
        // Create a popup, but don't add it to the map yet.

        map.addLayer({
            'id': 'county-layer',
            'type': 'fill',
            'source': 'county',
            'minzoom': 5.5,
            'paint': {
                'fill-color': 'rgba(150, 75, 150, 0.4)',
                'fill-outline-color': 'rgba(50, 0, 50, 0.8)'
            }
        });

        map.addLayer({
            'id': 'county-labels',
            'type': 'symbol',
            'source': 'county',
            'minzoom': 8,
            'layout': {
                'text-field': [
                    'concat',
                    ['to-string', ['get', 'NAME']],
                    '\nCases:'
                ],
                'text-font': [
                    'Open Sans Bold',
                    'Arial Unicode MS Bold'
                ],
                'text-size': 14
            },
                'paint': {
                    'text-color': 'rgba(0,0,0,1)'
                }
        });

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

// filter by function for map
function filterBy(date) {
    var dateArray = getDateArray();
    var filters = ['==', 'date', date];
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
        var startDate = new Date(parseInt(pos.start));
        var endDate = new Date(parseInt(pos.end));
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
        var zoom = [3, 20];

        initGeo();
        initMap(positions[0].location, zoom);
        document.getElementById("response-div").innerHTML = contributeForm;
        $("#loginModal")[0].style.display="none";
    } else {
        alert("Welp. Looks like there's no location overlap data.");
    }
}

// load JSON function called from button press
function loadJSON(e) {
    formdata = new FormData();
    formdata.append('radius',$("#radius")[0].value);
    formdata.append('time',$("#time")[0].value);
    if($("#data-consent-yes")[0].checked){
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
        url: config.server_ip + config.upload_url, 
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
                else    
                    location.reload()
            } else{
                json_data = JSON.parse(data);
                populatePoints(json_data);
            }
            $("#loginModal")[0].style.display="none";
        },
        error: ajaxErrorHandle
    });
    e.preventDefault();
}

function checkBoxStatusChange(){
    $("#file")[0].toggleAttribute("multiple");
    $("#2FileComment").toggle()
    $("#configParams").toggle()
}
// call methods -------------------------------------------
mainInit();