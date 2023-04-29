import csv
import requests
import os

# Read API credentials from environment variables
API_KEY = os.environ.get('FRESHDESK_API_KEY')
API_ENDPOINT = os.environ.get('FRESHDESK_API_ENDPOINT')

# Read ticket IDs from CSV file
with open('data/ticket_ids - ticket_ids.csv', 'r',encoding="utf8") as f:
    reader = csv.reader(f)
    next(reader)  # Skip the first row (header)
    ticket_ids = [row[0] for row in reader]

# Delete each ticket, along with its attachments and conversations
for ticket_id in ticket_ids:
    # Delete attachments
    url = f"{API_ENDPOINT}tickets/{ticket_id}/attachments"
    response = requests.get(url, auth=(API_KEY, 'X'))
    if response.ok:
        for attachment in response.json():
            attachment_id = attachment['id']
            url = f"{API_ENDPOINT}attachments/{attachment_id}"
            response = requests.delete(url, auth=(API_KEY, 'X'))
            if not response.ok:
                print(f"Error deleting attachment {attachment_id}: {response.text}")

    # Delete conversations
    url = f"{API_ENDPOINT}tickets/{ticket_id}/conversations"
    response = requests.get(url, auth=(API_KEY, 'X'))
    if response.ok:
        for conversation in response.json():
            conversation_id = conversation['id']
            url = f"{API_ENDPOINT}conversations/{conversation_id}"
            response = requests.delete(url, auth=(API_KEY, 'X'))
            if not response.ok:
                print(f"Error deleting conversation {conversation_id}: {response.text}")

    # Delete ticket
    url = f"{API_ENDPOINT}tickets/{ticket_id}"
    response = requests.delete(url, auth=(API_KEY, 'X'))
    if response.ok:
        print(f"Ticket {ticket_id} deleted successfully")
    else:
        print(f"Error deleting ticket {ticket_id}: {response.text}")
