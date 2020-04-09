config={
    server_local:"http://localhost:5000",
    server_remote:"http://173.28.146.185:5000",
    backend_remote : true,
    upload_url: "/handleUpload",
    allData_url: "/allData"
}

config['server_ip'] = config.backend_remote ? config.server_remote : config.server_local;