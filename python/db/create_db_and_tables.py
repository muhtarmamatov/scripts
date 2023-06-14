DB_USER = "<DB_USER>"
DB_USER_PASSWORD = "<DB_USER_PASSWORD>"
DB_HOST = "<DB_HOST>"
DB_PORT = "<DB_PORT>"


def connect_to_database(dbname, user, password, host, port):
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname=dbname, user=user, password=password, host=host, port=port
        )
        print("Connected to the database successfully.")
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None
    

import psycopg2


def create_database(database, user, password, host, port):
    """Creates a new database if it doesn't exist."""
    try:
        conn = psycopg2.connect(
            dbname="postgres", user=user, password=password, host=host, port=port
        )
        conn.autocommit = True
        cur = conn.cursor()

        # Check if the database already exists
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (database,))
        exists = cur.fetchone()

        if not exists:
            # Create the database
            cur.execute(f"CREATE DATABASE {database}")
            print(f"Database '{database}' created successfully.")
        else:
            print(f"Database '{database}' already exists.")

        cur.close()
        conn.close()
    except psycopg2.Error as e:
        print(f"Error creating the database: {e}")


def create_tables(conn, tables):
    """Creates tables if they don't exist."""
    try:
        cur = conn.cursor()

        for table in tables:
            table_name = table['name']
            table_definition = table['definition']

            # Create the table if it doesn't exist
            cur.execute(f"CREATE TABLE IF NOT EXISTS {table_name} {table_definition}")
            print(f"Table '{table_name}' created successfully.")

        cur.close()
        conn.commit()
    except psycopg2.Error as e:
        print(f"Error creating the tables: {e}")


TABLES = [
    {
        'name': 'commits_table',
        'definition': '''
            (
                id SERIAL PRIMARY KEY,
                commit_id VARCHAR(40) NOT NULL,
                ldap_user VARCHAR(255) NOT NULL,
                branch VARCHAR(255) NOT NULL,
                commit_date TIMESTAMP NOT NULL,
                comment TEXT NOT NULL
            )
        '''
    },
    {
        'name': 'other_table',
        'definition': '''
            (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                value INTEGER NOT NULL
            )
        '''
    }
]


# create_database("git_statistics", DB_USER, DB_USER_PASSWORD, DB_HOST, DB_PORT)

# conn = connect_to_database("git_statistics", DB_USER, DB_USER_PASSWORD, DB_HOST, DB_PORT)
# if conn is not None:
#     create_tables(conn, tables)