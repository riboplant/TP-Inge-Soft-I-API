class db_settings():
    user: str = "avnadmin"
    password: str = "AVNS_Jjvv_4zuzfe561yPPTV"
    host: str = "sql-db-inge-soft-tp.l.aivencloud.com"
    port: int = 14430
    name: str = "defaultdb"

DBSettings = db_settings()

class auth_settings():
    key: str = "83daa0256a2289b0fb23693bf1f6034d44396675749244721a2b20e896e11662"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
AuthSettings = auth_settings()