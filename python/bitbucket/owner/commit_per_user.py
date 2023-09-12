import os
import requests
import json

# Get access token, username, and repo slug from Windows environment variables
access_token = os.environ.get('BITBUCKET_ACCESS_TOKEN')
username = os.environ.get('BITBUCKET_USERNAME')
repo_slug = os.environ.get('BITBUCKET_REPO_SLUG')

# Authentication
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}


url = ""
# API endpoint
if username == "" or username == None:
    url = f"https://api.bitbucket.org/2.0/repositories/{repo_slug}/commits"
else:
    url = f"https://api.bitbucket.org/2.0/repositories/{username}/{repo_slug}/commits"

print(url)

# Get start and end dates
start_date = input("Enter start date (YYYY-MM-DD): ")
end_date = input("Enter end date (YYYY-MM-DD): ")

# Get list of commits within date range
params = {"since": start_date, "until": end_date}
response = requests.get(url, headers=headers, params=params)
#commits = response.json()["values"]
print(response)
try:
    commits = response.json()["values"]
except json.decoder.JSONDecodeError as e:
    print(f"Error decoding JSON response: {e}")

# Aggregate commits by author
commit_counts = {}
for commit in commits:
    author = commit["author"]["user"]["nickname"]
    commit_counts[author] = commit_counts.get(author, 0) + 1

# Print results
print(f"Commit activity for {repo_slug} between {start_date} and {end_date}:")
for author, count in commit_counts.items():
    print(f"{author} made {count} commits")
