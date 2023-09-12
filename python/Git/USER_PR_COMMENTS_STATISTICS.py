import requests
import sys
import re
import pyodbc
from collections import defaultdict
import traceback

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

# Format configuration 
def configuration_format(configuration_file_path):
    CONFIGURATION = read_configuration_from_file(configuration_file_path)
    DRIVER = CONFIGURATION.get('DRIVER','')
    SERVER_NAME = CONFIGURATION.get('SERVER', '')
    DATABASE_NAME = CONFIGURATION.get('DATABASE', '')
    DB_USERNAME = CONFIGURATION.get('UID', '')
    DB_PASSWORD = CONFIGURATION.get('PWD', '')
    API_TOKEN = CONFIGURATION.get('API_TOKEN', '')
    WORKSPACE = CONFIGURATION.get('WORKSPACE', '')
    REPO_SLUG = CONFIGURATION.get('REPO_SLUG', '')
    CONNECTION_STRING = "DRIVER={{{driver}}};SERVER={server_name};DATABASE={database_name};UID={username};PWD={password}".format(
        driver=DRIVER.strip('"{}"'),
        server_name=SERVER_NAME,
        database_name=DATABASE_NAME,
        username=DB_USERNAME,
        password=DB_PASSWORD
    )
    return API_TOKEN,WORKSPACE,REPO_SLUG,CONNECTION_STRING


# Method to get dates from user input
def get_dates_from_user():
    while True:
        update_date = input("Enter the since date (YYYY-MM-DD): ")

        # Check if dates are in the correct format
        date_regex = r'^\d{4}-\d{2}-\d{2}$'
        if re.match(date_regex, update_date):
            return update_date
        else:
            print("Invalid date format. Please enter dates in the format YYYY-MM-DD.")


# Method to get pull requests
def get_pull_requests(url, headers, date_since):
    params = {
        'state': 'MERGED',
        'fields': 'values.id,values.state,values.author.display_name,values.source,values.destination,values.merge_commit.hash,values.links.html.href,next',
        'q': f'created_on>={date_since}'
    }

    pull_requests = []

    while url:
        response = requests.get(url, headers=headers, params=params)

        try:
            # Raise an exception for non-2xx response codes
            response.raise_for_status()

            # Get body of response
            data = response.json()
        except (requests.HTTPError, requests.exceptions.RequestException) as e:
            print("Error retrieving pull requests:", str(e))
            sys.exit(1)

        pull_requests.extend(data.get("values", []))
        url = data.get("next")

        params.pop('state', None)
        params.pop('fields', None)
        params.pop('q',None)

    return pull_requests

# Method to get PR IDs
def get_pr_ids(prs_data):
    pr_ids = []

    for pr_id in prs_data:
        pr_ids.append(pr_id["id"])
    return pr_ids


# Method to get PR activity
def get_pr_activity(workspace, repo_slug, pr_id, access_token):
    url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}/activity"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data.get('values', []), data.get('next')
    else:
        print(f"Failed to retrieve activity for PR {pr_id}: {response.status_code} - {response.text}")
        return [], None

# Method for getting comments from activity
def find_comments_per_user(activity, commit_hash, pr_id, pr_author, source_branch, destination_branch):
    user_stats = defaultdict(lambda: {'reviewer_name': "", 'source_branch': "", 'destination_branch': "", 'comments': []})  # Modify the default factory to initialize 'comments' as a list

    for entry in activity:
        is_comment_exist = entry.get("comment", {})
        if is_comment_exist:
            comment_user_display_name = entry.get("comment", {}).get("user", {}).get("display_name")
            #if comment_user_display_name and comment_user_display_name in users:
            user_stats[comment_user_display_name]['reviewer_name'] = comment_user_display_name
            comment_text = entry.get("comment", {}).get("content", {}).get("raw")
            if comment_text:
                user_stats[comment_user_display_name]['comments'].append(comment_text)  # Append comment to the 'comments' list

    csv_data = []
    for reviewer_name, reviewer_stats in user_stats.items():
        comments_combined = '\n'.join([f"{i+1}. {comment}" for i, comment in enumerate(reviewer_stats['comments'])])  # Combine comments into a single string with numbering
        csv_data.append([pr_id, pr_author, source_branch, destination_branch, reviewer_name, comments_combined, commit_hash])

    return csv_data

