import requests

# Set the API endpoint and API key
api_endpoint = 'http://192.168.1.128:3000/api/search?type=dash-db&query=&starred=false'
api_key = 'eyJrIjoiTjNZRXNwWWhQQXhJRUhOTUcxSkJuSjd4TkQ1YXRQWDMiLCJuIjoiTmdpbngiLCJpZCI6MX0='


# Make the API request
response = requests.get(api_endpoint, headers={'Authorization': f'Bearer {api_key}'})

# Extract the dashboard UIDs from the response JSON
dashboards = [result for result in response.json() if result['type'] == 'dash-db']
dashboard_uids = [dashboard['uid'] for dashboard in dashboards]

# Print the list of dashboard UIDs
print(dashboard_uids)