// Global objects
let map = null;         // Mapbox GL object
let geojson = null;     // Geojson object
let positions = null;   // 2D array of longitude and latitude
let counties = null;    // Counties object from our backend
let erics = null;       // Erics county geometry data
let allData = null;     // All data in the whole universe
let allDataGeo = null;  // All data but in mapbox readable format
let dateList = null;    // List of dates to filter by
var ericDataAttempts = 0;   // Attempts to grab erics data
var maxCases = 0;           // Max cases to determine the min and max for gradient
var maxDeaths = 0;          // Max deaths to determine the min and max for gradient
var currentDate = '';       // Current day determined from the slider
var currentDayValue = 0;    // Numerical value of current day determined from the slider
var mapStyle = 'mapbox://styles/mapbox/dark-v10';
var uploadOption = "countyLevel";    // countyLevel, infectedPlaces, etc..

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
    mapboxgl.accessToken = config['mapbox_token'];
    map = new mapboxgl.Map({
        container: 'map',
        style: mapStyle,
        center: [-89.651607, 39.781232],
        zoom: 3.5,
        minZoom: 3.5,
        maxZoom: 12
    });
}

function loadAllData(data) {
    if (data != null) {
        if (data.length > 2) {
            allData = JSON.parse(data);
            populateAllGeo(allData);

            map.addSource('Points', {
                'type': 'geojson',
                'data': allDataGeo
            });
            map.addLayer({
                id: 'user-heatmap',
                type: 'heatmap',
                source: 'Points',
                maxzoom: 15,
                paint: {
                // increase weight as risk increases
                'heatmap-weight': {
                    'property': 'point_count',
                    'type': 'identity'
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
        }
    }
}

// ajax call to populate county data with formated filter
function loadInitialData(data) {
    if (erics != null) {
        if (data.length > 2) {
            dataObj = JSON.parse(data);
            console.log(dataObj);
            counties = dataObj.collection
            colorCodes = dataObj.colorCodes
            lastDayElapsed = dataObj.lastAvailableDay;
            // hopefully erics data doesn't change
            for (var i = 0; i < counties.length; i++) {
                // cut out the first part of the geoid
                var geoid = erics.features[i].properties.GEO_ID.substring(9,);
                // just a double check if theres an inconsitency in data, we really just wanna break out of the loop
                if (geoid == counties[i][config['ccd']['GEO_ID']]) {
                    // our cases array that will change as we reconstruct the differential encoding
                    var cases = counties[i][config['ccd']['confirmed_cases']];
                    // make sure there are cases in the county
                    if (cases.length > 0) {
                        // current index
                        var casesIndex = 0;

                        erics.features[i].properties['dates'] = new Array();
                        // most recently changed date in the for current index
                        let colorCode;
                        // iterate from the first day in cases until today
                        for (var j = 0; j < cases.length; j++) {
                            // Get the max of all cases
                            if (cases[casesIndex][config['ccd']['count']] > maxCases)
                                maxCases = cases[casesIndex][config['ccd']['count']];
                            cases[casesIndex]['date'] = niceDate(addToDate(startDate, cases[casesIndex][config['ccd']['daysElapsed']]));
                            erics.features[i].properties.dates.push(cases[casesIndex][config['ccd']['daysElapsed']]);
                            colorCode = getColorCode(colorCodes,cases[casesIndex][config['ccd']['count']]);
                            erics.features[i].properties[cases[casesIndex][config['ccd']['daysElapsed']]+"_color"] = colorCode;
                            let nextAvailableDay = (casesIndex!=cases.length-1) ? cases[casesIndex+1][config['ccd']['daysElapsed']] : lastDayElapsed;
                            let nextActualDay = cases[casesIndex][config['ccd']['daysElapsed']] + 1;
                            while(nextActualDay<=nextAvailableDay){
                                erics.features[i].properties[nextActualDay+"_color"] = colorCode;
                                nextActualDay++;
                            }
                            // will add colors to erics properties
                            casesIndex ++;
                        }
                        erics.features[i].properties['latestColor'] = colorCode;
                    }
                    // load deaths into an array for easy interaction
                    var deaths = counties[i][config['ccd']['deaths']];
                    // make sure there are deaths in the county before doing anything else
                    if (deaths.length > 0) {
                        // current index
                        var deathsIndex = 0;
                        // iterate through all deaths to add the date field
                        for (var j = 0; j < deaths.length; j++) {
                            // Get the max of all deaths
                            if (deaths[deathsIndex][config['ccd']['count']] > maxDeaths)
                                maxDeaths = deaths[deathsIndex][config['ccd']['count']];
                            deaths[deathsIndex]['date'] = niceDate(addToDate(startDate, deaths[deathsIndex][config['ccd']['daysElapsed']])); 
                            deathsIndex ++;
                        }
                    }
                    erics.features[i].properties['confirmed_cases'] = counties[i][config['ccd']['confirmed_cases']];
                    erics.features[i].properties['deaths'] = counties[i][config['ccd']['deaths']];
                } else {
                    displayFooterMessage("An error occured with combining erics data.", true);
                    console.log(geoid);
                    break;
                }
            }
            displayFooterMessage("Background loading complete. Map is fully ready.", false);
            document.getElementById("cases-max").textContent = niceNumber(maxCases);
            console.log("Max cases found in a singular county: " + maxCases);
            // console.log(erics);  // printing erics data for testing
            latestDateAvailable = erics.features[0].properties.dates.slice(-1)[0];
            dateList = getDateArray(addToDate(startDate,latestDateAvailable));
            var slider = document.getElementById("slider");
            slider.max = dateList.length -1;
            slider.value = date_diff_indays(startDate, getToday());
            initMap(erics, null);
        } else {
            displayFooterMessage("Data was empty. We need to repopulate the database again...", true);
        }
    } else {
        if (ericDataAttempts < 2) {
            console.log("Erics data is null. Will retry method in a moment...");
            ericDataAttempts ++;
            wait(500);
            loadInitialData(data);
        } else {
            console.log("Erics data was too slow to load.");
            displayFooterMessage("Erics county data was empty. Try reloading the page in a minute or so.", true);
        }
    }
    // load all points -- loads all the locations where infected people have been(at certain higher height) -- not doing it anymore
    // $.ajax({
    //     method: "GET",
    //     url: config.server_ip + config.allData_url,
    //     processData: false,
    //     contentType: false,
    //     encType: "multipart/form-data",
    //     success: loadAllData,
    //     error: ajaxErrorHandle
    // });
}

// initializes map
function initMap(data, fullData) {
    mapboxgl.accessToken = config['mapbox_token'];
    map = new mapboxgl.Map({
        container: 'map',
        style: mapStyle,
        center: [-89.651607, 39.781232],
        zoom: 3.5,
        minZoom: 3.5,
        maxZoom: 12
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
                'fill-opacity': 0.4
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
            let currentElement = {}
            if (casesConfirmed && casesConfirmed.length > 0) {
                casesConfirmed.forEach((element, index) => {
                    if (element[config['ccd']['daysElapsed']] < currentDayValue) { 
                        currentElement = element;
                        flag = 1;
                    }
                });
                if (flag == 1) {
                    let futureText = currentElement[config['ccd']['isPredicted']] ? " [Forecasted]" : "";
                    stringBuilder += "<br><strong>Confirmed Cases:</strong> " + niceNumber(currentElement[config['ccd']['count']]) + futureText;
                }

                // We won't see a death with out seeing other cases
                if (flag == 1) {
                    // grab our deaths array
                    var deathsConfirmed = JSON.parse(feature.properties['deaths']);
                    if (deathsConfirmed.length > 0) {
                        deathsConfirmed.forEach((element, index) => {
                            if (element[config['ccd']['daysElapsed']] < currentDayValue) { 
                                currentElement = element;
                                flag = 2;
                            }
                        });
                        if (flag == 2) {
                            let futureText = currentElement[config['ccd']['isPredicted']] ? " [Forecasted]" : "";
                            stringBuilder += "<br><strong>Deaths:</strong> " + niceNumber(currentElement[config['ccd']['count']]) + futureText;
                        }
                    } else {
                        stringBuilder += "<br>No deaths in this county.";
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

        map.on('mouseenter', 'county', function() {
            map.getCanvas().style.cursor = '';
            popup.remove();
            overlay.style.display = 'none';
        });

        // filter starting position
        if (dateList != null) {
            filterBy(date_diff_indays(startDate, getToday()));
            document.getElementById("map-overlay-inner").style.visibility = "visible";
        }
        // filter listener
        document.getElementById("slider").addEventListener('input', function(e) {
            filterBy(e.target.value);
        });
    }); // eof map.onLoad
} // eof initMap

// forces slider to today
function forceToday() {
    var slider = document.getElementById("slider");
    var today = date_diff_indays(startDate, getToday());
    slider.value = today;
    filterBy(today);
}

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
    currentDayValue = dateList[date];
    currentDate = niceDate(addToDate(startDate, dateList[date]));
    // the number of days from our first case until now
    var daysFromFirst = date_diff_indays(startDate, getToday());
    var referenceString = "Past";
    if (date == daysFromFirst) {
        referenceString = "Today";
    } else if (date > daysFromFirst) {
        referenceString = "Future";
    }

    document.getElementById("map-refrence-tense").textContent = referenceString;
    document.getElementById("map-date").textContent = currentDate;
}

// function for checking location overlap with infected
function initContactMap(center, option, countyData) {
    document.getElementById("map-slider").style.display="none";
    document.getElementById("map-color").style.display="none";
    map = new mapboxgl.Map({
        container: 'map',
        style: mapStyle,
        center: [center[0], center[1]],
        zoom: 7,
        minZoom: 3,
        maxZoom: 20
    });

    map.addControl(new mapboxgl.NavigationControl());

    // init of map with blank geojson
    map.on('load', function () {
        if (option == "countyLevel") {
            var formatedData = {
                'type': 'FeatureCollection',
                'features': []
            };
            for (var i = 0; i < countyData['collection'].length; i++) {
                for (var j = 0; j < erics.features.length; j++) {
                    if (erics.features[j].properties.GEO_ID.substring(9,) == countyData['collection'][i][config['ccd']['GEO_ID']]) {
                        formatedData.features.push({
                            'geometry': erics.features[j].geometry,
                            'properties': erics.features[j].properties,
                            'type': "Feature"
                        });
                    }
                }
            }
            console.log(formatedData);
            map.addSource('county', {
                'type': 'geojson',
                'data': formatedData
            });
            // county geometry
            map.addLayer({
                'id': 'county-layer',
                'type': 'fill',
                'source': 'county',
                'paint': {
                    'fill-outline-color': 'rgba(50, 0, 50, 0.3)',
                    'fill-opacity': 0.2,
                    'fill-color': ['get', 'latestColor']
                }
            });
        } // eof if county level
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
                  [0.1, 0.1],
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
                        [{ zoom: 15, value: 0 }, 5],
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

function populateAllGeo(data) {
    allDataGeo = {
        'type': 'FeatureCollection',
        'features': [
            {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [0, 0]
                }
            }
        ]
    };
    data.forEach(pos => {
        allDataGeo.features.push({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': pos.location
            }
        });
    });
}

// initializes geojson for location overlap
function initGeo(geoObject, points, uploadOption) {
    // init for geojson
    geoObject = {
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
    geoObject.features = new Array();
    var indexPos = 0;
    points.forEach(pos => {
        if (uploadOption != "allData") {
            var startDate = new Date(parseInt(pos.start));
            var endDate = new Date(parseInt(pos.end));
            var riskDisplay = "<ins class=\"risk-low\">low";
            if (pos.risk > 0.7){
                riskDisplay = "<ins class=\"risk-med\">moderate";
                if (pos.risk > 0.9) {
                    riskDisplay = "<ins class=\"risk-high\">high"
                }
            }
            var temp = '<strong class=\"map-info-box\">' + pos.address +
            '</strong><hr><p class=\"map-info-box\"><strong>Time Arrived:</strong> ' +
            startDate.toLocaleTimeString() + ' (' + startDate.toLocaleDateString() + ')' +
            '<br><strong>Time Left:</strong> '
            + endDate.toLocaleTimeString() + ' (' + endDate.toLocaleDateString() + ')' +
            '<br><strong style="font-size:15px">';
            if (uploadOption == "countyLevel")
                temp += 'Area Risk Assessment:</strong> '+ riskDisplay + '</p>';
            if (uploadOption == "infectedPlaces")
                temp += 'Risk Assessment:</strong> '+ riskDisplay + '</p><label class="map-info-box" for="pos_' + indexPos +
                '">Keep this location?</label><input type="checkbox" id="pos_' + indexPos + '" checked>';

            riskDisplay += "</ins>";
        }
        geoObject.features.push({
                'type': 'Feature',
                'properties': {
                    'description': temp,
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
function populatePoints(json_data, option) {
    displayFooterMessage("Populating user points.", false);
    // set position array to the size of the data
    positions = new Array(0);
    console.log(json_data.length + " location objects found.");
    // check to make sure there is an array to go through
    if (json_data.length > 0) {
        if (option == "countyLevel") {
            // for each data point
            for (var i = 0; i < json_data.length; i++) {
                var place_location = json_data[i]['place_location'];
                var duration = json_data[i]['duration'];
                // add to the positions array
                positions.push({
                    address: place_location["address"],
                    location: [json_data[i]['centerLon'], json_data[i]['centerLat']],
                    risk: json_data[i]['risk'],
                    start: duration["startTimestampMs"],
                    end: duration["endTimestampMs"]
                });
            }
        }
        if (option == "infectedPlaces") {
            // for each infected location
            for (var i = 0; i < json_data.length; i++) {
                var nearby = json_data[i]['nearby'];
                // for each nearby location
                for (var j = 0; j < nearby.length; j++) {
                    var coords = nearby[j]['coordinates'];
                    var timeStamp = nearby[j]['timestamp'];
                    // add to the positions array
                    positions.push({
                        address: nearby[j]['Address'],
                        location: [coords['lon'], coords['lat']],
                        risk: 0.95,
                        start: timeStamp['startTimestampMs'],
                        end: timeStamp['endTimestampMs']
                    });
                }
            }
        }
    } else {
        displayFooterMessage("There was no data returned from the database. This might be a data population error.", true);
    }
}

// load JSON function called from button press
function loadJSON(e) {
    formdata = new FormData();
    formdata.append('uploadOption', uploadOption);
    formdata.append('radius',$("#radius")[0].value);
    formdata.append('time',$("#time")[0].value);
    if($("#data-consent-yes")[0].checked){
        // for crowd sourcing
        if($("#file").prop('files').length != 2){
            alert("You were expected to upload exactly two files");
            return false;
        }
        fileList=$("#file").prop('files');
        formdata.append("jsonFile1",fileList[0]);
        formdata.append("jsonFile2",fileList[1]);
        console.log(fileList);
    } else {
        // for regular checking
        file = $("#file").prop('files')[0];
        formdata.append('jsonFile', file);
    }
    displayFooterMessage("Loading user data...", false);
    console.log("Calling ajax! with " + $("#file").prop('files').length + " file");
    // this next part is real pasta code
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
                    location.reload();
            } else{
                json_data = JSON.parse(data);
                // Detect what json file is coming from the backend
                var option = json_data['uploadOption'];
                switch (option) {
                    case "countyLevel":
                        populatePoints(json_data.placesVisited, option);
                        $("#loginModal")[0].style.display="none";
                        initGeo(geojson,positions,option);
                        initContactMap(positions[0].location, option, json_data['counties']);
                        displayFooterMessage(contributeForm, false);
                        break;
                    case "infectedPlaces":
                        populatePoints(json_data.infectedPlaces, option);
                        $("#loginModal")[0].style.display="none";
                        initGeo(geojson,positions,option);
                        initContactMap(positions[0].location, option);
                        displayFooterMessage(contributeForm, false);
                        break;
                    default:
                        console.log("The uploadOption returned a string not familiar. It returned: " + option);
                        displayFooterMessage("The file you submitted may not be supported or something else happened.", true);
                }

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