# Building user commnets statistics
def build_pr_comments_statistics(users, prs_data,workspace, repo_slug, api_token,headers):
    csv_data = []
    for pr in prs_data:
        pr_id = pr['id']
        pr_author = pr['author']['display_name']
        #pr_link = pr['links']['html']['href']
        source_branch = pr.get('source', {}).get('branch', {}).get('name', 'N/A')
        destination_branch = pr.get('destination', {}).get('branch', {}).get('name', 'N/A')
        state = pr['state']
        commit_hash = ''
        if(state == "OPEN"):
            commit_hash = pr['source']['commit']['hash']
        elif(state == "MERGED"):
            commit_hash = pr['merge_commit']['hash']
        
        activity, next_page = get_pr_activity(workspace, repo_slug, pr_id, api_token)

        print("Downloading PR ID:", pr_id)
        while activity:
            reviewer_comments = find_comments_per_user(activity, commit_hash, pr_id, pr_author,source_branch,destination_branch)

            if next_page:
                response = requests.get(next_page, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    activity = data.get('values', [])
                    next_page = data.get('next')
                else:
                    print(f"Failed to retrieve next page for PR {pr_id}: {response.status_code} - {response.text}")
                    break
            else:
                break
        csv_data.extend(reviewer_comments)
    
    return csv_data

# Write data to database defined in config file
def statistics_write_to_DB(data, connection):
    try:
        cursor = connection.cursor()
        for PullRequestID, Author, SourceBranch, DestinationBranch, ReviewerName, ReviewerComments, CommitHash in data:
            CommitID = search_commit_id_from_db(connection,CommitHash)
            if(CommitID is not None):
                print(PullRequestID,CommitHash, Author, SourceBranch, DestinationBranch, ReviewerName, ReviewerComments)
                sql_insert = "INSERT INTO PullRequestCommentStatistics(PullRequestID, CommitID, Author, SourceBranch, DestinationBranch, ReviewerName, ReviewerComments) VALUES(?,?,?,?,?,?,?)"
                cursor.execute(sql_insert,(PullRequestID,CommitID, Author,SourceBranch,DestinationBranch,ReviewerName,ReviewerComments))
        connection.commit()
        print("================================== Data saved to the database successfully. =================================================")
    except Exception as e:
        print(f"An error occurred while saving data to the database: {e}")
        print(traceback.format_exc())
        sys.exit(1)

# Method for searching full sha hashes from Commits table
def search_commit_id_from_db(connection, commit_hash):
    try:
        cursor = connection.cursor()
        sql_query = f"SELECT CommitID FROM Commits WHERE CommitID LIKE '{commit_hash}%'"
        # Execute the search query
        cursor.execute(sql_query)
        
        row = cursor.fetchone()
        commit_id = None  # Initialize commit_id variable outside the loop

        while row is not None:
            commit_id = row[0][0:]  # Extract the commit_id from the first element of the tuple
            row = cursor.fetchone()
            print(f"Found hash: {commit_id}")

        return commit_id  # Return the last fetched commit_id after the loop completes
    except Exception as e:
        print(f"An error occurred while getting data from the database: {e}")
        return ""
            
    



# FILE PATH TO READ DATABASE CONFIGURATION
CONFIGURATION_FILE_PATH = "./config/script_configuration.txt"

# SET UP DATABASE CONNECTION INFORMATION
API_TOKEN,WORKSPACE,REPO_SLUG,CONNECTION_STRING = configuration_format(CONFIGURATION_FILE_PATH)

# GLOBAL VARIABLES 
BASE_URL = 'https://api.bitbucket.org/2.0'
PERMISSION_REPO_URL = f"{BASE_URL}/workspaces/{WORKSPACE}/permissions/repositories/{REPO_SLUG}"
PULL_REQUEST_API_URL = f"{BASE_URL}/repositories/{WORKSPACE}/{REPO_SLUG}/pullrequests"
USERS = ["Ilyas Masirov", "Таалай", "Ermek Mambetov", "Mirbek Imanbaev", "Arslan Dzhunushev", "Timur Bostanov"]



# BITBUCKET API CONNECTION
HEADERS = {"Authorization": f"Bearer {API_TOKEN}", "Accept": "application/json"}

# GET DATE FROM USER
DATE_FROM = get_dates_from_user()

# GET PULL REQUESTS FROM ENTERED DATE
PRS_DATA = get_pull_requests(PULL_REQUEST_API_URL,HEADERS,DATE_FROM)


# GET PULL REQUESTS IDS
PR_IDS = get_pr_ids(PRS_DATA)

# GETTING FINAL DATA TO WRITE TO DATABASE
DATA = build_pr_comments_statistics(USERS,PRS_DATA,WORKSPACE,REPO_SLUG,API_TOKEN,HEADERS)


# CALL THE DB FUNCTIONS AND SAVE DATA TO DATABASE
CONNECTION = pyodbc.connect(CONNECTION_STRING)
statistics_write_to_DB(DATA, CONNECTION)

# CLOSE CONNECTION AFTER DATA WRITE TO DB
CONNECTION.close()