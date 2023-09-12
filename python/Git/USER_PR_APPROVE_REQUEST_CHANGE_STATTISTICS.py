import requests
import csv
import sys
import re
import json
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


# Method to get repository users
def get_repository_users(url, headers):
    users = []

    while url:
        response = requests.get(url, headers=headers)
        data = response.json()
        users.extend(data['values'])
        url = data.get('next')

    return users


# Method to get pull requests
def get_pull_requests(pull_request_api_url, headers, date_from):
    params = {
        'state': 'OPEN,MERGED',
        'fields': 'values.id,values.author,values.state,values.updated_on,values.created_on,next,pagelen',
        'q': f'created_on>={date_from}'
    }

    pull_requests = []
    next_url = pull_request_api_url

    while next_url:
        response = requests.get(next_url, headers=headers, params=params)

        try:
            response.raise_for_status()  # Raise an exception for non-2xx response codes
            data = response.json()
        except (requests.HTTPError, requests.exceptions.RequestException) as e:
            print("Error retrieving pull requests:", str(e))
            sys.exit()

        pull_requests.extend(data.get("values", []))
        next_url = data.get("next")

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
    
# Method to count PR approvals and changes requested
def count_approved_and_changes(activity):
    user_stats = defaultdict(lambda: {'approved': 0, 'changes_requested': 0})

    for entry in activity:
        if 'changes_requested' in entry:
            user = entry['changes_requested']['user']['display_name']
            user_stats[user]['changes_requested'] += 1
        elif 'approval' in entry:
            user = entry['approval']['user']['display_name']
            user_stats[user]['approved'] += 1

    return user_stats

# Method for calculating approves and request changes per user
def build_approve_requestchanges_statistics(pr_ids, workspace, repo_slug, api_token):
    user_stats = defaultdict(lambda: {'approved': 0, 'changes_requested': 0})
    
    for pr_id in pr_ids:
        activity, next_page = get_pr_activity(workspace, repo_slug, pr_id, api_token)

        while activity:
            pr_stats = count_approved_and_changes(activity)

            for user, stats in pr_stats.items():
                user_stats[user]['approved'] += stats['approved']
                user_stats[user]['changes_requested'] += stats['changes_requested']

            if next_page:
                response = requests.get(next_page, headers={"Authorization": f"Bearer {api_token}"})
                if response.status_code == 200:
                    data = response.json()
                    activity = data.get('values', [])
                    next_page = data.get('next')
                else:
                    print(f"Failed to retrieve next page for PR {pr_id}: {response.status_code} - {response.text}")
                    break
            else:
                break
    return user_stats


# Build statistics per user
def get_user_pr_stats(user_data, pr_data, user_stats):
    user_stats_list = []

    for user in user_data:
        user_display_name = user['user']['display_name']
        prs_by_user = [pr for pr in pr_data if pr["author"]["display_name"] == user_display_name]
        pr_count = len(prs_by_user)

        user_stat = {
            'User': user_display_name,
            'Total PR': pr_count,
            'Amount Of Approved PR': user_stats[user_display_name]['approved'],
            'Amount Of Requested Changes': user_stats[user_display_name]['changes_requested']
        }

        user_stats_list.append(user_stat)

    return user_stats_list




# FILE PATH TO READ DATABASE CONFIGURATION
CONFIGURATION_FILE_PATH = "./config/script_configuration.txt"

# SET UP DATABASE CONNECTION INFORMATION
API_TOKEN,WORKSPACE,REPO_SLUG,CONNECTION_STRING = configuration_format(CONFIGURATION_FILE_PATH)


# GET DATE FROM USER
DATE_FROM = get_dates_from_user()

# GLOBAL VARIABLES 
BASE_URL = 'https://api.bitbucket.org/2.0'
PERMISSION_REPO_URL = f"{BASE_URL}/workspaces/{WORKSPACE}/permissions/repositories/{REPO_SLUG}"
PULL_REQUEST_API_URL = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/pullrequests"

# BITBUCKET API CONNECTION
HEADERS = {"Authorization": f"Bearer {API_TOKEN}", "Accept": "application/json"}


# GET USER LIST FROM BITBUCKET 
USER_DATA = get_repository_users(PERMISSION_REPO_URL,HEADERS)

# GET PULL REQUESTS FROM ENTERED DATE
PRS_DATA = get_pull_requests(PULL_REQUEST_API_URL, HEADERS, DATE_FROM)

# GET LIST OF PR IDS
PRS_IDS = get_pr_ids(PRS_DATA)

# BUILD USER STATS FROM ACTIVITY ENDPOINT 
PR_USER_STATS = build_approve_requestchanges_statistics(PRS_IDS,WORKSPACE,REPO_SLUG,API_TOKEN)


# BULDING FINAL STATISTICS BY USER
PR_STATS_BY_USER_DATA = get_user_pr_stats(USER_DATA,PRS_DATA,PR_USER_STATS)


print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

print(PR_STATS_BY_USER_DATA)

print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")


