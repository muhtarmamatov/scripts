import csv
import os

# Read ticket IDs from CSV file
with open('data/ticket_ids - ticket_ids.csv', 'r',encoding="utf8") as f:
    reader = csv.reader(f)
    next(reader)  # Skip the first row (header)
    ticket_ids = [row[0] for row in reader]

# Delete each ticket, along with its attachments and conversations
for ticket_id in ticket_ids:
    print(ticket_id)


API_KEY = os.environ.get('FRESHDESK_API_KEY')
API_ENDPOINT = os.environ.get('FRESHDESK_API_ENDPOINT')

print(API_KEY)
print(API_ENDPOINT)