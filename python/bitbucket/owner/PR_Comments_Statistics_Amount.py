import requests
import requests
import csv
import sys
import re
import time
import os
from collections import defaultdict


start_time = time.time()

# Get access token, username, and repo slug from Windows environment variables
api_token = os.environ.get('<ENVIROMENT_BITBUCKET_ACCESS_TOKEN>')
workspace = os.environ.get('<ENVIROMENT_BITBUCKET_WORKSPACE>')
repo_slug = os.environ.get('<ENVIROMENT_BITBUCKET_REPO_SLUG>')


#Bitbucket repository access information
api_token = "<BITBUCKET_API_ACCESS_TOKEN>"
workspace = "<BITBUCKET_WORKSPACE>"
repo_slug="<BITBUCKET_REPO_SLUG>"

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



# Method to get pull requests
def get_pull_requests(url, headers, date_since):
    params = {
        'state': 'OPEN,MERGED',
        'fields': 'values.id,values.author,values.state,values.updated_on,values.created_on,next,pagelen',
        'q': f'created_on>={date_since}'
    }

    pull_requests = []
    next_url = url

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
    



def find_comments_per_user(activity, users, pr_link):
    user_stats = defaultdict(lambda: {'link': "", 'display_name': "", 'comments_amount': 0, 'comments': ""})

    for entry in activity:
        is_comment_exist = entry.get("comment",{})
        if is_comment_exist:
            comment_user_display_name = entry.get("comment", {}).get("user", {}).get("display_name")
            if comment_user_display_name and comment_user_display_name in users:
                user_stats[comment_user_display_name]['link'] = pr_link  # Assign the PR link to the 'link' field
                user_stats[comment_user_display_name]['display_name'] = comment_user_display_name
                user_stats[comment_user_display_name]['comments_amount'] += 1
                comment_text = entry.get("comment", {}).get("content", {}).get("raw")
                if comment_text:
                    user_stats[comment_user_display_name]['comments'] += f"{user_stats[comment_user_display_name]['comments_amount']}. {comment_text}\n"

    return user_stats


def write_to_csv(user_stats,date):

    filename = f"{date}_pr_comments.csv"
    fieldnames = ['Link', 'Display Name', 'Comments Amount', 'Comments']

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for user, stats in user_stats.items():
            # Split the multiline comments into separate lines
            comments_lines = stats['comments'].strip().split('\n')
            # Write each comment on a separate row
            for i, comment in enumerate(comments_lines, start=1):
                writer.writerow({
                    'Link': stats['link'] if i == 1 else '',  # Write link only on the first row
                    'Display Name': stats['display_name'] if i == 1 else '',  # Write display name only on the first row
                    'Comments Amount': stats['comments_amount'] if i == 1 else '',  # Write comment amount only on the first row
                    'Comments': comment.strip()
                })

    print(f"Result written to {filename} file.")

DATE_SINCE = get_dates_from_user()

PRS_DATA = get_pull_requests(PULL_REQUEST_API_URL,HEADERS,DATE_SINCE)

PRS_IDS = get_pr_ids(PRS_DATA)

USERS = ["User", "User1", "User2", "User3", "User4"]

user_stats = defaultdict(lambda: {'link': "", 'display_name': "", 'comments_amount': 0, 'comments': ""})


for pr_id in PRS_IDS:
    pr_link = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}"
    activity, next_page = get_pr_activity(workspace, repo_slug, pr_id, api_token)

    print("Downloading PR ID:", pr_id)
    while activity:
        user_stats_update = find_comments_per_user(activity, USERS, pr_link)  # Pass the PR link
        for user, stats in user_stats_update.items():
            user_stats[user].update(stats)

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

write_to_csv(user_stats, DATE_SINCE)


end_time = time.time()

total_time = (end_time - start_time)/60

print("Time consumed to finish script is ", total_time)