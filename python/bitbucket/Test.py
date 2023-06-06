import requests
import csv
import sys
import re
import os
from collections import defaultdict

#Bitbucket repository access information
api_token = "<BITBUCKET_API_ACCESS_TOKEN>"
workspace = "<BITBUCKET_WORKSPACE>"
repo_slug="<BITBUCKET_REPO_SLUG>"

# Get access token, username, and repo slug from Windows environment variables
api_token = os.environ.get('<ENVIROMENT_BITBUCKET_ACCESS_TOKEN>')
workspace = os.environ.get('<ENVIROMENT_BITBUCKET_WORKSPACE>')
repo_slug = os.environ.get('<ENVIROMENT_BITBUCKET_REPO_SLUG>')


base_url = 'https://api.bitbucket.org/2.0'
permission_repo_url = f"{base_url}/workspaces/{workspace}/permissions/repositories/{repo_slug}"
pull_request_api_url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests"

# Method to get repository users
def get_repository_users(url):
    users = []

    while url:
        response = requests.get(url, headers=headers)
        data = response.json()
        users.extend(data['values'])
        url = data.get('next')

    return users


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


# Method to get pull requests
def get_pull_requests(pull_request_api_url, headers):
    params = {
        'state': 'OPEN,MERGED',
        'fields': 'values.id,values.author,values.state,values.updated_on,values.created_on,next,pagelen',
        'q': f'created_on>={DATE_SINCE}'
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


# Bitbucket API connection
headers = {"Authorization": f"Bearer {api_token}", "Accept": "application/json"}

# Get user-entered date
DATE_SINCE = get_dates_from_user()

# Get repository users
users_data = get_repository_users(permission_repo_url)

# Get pull requests for the given date
pull_requests_data = get_pull_requests(pull_request_api_url, headers)

# Get PR IDs
pr_ids = get_pr_ids(pull_requests_data)

# Count PR approvals and changes requested for each user
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




# Get user PR stats
# user_pr_stats = get_user_pr_stats(users_data, pull_requests_data)
user_pr_stats = get_user_pr_stats(users_data, pull_requests_data, user_stats)


# Write user statistics to a CSV file
csv_file = 'user_stats.csv'
fieldnames = ['User', 'Total PR', 'Amount Of Approved PR', 'Amount Of Requested Changes']

with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    for stat in user_pr_stats:
        writer.writerow(stat)

print(f"User statistics have been written to {csv_file}.")
