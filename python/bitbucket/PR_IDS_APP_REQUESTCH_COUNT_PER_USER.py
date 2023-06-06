import requests
from collections import defaultdict
import os

def get_pr_activity(workspace, repo_slug, pr_id, access_token):
    url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}/activity"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data.get('values', [])
    else:
        print(f"Failed to retrieve activity for PR {pr_id}: {response.status_code} - {response.text}")
        return []

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


#Bitbucket repository access information
api_token = "<BITBUCKET_API_ACCESS_TOKEN>"
workspace = "<BITBUCKET_WORKSPACE>"
repo_slug="<BITBUCKET_REPO_SLUG>"

# Get access token, username, and repo slug from Windows environment variables
api_token = os.environ.get('<ENVIROMENT_BITBUCKET_ACCESS_TOKEN>')
workspace = os.environ.get('<ENVIROMENT_BITBUCKET_WORKSPACE>')
repo_slug = os.environ.get('<ENVIROMENT_BITBUCKET_REPO_SLUG>')

# List of PR IDs
pr_ids = ['7910']

# Count PR approval and changes for each user
user_stats = defaultdict(lambda: {'approved': 0, 'changes_requested': 0})

for pr_id in pr_ids:
    activity = get_pr_activity(workspace, repo_slug, pr_id, api_token)
    pr_stats = count_approved_and_changes(activity)
    

    for user, stats in pr_stats.items():
        user_stats[user]['approved'] += stats['approved']
        user_stats[user]['changes_requested'] += stats['changes_requested']



# Print the user statistics
for user, stats in user_stats.items():
    print(f"User: {user}")
    print(f"Approved PRs: {stats['approved']}")
    print(f"PRs with Requested Changes: {stats['changes_requested']}")
    print()
