config={
    server_local:"http://localhost:5000",
    server_remote:"http://173.28.146.185:5000",
    backend_remote : true,
    upload_url: "/handleUpload",
    allData_url: "/allData",
    countyCases_url: "/countyCasesData",
    allInfected_url: "/allData",
    countyCases_url: "/countyCasesData",
    ericsData_url: "/ericsData"
}

config['server_ip'] = config.backend_remote ? config.server_remote : config.server_local;

var colorArray = ['#FEC4E9','#F5B3D4','#EDA2C0','#E592AC','#DC8095','#D36E7F','#C85964','#BE454C','#B6373A','#B12B2C','#A91C19'];