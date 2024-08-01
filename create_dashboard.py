import os
import json
from datadog import initialize, api
from git import Repo  # GitPython to handle Git operations

# Datadog API and application keys
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

# Read the state file to get already processed clients
state_file = 'state.json'
if os.path.exists(state_file):
    with open(state_file, 'r') as f:
        processed_clients = json.load(f)
else:
    processed_clients = []

# Create a dashboard for each new client
new_clients = [client for client in clients_info if client["client_name"] not in processed_clients]

for client_info in new_clients:
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
    
    # Update the state file with the new client
    processed_clients.append(client_name)

# Write the updated processed clients list back to the state file
with open(state_file, 'w') as f:
    json.dump(processed_clients, f)

# Commit changes to the Git repository
repo = Repo('.')
repo.index.add([state_file])
repo.index.commit('Update processed clients list')
origin = repo.remote(name='origin')

# Set up credentials for pushing
with repo.config_writer() as git_config:
    git_config.set_value('user', 'name', 'github-actions')
    git_config.set_value('user', 'email', 'github-actions@github.com')

origin.push()
