#!/usr/bin/env python3

import requests
import psycopg2
import os
from datetime import datetime

def setup_db_connection():
    print("Setting up DB connection")
    dbName = os.environ.get("POSTGRES_DB", "aveey_dev")
    user = os.environ.get("POSTGRES_USER", "aveey_dev")
    password = os.environ.get("POSTGRES_PASSWORD", "aveeyDevPassword")
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", 5432)

    return psycopg2.connect(dbname=dbName, user=user, password=password, host=host, port=port)

def get_space_pop():
    print("Getting Space Population")
    response = requests.get("http://api.open-notify.org/astros.json")
    pop = response.json()["number"]
    print("Current Space Population is %s" % pop)
    return pop

def save_space_pop(dbConnection):
    spacePop = get_space_pop()
    with dbConnection:
        with dbConnection.cursor() as cursor:
            cursor.execute("INSERT INTO space_pop (pop) VALUES (%s)", (spacePop,))

if __name__ == "__main__":
    connection = setup_db_connection()
    save_space_pop(connection)
