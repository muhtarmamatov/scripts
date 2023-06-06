import requests
import csv
import sys
import re
import json
import os



#Bitbucket repository access information
api_token = "<BITBUCKET_API_ACCESS_TOKEN>"
workspace = "<BITBUCKET_WORKSPACE>"
repo_slug="<BITBUCKET_REPO_SLUG>"

# Get access token, username, and repo slug from Windows environment variables
api_token = os.environ.get('<ENVIROMENT_BITBUCKET_ACCESS_TOKEN>')
workspace = os.environ.get('<ENVIROMENT_BITBUCKET_WORKSPACE>')
repo_slug = os.environ.get('<ENVIROMENT_BITBUCKET_REPO_SLUG>')

# Bitbucket API ENDPOINTS
base_url = 'https://api.bitbucket.org/2.0'
permission_repo_url = f"{base_url}/workspaces/{workspace}/permissions/repositories/{repo_slug}"
#pull_request_api_url = f"{base_url}/repositories/{workspace}/{repo_slug}/pullrequests"
pull_request_api_url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests"

# Bitbucket API connection
headers = {"Authorization": f"Bearer {api_token}", "Accept": "application/json"}
 

# Global variables

start_date_entry = None
end_date_entry = None


def get_repository_users(url):
    users = []

    while url:
        response = requests.get(url,headers=headers)
        data = response.json()
        users.extend(data['values'])
        url = data.get('next')
    
    return users

def get_dates_from_user():

    while True:
        update_date = input("Enter the since date (YYYY-MM-DD): ")
    

        # Check if dates are in the correct format
        date_regex = r'^\d{4}-\d{2}-\d{2}$'
        if re.match(date_regex, update_date):
            return update_date
        else:
            print("Invalid date format. Please enter dates in the format YYYY-MM-DD.")


UPDATED_ON = get_dates_from_user()

def get_pull_requests(pull_request_api_url, headers):
    params = {
        'state': 'OPEN,MERGED',
        'fields': 'values.id,values.author,values.state,values.updated_on,values.created_on,next,pagelen',
        'q': f'created_on>={UPDATED_ON}'
    }

    pull_requests = []
    next_url = pull_request_api_url

    while next_url:
        response = requests.get(next_url, headers=headers, params=params)

        try:
            response.raise_for_status()  # Raise an exception for non-2xx response codes
            data = response.json()
        except (requests.HTTPError, json.JSONDecodeError) as e:
            print("Error retrieving pull requests:", str(e))
            sys.exit()

        pull_requests.extend(data.get("values", []))
        next_url = data.get("next")

        params.pop('state', None)
        params.pop('q', None)

    return pull_requests

users_data = get_repository_users(f'{permission_repo_url}?pagelen=100')

prs_data = get_pull_requests(pull_request_api_url,headers)

#print(prs_data)

filename = f'{UPDATED_ON}.csv'

with open(filename, 'w', newline='',encoding='utf-8') as file:

    writer = csv.writer(file)
    writer.writerow(['Name', 'Amount Of PR', 'Amount of Approved PR', 'Amount of Request Change'])

    for user in users_data:
        user_display_name = user['user']['display_name']
        user_account_id = user['user']['account_id']

        prs_by_user = [pr for pr in prs_data if pr["author"]["display_name"] == user_display_name]
        pr_count = len(prs_by_user)

        approved_pr_by_user = [pr for pr in prs_data if  pr["author"]["display_name"] == user_display_name and pr['state'] == 'MERGED']
        approved_pr_count = len(approved_pr_by_user)

        request_changes_by_user = [pr for pr in prs_data  if pr["author"]["display_name"] == user_display_name and pr['state'] == 'OPEN']
        request_changes_count = len(request_changes_by_user)

        writer.writerow([user_display_name, pr_count, approved_pr_count, request_changes_count])

print(f'CSV file "{filename}" created successfully.')















