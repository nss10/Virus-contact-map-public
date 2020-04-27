// Global objects
let map = null;         // Mapbox GL object
let geojson = null;     // Geojson object
let positions = null;   // 2D array of longitude and latitude
let counties = null;    // Counties object from our backend
let erics = null;       // Erics county geometry data
let dateList = null;    // List of dates to filter by
var maxCases = 0;       // Max cases to determine the min and max for gradient
var maxDeaths = 0;      // Max deaths to determine the min and max for gradient
var currentDate = '';    // Current day determined from the slider
var mapStyle = 'mapbox://styles/mapbox/dark-v10';

// initializer functions -------------------------------------------------------
// main initializer
function mainInit() {
    drawBlankMap();
    // load erics
    $.ajax({
        method: "GET",
        url: config.server_ip + config.ericsData_url,
        processData: false,
        contentType: false,
        encType: "multipart/form-data",
        success: loadEricData,
        error: ajaxErrorHandle
    });

    // load ours
    $.ajax({
        method: "GET",
        url: config.server_ip + config.countyCases_url, 
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
    erics = JSON.parse(data);
    displayFooterMessage("Map pre-load finished. Moving to background loading...", false);
}

function drawBlankMap() {
    mapboxgl.accessToken = 'pk.eyJ1IjoiemFjaGFyeTgxNiIsImEiOiJjazd6NXN2eWwwMml0M2tvNGo2c3JkcGFpIn0.aB1upejZ61JQjb_z2g1NuA';
    map = new mapboxgl.Map({
        container: 'map',
        style: mapStyle,
        center: [-89.651607, 39.781232],
        zoom: 4,
        minZoom: 4,
        maxZoom: 7
    });
}

// ajax call to populate county data with formated filter
function loadInitialData(data){
    if (data.length > 2) {
        dataObj = JSON.parse(data);
        counties = dataObj.collection
        colorCodes = dataObj.colorCodes
        // hopefully erics data doesn't change
        for (var i = 0; i < counties.length; i++) {
            // cut out the first part of the geoid
            var geoid = erics.features[i].properties.GEO_ID.substring(9,);
            // just a double check if theres an inconsitency in data, we really just wanna break out of the loop
            if (geoid == counties[i].GEO_ID) {
                // our cases array that will change as we reconstruct the differential encoding
                var cases = counties[i].confirmed_cases;
                // make sure there are cases in the county
                if (cases.length > 0) {
                    // current index
                    var casesIndex = 0;

                    erics.features[i].properties['dates'] = new Array();
                    // most recently changed date in the for current index
                    var lastChangedDate = addToDate(startDate, cases[0].daysElapsed);
                    // the number of days from our first case until now
                    var daysFromFirst = date_diff_indays(lastChangedDate, getToday());
                    // iterate from the first day in cases until today
                    for (var j = 0; j < cases.length; j++) {
                        // Get the max of all cases
                        if (cases[casesIndex].count > maxCases)
                            maxCases = cases[casesIndex].count;
                        cases[casesIndex]['date'] = niceDate(addToDate(startDate, cases[casesIndex].daysElapsed));
                        erics.features[i].properties.dates.push(cases[casesIndex].daysElapsed);
                        erics.features[i].properties[cases[casesIndex].daysElapsed+"_color"] = colorCodes[cases[casesIndex].count];
                        // will add colors to erics properties
                        casesIndex ++;
                    }
                }
                // load deaths into an array for easy interaction
                var deaths = counties[i].deaths;
                // make sure there are deaths in the county before doing anything else
                if (deaths.length > 0) {
                    // current index
                    var deathsIndex = 0;
                    // iterate through all deaths to add the date field
                    for (var j = 0; j < deaths.length; j++) {
                        // Get the max of all deaths
                        if (deaths[deathsIndex].count > maxDeaths)
                            maxDeaths = deaths[deathsIndex].count;
                        deaths[deathsIndex]['date'] = niceDate(addToDate(startDate, deaths[deathsIndex].daysElapsed));
                        deathsIndex ++;
                    }
                }
                erics.features[i].properties['confirmed_cases'] = counties[i].confirmed_cases;
                erics.features[i].properties['deaths'] = counties[i].deaths;
            } else {
                displayFooterMessage("An error occured with combining erics data.", true);
                console.log(geoid);
                break;
            }
        }
        displayFooterMessage("Background loading complete. Map is fully ready.", false);
        console.log("Max cases found in a singular county: " + maxCases);
        // console.log(erics);  // printing erics data for testing
        latestDateAvailable = erics.features[0].properties.dates.slice(-1)[0];
        dateList = getDateArray(addToDate(startDate,latestDateAvailable));
        document.getElementById('slider').max = dateList.length -1;
        document.getElementById('slider').value = dateList.length - 1;
        initMap(erics, [4, 8]);
    } else {
        displayFooterMessage("Data was empty. We need to repopulate the database again...", true);
    }    
}

// initializes map
function initMap(data, zoom) {
    mapboxgl.accessToken = 'pk.eyJ1IjoiemFjaGFyeTgxNiIsImEiOiJjazd6NXN2eWwwMml0M2tvNGo2c3JkcGFpIn0.aB1upejZ61JQjb_z2g1NuA';
    map = new mapboxgl.Map({
        container: 'map',
        style: mapStyle,
        center: [-89.651607, 39.781232],
        zoom: 4,
        minZoom: zoom[0],
        maxZoom: zoom[1]
    });
    // disable map rotation using right click + drag
    map.dragRotate.disable();
    // disable map rotation using touch rotation gesture
    map.touchZoomRotate.disableRotation();
    //map.addControl(new mapboxgl.NavigationControl());
    var popup = new mapboxgl.Popup({
        closeButton: false
    });
    // init of map with blank geojson
    map.on('load', function () {
        map.addSource('county', {
            'type': 'geojson',
            'data': data
        });
        // county geometry
        map.addLayer({
            'id': 'county-layer',
            'type': 'fill',
            'source': 'county',
            'paint': {
                'fill-outline-color': 'rgba(50, 0, 50, 0.3)',
                'fill-opacity': 0.1
            }
        });
        // mouse moving display
        map.on('mousemove', 'county-layer', function(e) {
            // Change the cursor style as a UI indicator.
            map.getCanvas().style.cursor = 'pointer';
             
            // Single out the first found feature.
            var feature = e.features[0];

            // Start the popup string
            var stringBuilder = "<div class=\"map-info-box\">" + currentDate;
            // Grab our confirmed cases array
            var casesConfirmed = JSON.parse(feature.properties['confirmed_cases']);
            // Flag if there was no cases for that date
            var flag = 0;
            if (casesConfirmed) {
                if (casesConfirmed.length > 0) {
                    casesConfirmed.forEach(element => {
                        if (element.date == currentDate) {
                            stringBuilder += "<br><strong>Confirmed Cases:</strong> " + element.count;
                            flag = 1;
                        }
                    });
                    // We won't see a death with out seeing other cases
                    if (flag == 1) {
                        // grab our deaths array
                        var deathsConfirmed = JSON.parse(feature.properties['deaths']);
                        if (deathsConfirmed.length > 0) {
                            deathsConfirmed.forEach(element => {
                                if (element.date == currentDate) {
                                    stringBuilder += "<br><strong>Deaths:</strong> " + element.count;
                                } 
                            });
                        } else {
                            stringBuilder += "<br>No deaths in this county.";  
                        }
                    }
                }
            }
            // Flag will be 0 if no cases were gathered on date the user is currently looking at
            if (flag == 0) {
                stringBuilder += "<br>There are no reported cases on this day.";
            }

            stringBuilder += "</div>";
            // Display a popup with the name of the county
            var textString = "<strong class=\"map-info-box-title\">" + feature.properties.NAME + "</strong>" + stringBuilder;
            popup.setLngLat(e.lngLat).setHTML(textString).addTo(map);
        });

        map.on('mouseleave', 'county', function() {
            map.getCanvas().style.cursor = '';
            popup.remove();
            overlay.style.display = 'none';
        });

        // filter starting position
        if (dateList != null)
            filterBy(dateList.length - 1);
        // filter listener
        document.getElementById('slider').addEventListener('input', function(e) {
            filterBy(e.target.value);
        });
    }); // eof map.onLoad
} // eof initMap

// filter by date for county map
function filterBy(date) {
    date_color=date+"_color"
    var filters = ['!=',date_color, null];
    map.setPaintProperty('county-layer', 'fill-color', 
    [   
        "case",
        ["!=",["get",date_color],null],["get",date_color],
       "rgba(0,0,0,0)"
    ]
    );
    currentDate = niceDate(addToDate(startDate, dateList[date]));
    document.getElementById('map-date').textContent = currentDate;
}

// function for checking location overlap with infected
function initContactMap(center, zoom) {
    document.getElementById("map-slider").style.display="none";;
    map = new mapboxgl.Map({
        container: 'map',
        style: mapStyle,
        center: [center[0], center[1]],
        zoom: 7,
        minZoom: zoom[0],
        maxZoom: zoom[1]
    });

    map.addControl(new mapboxgl.NavigationControl());

    // init of map with blank geojson
    map.on('load', function () {
        map.addSource('Points', {
            'type': 'geojson',
            'data': geojson
        });
        // Heatmap
        map.addLayer({
            id: 'user-heatmap',
            type: 'heatmap',
            source: 'Points',
            maxzoom: 15,
            paint: {
              // increase weight as risk increases
              'heatmap-weight': {
                property: 'risk',
                type: 'exponential',
                stops: [
                  [0, 0],
                  [1, 1]
                ]
              },
              // increase intensity as zoom level increases
              'heatmap-intensity': {
                stops: [
                  [11, 1],
                  [15, 3]
                ]
              },
              // assign color values be applied to points depending on their density
                'heatmap-color': [
                    'interpolate',
                    ['linear'],
                    ['heatmap-density'],
                    0, 'hsla(180, 100%, 80%, 0)',
                    0.2, 'hsl(230, 100%, 80%)',
                    0.4, 'hsl(275, 100%, 70%)',
                    0.6, 'hsl(320, 100%, 60%)',
                    0.8, 'hsl(350, 100%, 60%)',
                ],
              // increase radius as zoom increases
              'heatmap-radius': {
                stops: [
                  [11, 15],
                  [15, 20]
                ]
              },
              // decrease opacity to transition into the circle layer
              'heatmap-opacity': {
                default: 1,
                stops: [
                  [14, 1],
                  [15, 0]
                ]
              },
            }
        }, 'waterway-label');
        // Adding circles
        map.addLayer({
            id: 'user-position',
            type: 'circle',
            source: 'Points',
            minzoom: 14,
            paint: {
                // increase the radius of the circle as the zoom level and dbh value increases
                'circle-radius': {
                    property: 'risk',
                    type: 'exponential',
                    stops: [
                        [{ zoom: 15, value: 0 }, 1],
                        [{ zoom: 15, value: 1 }, 10],
                        [{ zoom: 22, value: 0 }, 10],
                        [{ zoom: 22, value: 1 }, 30],
                    ]
                },
                'circle-color': {
                    property: 'risk',
                    type: 'exponential',
                    stops: [
                        [0, 'rgba(50,255,50,0.5)'],
                        [0.7, 'rgb(50,255,50)'],
                        [0.9, 'rgb(255,255,50)'],
                        [1, 'rgb(255,50,50)']
                    ]
                },
                'circle-stroke-color': 'black',
                'circle-stroke-width': {
                    stops: [
                        [13, 1],
                        [16, 0]
                    ]
               },
                'circle-opacity': {
                     stops: [
                         [13, 0],
                         [16, 1]
                     ]
                }
            }
        }, 'waterway-label');
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
    displayFooterMessage("Map displayed.", false);
}

// initializes geojson for location overlap
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
    geojson.features = new Array();
    var indexPos = 0;
    positions.forEach(pos => {
        var startDate = new Date(parseInt(pos.start));
        var endDate = new Date(parseInt(pos.end));
        var riskDisplay = "<ins class=\"risk-low\">low";
        if (pos.risk > 0.7){
            riskDisplay = "<ins class=\"risk-med\">moderate";
            if (pos.risk > 0.9) {
                riskDisplay = "<ins class=\"risk-high\">high"
            }
        }
        riskDisplay += "</ins>";
        geojson.features.push({
                'type': 'Feature',
                'properties': {
                    'description':'<strong class=\"map-info-box\">' + pos.address +
                    '</strong><hr><p class=\"map-info-box\"><strong>Time Arrived:</strong> ' +
                    startDate.toLocaleTimeString() + ' (' + startDate.toLocaleDateString() + ')' +
                    '<br><strong>Time Left:</strong> '
                    + endDate.toLocaleTimeString() + ' (' + endDate.toLocaleDateString() + ')' +
                    '<br><strong style="font-size:15px">Risk Assessment:</strong> '
                    + riskDisplay + '</p><label class="map-info-box" for="pos_' + indexPos + '">Keep this location?</label><input type="checkbox" id="pos_' + indexPos + '" checked>',
                    'risk': pos.risk
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': pos.location
                }
            });
        indexPos ++;
    });
}

// function functions -------------------------------------------------------------
// populates the geojson object with points
function populatePoints(json_data) {
    displayFooterMessage("Populating user points.", false);
    // set position array to the size of the data
    positions = new Array(0);
    console.log(json_data.length + " location objects found.");
    // check to make sure there is an array to go through
    if (json_data.length > 0) {
        // for each data point
        for (var i = 0; i < json_data.length; i++) {
            var place_location = json_data[i]['place_location'];
            var duration = json_data[i]['duration'];
            // add to the positions array
            positions.push({
                address: place_location["address"],
                location: [json_data[i]['centerLon'], json_data[i]['centerLat']],
                risk: 0.6,
                start: duration["startTimestampMs"],
                end: duration["endTimestampMs"]
            });
        }

        var zoom = [3, 20];
        initGeo();
        initContactMap(positions[0].location, zoom);
        document.getElementById("response-div").innerHTML = contributeForm;
        $("#loginModal")[0].style.display="none";
    } else {
        displayFooterMessage("There was no data returned from the database. This might be a data population error.", true);
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
    } else {
        file = $("#file").prop('files')[0];
        formdata.append('jsonFile', file);
        console.log(file)
    }
    displayFooterMessage("Loading user data...", false);
    console.log("Calling ajax! with " + $("#file").prop('files').length + " file");
    $.ajax({
        method: "POST",
        url: config.server_ip + config.upload_url, 
        data: formdata,
        processData: false,
        contentType: false,
        encType:"multipart/form-data",
        success: function (data) {
            if(typeof data != "object" && data.toLowerCase().includes("message")){
                alert(data);
                if(data.toLowerCase().includes("error"))
                    return false;
                else    
                    location.reload()
            } else{
                json_data = JSON.parse(data);
                console.log(json_data);
                populatePoints(json_data.placesVisited);
            }
            $("#loginModal")[0].style.display="none";
        },
        error: ajaxErrorHandle
    });
    e.preventDefault();
}

// check box listener
function checkBoxStatusChange(){
    $("#file")[0].toggleAttribute("multiple");
    $("#2FileComment").toggle()
    $("#configParams").toggle()
}
// call methods -------------------------------------------
mainInit();