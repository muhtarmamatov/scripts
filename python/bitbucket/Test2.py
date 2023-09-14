import pyodbc

def search_commit_id_from_db(connection, commit_hash):
    print(commit_hash)
    try:
        cursor = connection.cursor()
        sql_query = f"SELECT CommitID FROM Commits WHERE CommitID LIKE '{commit_hash}%'"
        # Execute the search query
        cursor.execute(sql_query)
        
        row = cursor.fetchone()
        commit_id = None  # Initialize commit_id variable outside the loop

        while row is not None:
            commit_id = row[0][1:]  # Extract the commit_id from the first element of the tuple
            row = cursor.fetchone()

        return commit_id  # Return the last fetched commit_id after the loop completes
    except Exception as e:
        print(f"An error occurred while getting data from the database: {e}")
        return ""



# Reading script configuration form file 
def read_configuration_from_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    configuration = {}

    for line in lines:
        line = line.strip()
        if line:
            try:
                key, *value_parts = line.split('=')
                value = '='.join(value_parts)
                configuration[key.strip()] = value.strip()
            except ValueError:
                print(f"Skipping line: {line}. Invalid format.")

    return configuration

# Parse script configuration 
def configuration_format(configuration_file_path):
    CONFIGURATION = read_configuration_from_file(configuration_file_path)
    DRIVER = CONFIGURATION.get('DRIVER','')
    SERVER_NAME = CONFIGURATION.get('SERVER', '')
    DATABASE_NAME = CONFIGURATION.get('DATABASE', '')
    DB_USERNAME = CONFIGURATION.get('UID', '')
    DB_PASSWORD = CONFIGURATION.get('PWD', '')
    REPO_PATH = CONFIGURATION.get('REPO_PATH', '')
    BRANCHES = CONFIGURATION.get('BRANCHES', '')
    branches = [branch.strip().strip('[]"\'') for branch in BRANCHES.split(',')]

    CONNECTION_STRING = "DRIVER={{{driver}}};SERVER={server_name};DATABASE={database_name};UID={username};PWD={password}".format(
        driver=DRIVER.strip('"{}"'),
        server_name=SERVER_NAME,
        database_name=DATABASE_NAME,
        username=DB_USERNAME,
        password=DB_PASSWORD
    )
    return str(REPO_PATH),branches,CONNECTION_STRING

# FILE PATH TO READ DATABASE CONFIGURATION
CONFIGURATION_FILE_PATH = "./financesoft/conf/script_configuration.txt"

# SET UP DATABASE CONNECTION INFORMATION

REPO_PATH,BRANCHES,CONNECTION_STRING = configuration_format(CONFIGURATION_FILE_PATH)


CONNECTION = pyodbc.connect(CONNECTION_STRING)

result = search_commit_id_from_db(CONNECTION,'f339e97e0a952132')

print(result)

# CLOSE CONNECTION AFTER DATA WRITE TO DB
CONNECTION.close()

