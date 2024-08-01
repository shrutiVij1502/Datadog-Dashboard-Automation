# from datadog import initialize, api
# import json

# # Datadog API and application keys
# options = {
#     'api_key': 'YOUR_API_KEY',
#     'app_key': 'YOUR_APP_KEY'
# }

# initialize(**options)

# # Read client configurations from client-info.json
# with open('client-info.json', 'r') as f:
#     clients_info = json.load(f)

# # Read the base dashboard configuration from dashboard.json
# with open('dashboard.json', 'r') as f:
#     base_dashboard_config = json.load(f)

# # Create a dashboard for each client
# for client_info in clients_info:
#     client_name = client_info["client_name"]
#     # Customize the dashboard title or other parameters based on the client
#     dashboard_config = base_dashboard_config.copy()
#     dashboard_config['title'] = client_name
    
#     response = api.Dashboard.create(**dashboard_config)
#     print(f"Dashboard created for {client_name}: {response}")

import os
import json
import hashlib
from datadog import initialize, api

options = {
    'api_key': os.getenv('DATADOG_API_KEY'),
    'app_key': os.getenv('DATADOG_APP_KEY'),
    'api_host': 'https://api.us5.datadoghq.com'
}

initialize(**options)

# Read client configurations from client-info.json
with open('client-info.json', 'r') as f:
    clients_info = json.load(f)

# Read the base dashboard configuration from dashboard.json
with open('dashboard.json', 'r') as f:
    base_dashboard_config = json.load(f)

# Create a dashboard for each client
for client_info in clients_info:
    client_name = client_info["client_name"]
    
    # Convert the base dashboard config to a string
    dashboard_config_str = json.dumps(base_dashboard_config)
    
    # Replace the placeholder with the actual client name
    dashboard_config_str = dashboard_config_str.replace("{{client_name}}", client_name)
    
    # Convert the string back to a dictionary
    dashboard_config = json.loads(dashboard_config_str)
    
    # Create the dashboard
    response = api.Dashboard.create(**dashboard_config)
    print(f"Dashboard created for {client_name}: {response}")
