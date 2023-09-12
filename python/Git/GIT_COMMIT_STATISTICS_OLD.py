import subprocess
from datetime import datetime, timedelta
import pyodbc
import os
import sys
import traceback

# Class Exception for non-zero exit code 
class NotGitRepositoryError(Exception):
    pass

# Get list of commit sha hashes
def commit_hash_per_day(repository):
    try:
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) 
        formatted_date = start_date.strftime('%Y-%m-%d %H:%M:%S')
        git_cmd = f'git -C "{repository}" log --all --after="{formatted_date}" --pretty=format:"%H|%an|%d|%ci|%s"'
        output = subprocess.check_output(git_cmd, shell=True).decode('utf-8').strip().split('\n')
        return output
    except NotGitRepositoryError as e:
        print(e)
        
        
# Write data to database defined in config file      
def statistics_write_to_DB(data, connection):
    if len(data) > 0:
        try:
            cursor = connection.cursor()

            for line in data:
                commit_id, ldap_user, branch, commit_date_str, comment = line.split('|')

                branch = branch.replace('(origin/', '').replace(')', '').strip()

                input_date = datetime.strptime(commit_date_str, "%Y-%m-%d %H:%M:%S %z")
                commit_date = input_date.strftime("%Y-%m-%d %H:%M:%S")

                # print(f"Author: {ldap_user}, Commit ID: {commit_id}, Branch: {branch}, Commit Date: {commit_date}, Comments: {comment}\n")

                sql_insert = "INSERT INTO Commits (CommitID, LdapUser, Branch, CommitDate, Comments) VALUES (?, ?, ?, ?, ?)"

                cursor.execute(sql_insert, (commit_id, ldap_user, branch, commit_date, comment))

            connection.commit()
            
            print("================================== Data saved to the database successfully. =================================================")
        except Exception as e:
            print(f"An error occurred while saving data to the database: {e}")
            print(traceback.format_exc())
            sys.exit(1)


# Reading script configuration form file 
def read_configuration_from_file(file_path):
    if os.path.exists(file_path):
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
    else:
        print(f"Could not find configuration file at path {file_path}. Please correct the path.")
        sys.exit()



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

    CONNECTION_STRING = "DRIVER={{{driver}}};SERVER={server_name};DATABASE={database_name};UID={username};PWD={password};ENCODING=utf-8".format(
        driver=DRIVER.strip('"{}"'),
        server_name=SERVER_NAME,
        database_name=DATABASE_NAME,
        username=DB_USERNAME,
        password=DB_PASSWORD
    )
    return str(REPO_PATH),branches,CONNECTION_STRING


# FILE PATH TO READ DATABASE CONFIGURATION
CONF_DIR = r"C:\GitCommitStatisticsUtils"
CONF_FILE = "script_configuration.txt"
CONFIGURATION_FILE_PATH = os.path.join(CONF_DIR,CONF_FILE)

# SET UP DATABASE CONNECTION INFORMATION
REPO_PATH,BRANCHES,CONNECTION_STRING = configuration_format(CONFIGURATION_FILE_PATH)

# GET LIST OF COMMIT HASHES
LIST_OF_COMMIT_HASHES = commit_hash_per_day(REPO_PATH)

# CALL THE DB FUNCTIONS AND SAVE DATA TO DATABASE
CONNECTION = pyodbc.connect(CONNECTION_STRING)
statistics_write_to_DB(LIST_OF_COMMIT_HASHES, CONNECTION)

# CLOSE CONNECTION AFTER DATA WRITE TO DB
CONNECTION.close()