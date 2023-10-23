
platform_config = [
    {
        "name" : "logger-db",
        "server_url": "mongodb+srv://pranshu_mongo:iasproject@cluster0.svcqjdj.mongodb.net/?retryWrites=true&w=majority",
        "db_name": "LOGS"
    },
    {
        "name" : "platform-db",
        "server_url": "mongodb+srv://pranshu_mongo:iasproject@cluster0.svcqjdj.mongodb.net/?retryWrites=true&w=majority",
        "db_name": "IAS_test_1"
    },
    {
        "name" : "monitoring-db",
        "server_url": "mongodb+srv://pranshu_mongo:iasproject@cluster0.svcqjdj.mongodb.net/?retryWrites=true&w=majority",
        "db_name": "M_FT"
    },
    {
        "name": "acr_info",
        "user_name":  "testimages01",
        "password": "EnQFZBylKmDFlOEPuf1LQ3ZYvKxxlbb1Qd8uYdXGQw+ACRBcl3xB",
        "login_server": "testimages01.azurecr.io"
    },
    {
        "name": "blob_storage",
        "server_url": "https://applicationrepo326.blob.core.windows.net/",
        "container_name": "appdb"
    }
]
