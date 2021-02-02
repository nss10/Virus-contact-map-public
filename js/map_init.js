// Global objects
let map = null;         // Mapbox GL object
let dateList = null;    // List of dates to filter by
let maxPropValForColorCode = 0; // Max cases to determine the min and max for gradient
let currentDate = '';       // Current day determined from the slider
let currentDayValue = 0;    // Numerical value of current day determined from the slider
let latestDateValue;
let lastDayElapsed;
const mapStyle = 'mapbox://styles/mapbox/dark-v10';
const countKey = config['ccd']['count'];
const daysElapsedKey = config['ccd']['daysElapsed'];
const FETCH_RETRY_LIMIT = 3;
const htmlElements = {
    slider : document.getElementById("slider"),
    sliderToolbar : document.getElementById("map-overlay-inner"),
    maxCasesDiv :  document.getElementById("cases-max"),
    dateLabel : document.getElementById("map-date")

}

// initializer functions -------------------------------------------------------
// main initializer
async function mainInit() {
    drawBlankMap();

    // load erics
    let geoJsonPromise = fetch_retry(config.geoJsonData_url, FETCH_RETRY_LIMIT);
    let countyCasesPromise = fetch_retry(config.countyCases_url, FETCH_RETRY_LIMIT);

    let [geoJson,countyCases] = await Promise.all([geoJsonPromise, countyCasesPromise]);
    displayFooterMessage("Loading initial county data, please wait...", false);
    loadInitialData(geoJson, countyCases);
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

// ajax call to populate county data with formated filter
function loadInitialData(geoJson, countyCases) {
    let counties = countyCases.collection
    let colorCodes = countyCases.colorCodes
    lastDayElapsed = countyCases.lastAvailableDay;

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
            addColorCodes(geoJson, cases, colorCodes, lastDayElapsed);

            geoJson.features[countyIndex].properties['confirmed_cases'] = cases;
            geoJson.features[countyIndex].properties['deaths'] = deaths;
        }
    }
    displayFooterMessage("Background loading complete. Map is fully ready.", false);

    latestDateValue = addToDate(startDate, lastDayElapsed)
    initMap(geoJson);
    updateToolbarLimits();
    
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
    function addColorCodes(geoJson, prop, colorCodes, lastDayElapsed) {
        if (prop.length <= 0) {
            return;
        }
        let colorCode;
        // iterate from the first day in cases until today
        for (let propIndex = 0; propIndex < prop.length; propIndex++) {
            let daysElapsed = prop[propIndex][daysElapsedKey];
            let caseCount = prop[propIndex][countKey];
            maxPropValForColorCode = Math.max(caseCount,maxPropValForColorCode);
            colorCode = getColorCode(colorCodes, caseCount);

            // next date where number of cases is changed
            let nextAvailableDay = (propIndex < prop.length-1) ? prop[propIndex + 1][daysElapsedKey] : lastDayElapsed;
            while (daysElapsed <= nextAvailableDay) {
                //Making colorcode as a property in the county object (required for mapbox)
                geoJson.features[countyIndex].properties[daysElapsed + "_color"] = colorCode;
                daysElapsed++;
            }
        }
    }
}

function updateToolbarLimits() {
    htmlElements.maxCasesDiv.textContent = niceNumber(maxPropValForColorCode);
    dateList = getDateArray(latestDateValue);
    htmlElements.slider.max = dateList.length - 1;
    htmlElements.slider.value = date_diff_indays(startDate, latestDateValue);
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
        map.addSource('county', {'type': 'geojson','data': geoJson});
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
        htmlElements.slider.addEventListener('input', e =>filterBy(e.target.value));

        // filter by initial slider position
        if (dateList) {
            filterBy(lastDayElapsed);
            htmlElements.sliderToolbar.style.visibility = "visible";
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
    htmlElements.dateLabel.textContent = currentDate;
}



// function functions -------------------------------------------------------------

async function fetch_retry(url,attempts){
    try{
        let response = await fetch(config.server_ip + url);
        if(response.status!=200){
            throw response.statusText;
        }
        return await response.json();
        
    }
    catch(err){
        if(attempts==0){
            displayFooterMessage("An error occured while fetching data from the server.", true);
            throw err;
        }
        return fetch_retry(url,attempts-1);

    }
}
// call methods -------------------------------------------
mainInit(); 