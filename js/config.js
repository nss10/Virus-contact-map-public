config = {
    server_local: "http://localhost:5000",
    server_remote: "<remote_server_address_here>",
    backend_remote: false,
    countyCases_url: "/countyCasesData",
    geoJsonData_url: "/geometryData",
    mapbox_token: 'pk.eyJ1IjoiemFjaGFyeTgxNiIsImEiOiJjazd6NXN2eWwwMml0M2tvNGo2c3JkcGFpIn0.aB1upejZ61JQjb_z2g1NuA'
}

config['server_ip'] = config.backend_remote ? config.server_remote : config.server_local;
config['ccd'] = {
    GEO_ID: "ID",
    NAME: "N",
    confirmed_cases: "CC",
    deaths: "D",
    daysElapsed: "DE",
    count: "C",
    isPredicted : "IP"
}

var colorArray = ['#FEC4E9', '#F5B3D4', '#EDA2C0', '#E592AC', '#DC8095', '#D36E7F', '#C85964', '#BE454C', '#B6373A', '#B12B2C', '#A91C19'];