// Global objects
let map = null;         // Mapbox GL object
let geojson = null;     // Geojson object
let positions = null;   // 2D array of longitude and latitude
let counties = null;    // Counties object from our backend
let geoJson = null;       // Erics county geometry data
let allData = null;     // All data in the whole universe
let allDataGeo = null;  // All data but in mapbox readable format
let dateList = null;    // List of dates to filter by
var geoJsonDataAttempts = 0;   // Attempts to grab erics data
var maxPropValForColorCode = 0;           // Max cases to determine the min and max for gradient
var currentDate = '';       // Current day determined from the slider
var currentDayValue = 0;    // Numerical value of current day determined from the slider
var latestDateValue;
var lastDayElapsed;
var mapStyle = 'mapbox://styles/mapbox/dark-v10';
var uploadOption = "countyLevel";    // countyLevel, infectedPlaces, etc..
const countKey = config['ccd']['count'];
const daysElapsedKey = config['ccd']['daysElapsed'];

// initializer functions -------------------------------------------------------
// main initializer
function mainInit() {
    drawBlankMap();

    // load erics
    callService(config.geoJsonData_url, loadGeometryData);

    // load ours
    callService(config.countyCases_url, loadInitialData);

    displayFooterMessage("Loading initial county data, please wait...", false);
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

// load erics while moving stuff around in the background
function loadGeometryData(data) {
    geoJson = JSON.parse(data);
    displayFooterMessage("Map pre-load finished. Moving to background loading...", false);
}

// ajax call to populate county data with formated filter
function loadInitialData(responseData) {
    if (geoJson == null) // FIXME: See if there is a better way to do it
    {
        if (geoJsonDataAttempts < 2) {
            console.log("GeoJson data is null. Will retry method in a moment...");
            geoJsonDataAttempts++;
            setTimeout(() => loadInitialData(responseData), 500)
            
        } else {
            console.log("GeoJson data was too slow to load.");
            displayFooterMessage("County level GeoJson data was empty. Try reloading the page in a minute or so.", true);
        }
    }
    else {
        if (responseData && responseData.length < 2) {
            displayFooterMessage("Data was empty. We need to repopulate the database again...", true);
        }
        else {
            let countyCasesObject = JSON.parse(responseData);
            let counties = countyCasesObject.collection
            let colorCodes = countyCasesObject.colorCodes
            lastDayElapsed = countyCasesObject.lastAvailableDay;

            for (var countyIndex = 0; countyIndex < counties.length; countyIndex++) {
                var geoid = geoJson.features[countyIndex].properties.GEO_ID;
                // just a double check if theres an inconsitency in data, we really just wanna break out of the loop
                if (geoid != counties[countyIndex][config['ccd']['GEO_ID']]) {
                    displayFooterMessage("An error occured with combining erics data.", true);
                    console.log(geoid);
                    break;
                }
                else {

                    let cases = counties[countyIndex][config['ccd']['confirmed_cases']];
                    let deaths = counties[countyIndex][config['ccd']['deaths']];
                    addNiceDateToProp(cases);
                    addNiceDateToProp(deaths);

                    //For a property whose value decides the color codes
                    addColorCodes(cases, colorCodes, lastDayElapsed);

                    geoJson.features[countyIndex].properties['confirmed_cases'] = cases;
                    geoJson.features[countyIndex].properties['deaths'] = deaths;
                }
            }
            displayFooterMessage("Background loading complete. Map is fully ready.", false);

            latestDateValue = addToDate(startDate, lastDayElapsed)
            initMap(geoJson);
            updateToolbarLimits();
        }
    }

    //Local function 
    function addNiceDateToProp(prop) {
        if (prop.length > 0) {
            // iterate through all prop instances to add the date field
            for (let propIndex = 0; propIndex < prop.length; propIndex++) {
                let daysElapsed = prop[propIndex][daysElapsedKey];
                // Parsing the daysElapsed property to get the actual date in MM/DD/YYYY format
                prop[propIndex]['date'] = niceDate(addToDate(startDate, daysElapsed));
            }
        }
    }

    //Local function
    function addColorCodes(prop, colorCodes, lastDayElapsed) {
        if (prop.length > 0) {
            let colorCode; // current colorCode

            // iterate from the first day in cases until today
            for (let propIndex = 0; propIndex < prop.length; propIndex++) {
                let daysElapsed = prop[propIndex][daysElapsedKey];
                let caseCount = prop[propIndex][countKey];

                // Get the max of all cases
                if (caseCount > maxPropValForColorCode)
                    maxPropValForColorCode = caseCount;

                // Getting color code corresponding to caseCount from the function
                colorCode = getColorCode(colorCodes, caseCount);

                // next date where number of cases is changed
                let nextAvailableDay = (propIndex != prop.length - 1) ? prop[propIndex + 1][daysElapsedKey]
                    : lastDayElapsed;

                // Add more color key value pairs with same color until next differential date is available
                while (daysElapsed <= nextAvailableDay) {
                    //Making colorcode as a property in the county object (required for mapbox)
                    geoJson.features[countyIndex].properties[daysElapsed + "_color"] = colorCode;
                    daysElapsed++;
                }
            }
            geoJson.features[countyIndex].properties['latestColor'] = colorCode;
        }
    }
}

function updateToolbarLimits() {
    document.getElementById("cases-max").textContent = niceNumber(maxPropValForColorCode);
    dateList = getDateArray(latestDateValue);
    var slider = document.getElementById("slider");
    slider.max = dateList.length - 1;
    slider.value = date_diff_indays(startDate, latestDateValue);
}


// initializes map
function initMap(geoJson) {
    map = new mapboxgl.Map({
        container: 'map',
        style: mapStyle,
        center: [-89.651607, 39.781232],
        zoom: 3.5,
        minZoom: 3.5,
        maxZoom: 12,
        dragRotate: false,
        touchZoomRotate: false
    });

    var popup = new mapboxgl.Popup({
        closeButton: false
    });

    // county geometry
    const countyLayerGeometry = {
        'id': 'county-layer',
        'type': 'fill',
        'source': 'county',
        'paint': {
            'fill-outline-color': 'rgba(50, 0, 50, 0.3)',
            'fill-opacity': 0.4
        }
    };

    // init of map with blank geojson
    map.on('load', function () {
        map.addSource('county', {
            'type': 'geojson',
            'data': geoJson
        });
        map.addLayer(countyLayerGeometry);
        map.on('mousemove', 'county-layer', function (e) {
            // Change the cursor style as a UI indicator.
            map.getCanvas().style.cursor = 'pointer';
            popup
                .setLngLat(e.lngLat)
                .setHTML(getPopupContent(e.features[0]))
                .addTo(map);
        });
        map.on('mouseleave', 'county', resetPopupProerties);
        map.on('mouseenter', 'county', resetPopupProerties);
        
        // filter listener
        document.getElementById("slider").addEventListener('input', e =>filterBy(e.target.value));

        // filter by initial slider position
        if (dateList) {
            filterBy(lastDayElapsed);
            document.getElementById("map-overlay-inner").style.visibility = "visible";
        }
    }); // eof map.onLoad

    function resetPopupProerties() {
        map.getCanvas().style.cursor = '';
        popup.remove();
        overlay.style.display = 'none';
    }
} // eof initMap


function getPopupContent(feature) {

    // Grab our confirmed cases array for the hovered county
    const casesConfirmed = JSON.parse(feature.properties['confirmed_cases']);

    // Start the popup string
    let stringBuilder = "<strong class=\"map-info-box-title\">" + feature.properties.NAME + "</strong>";
    stringBuilder += "<div class=\"map-info-box\">" + currentDate;
    let currentCaseElement = getCurrentElement(casesConfirmed);
    if (currentCaseElement) {
        stringBuilder += "<br><strong>Confirmed Cases:</strong> " + niceNumber(currentCaseElement[countKey]);
        let currentDeathElement = null;
        // grab our deaths array - we get deaths only if we have cases. 
        const deathsConfirmed = JSON.parse(feature.properties['deaths']);
        currentDeathElement = getCurrentElement(deathsConfirmed);
        if (currentDeathElement) {
            stringBuilder += "<br><strong>Deaths:</strong> " + niceNumber(currentDeathElement[countKey]);
        }
        else {
            stringBuilder += "<br>No deaths in this county.";
        }
    }

    else {
        stringBuilder += "<br>There are no reported cases on this day.";
    }
    stringBuilder += "</div>";
    return stringBuilder


    function getCurrentElement(propList) {
        let currentElement = null;
        if (propList && propList.length > 0) {
            propList.forEach((element, index) => {
                if (element[daysElapsedKey] < currentDayValue) {
                    currentElement = element;
                }
            });
        }
        return currentElement;
    }
}

// Update the colors of map based on selected date
function filterBy(date) {
    date_color = date + "_color"
    map.setPaintProperty('county-layer', 'fill-color',
        [
            "case",
            ["!=", ["get", date_color], null], ["get", date_color],
            "rgba(0,0,0,0)"
        ]
    );
    currentDayValue = dateList[date];
    currentDate = niceDate(addToDate(startDate, dateList[date]));
    document.getElementById("map-date").textContent = currentDate;
}



// function functions -------------------------------------------------------------

function callService(url, callback) {
    $.ajax({
        method: "GET",
        url: config.server_ip + url,
        processData: false,
        contentType: false,
        encType: "multipart/form-data",
        success: callback,
        error: ajaxErrorHandle
    });
}

// call methods -------------------------------------------
mainInit();