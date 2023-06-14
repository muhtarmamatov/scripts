import requests
import json


glpi_url = "<GLPI_URL>"

api_token = "<GLPI_USER_API_TOKEN>"

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'user_token {api_token}'
}

# API endpoint for getting users
api_endpoint = '/user'

# Make the API request
response = requests.get(f'{glpi_url}{api_endpoint}', headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    if 'data' in data:
        # Extract the list of users
        users = data['data']

        # Print user details
        for user in users:
            print(f"User ID: {user['id']}")
            print(f"Name: {user['name']}")
            print(f"Email: {user['email']}")
            print('---')
    else:
        print('No user data found.')
else:
    print(f"Error: {response.status_code} - {response.text}")