import requests


subdomain = "<Subdomain>"
api_key = "<API_KEY>"


url = f"https://{subdomain}.freshdesk.com/api/v2/tickets?order_by=created_at"

headers = {"Content-Type": "application/json"}
auth = (api_key, "X")


# Send the API request and parse the response.
response = requests.get(url, headers=headers, auth=auth)
if response.status_code == 200:
    tickets = response.json()
    if len(tickets) > 0:
        first_ticket = tickets[0]
        print(f"The first created ticket is {first_ticket['id']}")
    else:
        print("No tickets found in Freshdesk")
else:
    print(f"Failed to retrieve tickets from Freshdesk: {response.text}")