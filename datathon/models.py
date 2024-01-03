from django.db import models

import pyodbc


def get_db_connection():
    # TODO variables should be import from setting
    driver = '{ODBC Driver 17 for SQL Server}'
    server = 'datathon.database.windows.net'
    database = 'datathon_mssql'
    username = 'datathonuser'
    password = '1qaz@WSX3edc'

    connection_string = f"DRIVER={driver};"\
                        +f"SERVER={server};"\
                        +f"DATABASE={database};"\
                        +f"UID={username};"\
                        +f"PWD={password}"

    conn = pyodbc.connect(connection_string)
    return conn
