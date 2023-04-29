import requests

# Set your Freshdesk domain and API key
subdomain = "<Subdomain>"
api_key = "<API_KEY>"

# Endpoint for getting tickets
url = f'https://{subdomain}.freshdesk.com/api/v2/tickets'

# Set query parameters to filter closed tickets
query_params = {
    'query': 'status:5',  # Status 5 represents "Closed" tickets
    'order_by': 'created_at',  # Optional: Order by created_at field
    'order_type': 'desc'  # Optional: Sort in descending order
}

# Make GET request with API key for authentication
response = requests.get(url, headers={'Content-Type': 'application/json'}, auth=(api_key, 'X'), params=query_params)

# Check response status code
if response.status_code == 200:
    # Tickets are in JSON format in the response body
    tickets = response.json()
    print(tickets)
else:
    print(f'Request failed with status code {response.status_code}.')
