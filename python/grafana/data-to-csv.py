import requests
import csv

# Set the API endpoint and API key
api_endpoint = 'http://192.168.1.128:3000/api/dashboards/uid/2F01Ef-4k'
api_key = 'eyJrIjoiTjNZRXNwWWhQQXhJRUhOTUcxSkJuSjd4TkQ1YXRQWDMiLCJuIjoiTmdpbngiLCJpZCI6MX0='

# Make the API request
response = requests.get(api_endpoint, headers={'Authorization': f'Bearer {api_key}'})
dashboard_data = response.json()['dashboard']

# Create a CSV file to write the panel data
with open('dashboard_panels.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)

    # Write the header row
    writer.writerow(['panel_id', 'panel_title', 'panel_type', 'panel_targets'])

    # Loop through each row in the grid and write the panel data to the CSV file
    for row in dashboard_data['panels']:
        panel_index = 0
        for panel in row:
            # Check if the element in the row is a dictionary
            if isinstance(panel, dict):
                # Extract the panel data
                panel_id = panel['id']
                panel_title = panel['title']
                panel_type = panel['type']
                panel_targets = panel['targets']

                # Only increment the panel_index if the panel type is "graph"
                if panel_type == 'graph':
                    panel_index += 1
                else:
                    panel_id = f'{panel_id}-not-a-graph'

                # Write the panel data to the CSV file
                writer.writerow([f'{panel_id}-{panel_index}', panel_title, panel_type, panel_targets])

print('Dashboard panel data written to dashboard_panels.csv')