import subprocess
from datetime import datetime, timedelta
import codecs
import pyodbc


# Class Exception for non-zero exit code 
class NotGitRepositoryError(Exception):
    pass


# Get list of commit sha hashes
def commit_hash_per_week(repository):
    try:
        # weeks_ago = 1
        # start_date = datetime.now() - timedelta(weeks=weeks_ago)
        start_date = datetime(datetime.now().year, 1, 1)  # Start of the year 2023
        formatted_date = start_date.strftime('%Y-%m-%d %H:%M:%S')
        git_log_command = f'git -C "{repository}" log --all --after="{formatted_date}" --pretty=format:%H'
        git_log_output = subprocess.check_output(git_log_command, cwd=repository).decode('utf-8')
        commit_hashes = git_log_output.strip().split('\n')
        return commit_hashes
    except subprocess.CalledProcessError as e:
        print(e)
    except FileNotFoundError as e:
        print(e)


def commit_statistics(list_commit_hash, repo_path):
    result = []

    for commit_id in list_commit_hash:
        print(f"Downloading statistics for commit ID: {commit_id}")
        commit_info_command = ['git', 'show', '--stat', '--oneline', '--name-status', commit_id]
        commit_info_output = subprocess.check_output(commit_info_command, cwd=repo_path).decode('utf-8')

        commit_info_lines = commit_info_output.strip().split('\n')

        changed_files = list_of_changed_files(commit_info_lines)

        for file_path in changed_files:
            diff_stats_command = ['git', 'diff', '--numstat', commit_id + '^', commit_id, '--', file_path]
            diff_stats_output = subprocess.check_output(diff_stats_command, cwd=repo_path).decode('utf-8').strip()

            if diff_stats_output:
                lines_added = 0
                lines_deleted = 0

                for stat in diff_stats_output.strip().split('\n'):
                    parts = stat.strip().split('\t')
                    if len(parts) == 3:
                        added, deleted, _ = parts
                        if added != '-' and deleted != '-':
                            lines_added += int(added)
                            lines_deleted += int(deleted)

                modified_lines = lines_added + lines_deleted

                # Check if the data already exists in the result list
                commit_exists = False
                for item in result:
                    if item[0] == commit_id and item[1].lower() == file_path.lower():
                        commit_exists = True
                        break

                # Add the data to the result list if it doesn't already exist
                if not commit_exists:
                    result.append([commit_id, file_path, lines_added, modified_lines, lines_deleted])

    return result



# Decode cyclic filenames 
def list_of_changed_files(commit_lines):
    changed_files = []

    for line in commit_lines[1:]:
        parts = line.split('\t')
        if len(parts) >= 2:
            file_status = parts[0]
            file_path = '\t'.join(parts[1:])
            if file_status != ' ':
                try:
                    decoded_file_path = codecs.escape_decode(file_path)[0].decode('utf-8')
                except UnicodeDecodeError:
                    decoded_file_path = file_path
                changed_files.append(decoded_file_path)

    return changed_files

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

# Write data to database defined in config file
def statistics_write_to_DB(data, connection):
    
    try:
        cursor = connection.cursor()
        
        for commit_id, file_path, lines_added, modified_lines, lines_deleted in data:
            
            print(f"COMMIT_ID {commit_id}, FILE_PATH: {file_path}, LINES_ADDED: {lines_added}, MODIFIED_LINES: {modified_lines}, LINES_DELETED: {lines_deleted}")
            
            
            sql_insert = "INSERT INTO CommitsAffectedFiles(CommitID,ChangeFileName, AddedLines, ModifiedLines, DeletedLines) VALUES(?,?,?,?,?)"
            cursor.execute(sql_insert, (commit_id, file_path, lines_added, modified_lines, lines_deleted))
        
        connection.commit()
        
        print("================================== Data saved to the database successfully. =================================================")
    except Exception as e:
        print(f"An error occurred while saving data to the database: {e}")


# FILE PATH TO READ DATABASE CONFIGURATION
CONFIGURATION_FILE_PATH = "./config/script_configuration.txt"

# SET UP DATABASE CONNECTION INFORMATION
REPO_PATH,BRANCHES,CONNECTION_STRING = configuration_format(CONFIGURATION_FILE_PATH)

# GET LIST OF COMMIT HASHES
LIST_OF_COMMIT_HASHES = commit_hash_per_week(REPO_PATH)

# GET AFFECTED FILES, ADDED LINES, MODIFIED LINES, DELETED LINES FROM SHA HASHES
DATA = commit_statistics(LIST_OF_COMMIT_HASHES,REPO_PATH)

# CALL THE DB FUNCTIONS AND SAVE DATA TO DATABASE
CONNECTION = pyodbc.connect(CONNECTION_STRING)
statistics_write_to_DB(DATA, CONNECTION)

# CLOSE CONNECTION AFTER DATA WRITE TO DB
CONNECTION.close()

