import os

import psycopg2


def setup_db_connection():
    print("Setting up DB connection")
    # dbName = os.environ.get("POSTGRES_DB", "aveey_dev")
    # user = os.environ.get("POSTGRES_USER", "aveey_dev")
    # password = os.environ.get("POSTGRES_PASSWORD", "aveeyDevPassword")
    # host = os.environ.get("POSTGRES_HOST", "localhost")
    # port = os.environ.get("POSTGRES_PORT", 5432)
    database_url = os.environ.get("DATABASE_URL")

    return psycopg2.connect(database_url, sslmode='require')
