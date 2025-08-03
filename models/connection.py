import mysql.connector
import toml

def get_connection():
    try:
        secrets = toml.load("secrets.toml")
        conn = mysql.connector.connect(
            host=secrets['database']['host'],
            database=secrets['database']['name'],
            user=secrets['database']['user'],
            password=secrets['database']['password']
        )
        return conn
    except:
        return None