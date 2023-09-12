import requests
import sys
import re
import pyodbc
from collections import defaultdict



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

# def extract_tags_from_description(description, keyboards):
#     result = []
#     for keyboard in keyboards:
#         pattern = rf'{keyboard}\s*=\s*((?:(?!,\s*{keyboard}\s*=).)+)'
#         matches = re.findall(pattern, description)
#         for match in matches:
#             tag_values = [tag.strip() for tag in match.split(",")]
#             for tag_value in tag_values:
#                 result.append(f"Tag_ID: {keyboard}, Tag_Value: {tag_value.strip()}")
#     return result

def extract_tags_from_description(description, keyboards):
    result = []
    for keyboard in keyboards:
        pattern = rf'{keyboard}\s*=\s*((?:(?!,\s*{keyboard}\s*=).)+)'
        #pattern = rf'{keyboard}\s*=\s*((?:(?!,\s*{keyboard}\s*=).+?)\*\*)'
        matches = re.findall(pattern, description)
        for match in matches:
            tag_values = [tag.strip() for tag in match.split(",")]
            for tag_value in tag_values:
                link_match = re.search(r'\[\*\*(.+?)\*\*\]', tag_value)
                if link_match:
                    tag_value = link_match.group(1)
                result.append(f"Tag_ID: {keyboard}, Tag_Value: {tag_value.strip()}")
    return result

def search_tags_in_pr(pull_request, keyboards):
    pr_description = pull_request.get("description", "")
    state = pull_request['state']
    
    commit_hash = ''
    if(state == "OPEN"):
            commit_hash = pull_request['source']['commit']['hash']
    elif(state == "MERGED"):
            commit_hash = pull_request['merge_commit']['hash']
        
    tags_data = extract_tags_from_description(pr_description, keyboards)

    if tags_data:
        result = [f"Commit_ID: {commit_hash}, {tag}" for tag in tags_data]
        return result
    else:
        return None


def get_pull_requests(url, headers, date_since):
    params = {
        'state': 'OPEN, MERGED',
        'fields': 'values.id,values.state,values.title,values.description,values.author.display_name,values.source,values.destination,values.merge_commit.hash,values.links.html.href,next',
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
        params.pop('q', None)

    return pull_requests
# FILE PATH TO READ DATABASE CONFIGURATION
CONFIGURATION_FILE_PATH = "./config/script_configuration.txt"

# SET UP DATABASE CONNECTION INFORMATION
API_TOKEN,WORKSPACE,REPO_SLUG,CONNECTION_STRING = configuration_format(CONFIGURATION_FILE_PATH)

# GLOBAL VARIABLES 
BASE_URL = 'https://api.bitbucket.org/2.0'
PERMISSION_REPO_URL = f"{BASE_URL}/workspaces/{WORKSPACE}/permissions/repositories/{REPO_SLUG}"
PULL_REQUEST_API_URL = f"{BASE_URL}/repositories/{WORKSPACE}/{REPO_SLUG}/pullrequests"



# BITBUCKET API CONNECTION
HEADERS = {"Authorization": f"Bearer {API_TOKEN}", "Accept": "application/json"}


if __name__ == "__main__":
    
    # GET DATE FROM USER
    DATE_FROM = get_dates_from_user()

    # GET PULL REQUESTS FROM ENTERED DATE
    PRS_DATA = get_pull_requests(PULL_REQUEST_API_URL,HEADERS,DATE_FROM)
    
    KEYBOARDS = ['Tasks', 'Bugs']
    
    print("=======================================================")
    print(PRS_DATA)
    print("=======================================================")
    for pr in PRS_DATA:
        pr_id = pr['id']
        print(f"Parsing PR ID: {pr_id}" )
        pr_tags_data = search_tags_in_pr(pr, KEYBOARDS)
        if pr_tags_data:
            for data in pr_tags_data:
                print(data)


