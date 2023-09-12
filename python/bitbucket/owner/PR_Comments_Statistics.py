import requests
import requests
import csv
import sys
import re
import time
import os
from collections import defaultdict


start_time = time.time()

#Bitbucket repository access information
api_token = "<BITBUCKET_API_ACCESS_TOKEN>"
workspace = "<BITBUCKET_WORKSPACE>"
repo_slug="<BITBUCKET_REPO_SLUG>"

# Get access token, username, and repo slug from Windows environment variables
api_token = os.environ.get('<ENVIROMENT_BITBUCKET_ACCESS_TOKEN>')
workspace = os.environ.get('<ENVIROMENT_BITBUCKET_WORKSPACE>')
repo_slug = os.environ.get('<ENVIROMENT_BITBUCKET_REPO_SLUG>')

BASE_URL = 'https://api.bitbucket.org/2.0'
PERMISSION_REPO_URL = f"{BASE_URL}/workspaces/{workspace}/permissions/repositories/{repo_slug}"
PULL_REQUEST_API_URL = f"{BASE_URL}/repositories/{workspace}/{repo_slug}/pullrequests"


HEADERS = {"Authorization": f"Bearer {api_token}", "Accept": "application/json"}

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

def get_pull_requests(url, headers, date_since):
    params = {
        'state': 'OPEN, MERGED',
        'fields': 'values.id,values.author.display_name,values.source.branch.name,values.destination.branch.name,'
                  'values.links.html.href,next',
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
            sys.exit()

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

def find_comments_per_user(activity, users, pr_link, pr_id, pr_author, source_branch, destination_branch):
    user_stats = defaultdict(lambda: {'reviewer_name': "", 'source_branch': "", 'destination_branch': "", 'comments': []})  # Modify the default factory to initialize 'comments' as a list

    for entry in activity:
        is_comment_exist = entry.get("comment", {})
        if is_comment_exist:
            comment_user_display_name = entry.get("comment", {}).get("user", {}).get("display_name")
            if comment_user_display_name and comment_user_display_name in users:
                user_stats[comment_user_display_name]['reviewer_name'] = comment_user_display_name
                comment_text = entry.get("comment", {}).get("content", {}).get("raw")
                if comment_text:
                    user_stats[comment_user_display_name]['comments'].append(comment_text)  # Append comment to the 'comments' list

    csv_data = []
    for reviewer_name, reviewer_stats in user_stats.items():
        comments_combined = '\n'.join([f"{i+1}. {comment}" for i, comment in enumerate(reviewer_stats['comments'])])  # Combine comments into a single string with numbering
        csv_data.append([pr_id, pr_author, source_branch, destination_branch, reviewer_name, comments_combined, pr_link])

    return csv_data


def write_to_csv(header, data, date):
    filename = f"{date}_pr_comments.csv"

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t')  # Enclose all fields in double quotes
        writer.writerow(header)
        writer.writerows(data)  # Write all rows at once

    print(f"Result written to {filename} file.")


DATE = get_dates_from_user()

PRS_DATA = get_pull_requests(PULL_REQUEST_API_URL,HEADERS,DATE)

PR_IDS = get_pr_ids(PRS_DATA)
USERS = ["Ilyas Masirov", "Таалай", "Ermek Mambetov", "Mirbek Imanbaev", "Arslan Dzhunushev", "Timur Bostanov"]

CSV_DATA = []
CSV_HEADERS = ["Pull Request ID", "Author", "Source Branch", "Destination Branch", "Reviewer Name",
               "Reviewer Comments","Pull Request HTML link"]
for pr in PRS_DATA:
   pr_id = pr['id']
   pr_author = pr['author']['display_name']
   pr_link = pr['links']['html']['href']
   source_branch = pr.get('source', {}).get('branch', {}).get('name', 'N/A')
   destination_branch = pr.get('destination', {}).get('branch', {}).get('name', 'N/A')

   activity, next_page = get_pr_activity(workspace, repo_slug, pr_id, api_token)

   print("Downloading PR ID:", pr_id)
   while activity:
        reviewer_comments = find_comments_per_user(activity,USERS, pr_link, pr_id, pr_author,source_branch,destination_branch)

        if next_page:
            response = requests.get(next_page, headers=HEADERS)
            if response.status_code == 200:
                data = response.json()
                activity = data.get('values', [])
                next_page = data.get('next')
            else:
                print(f"Failed to retrieve next page for PR {pr_id}: {response.status_code} - {response.text}")
                break
        else:
            break
   CSV_DATA.extend(reviewer_comments)

write_to_csv(CSV_HEADERS, CSV_DATA, DATE)

end_time = time.time()

total_time = (end_time - start_time)/60

print("Time consumed to finish script is ", total_time, "min")

    


    

