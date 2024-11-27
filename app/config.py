class Config:
    DATABASE_CONNECTION = (
        "Driver={ODBC Driver 18 for SQL Server};"
        "Server=localhost;"
        "Database=Futbol;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
