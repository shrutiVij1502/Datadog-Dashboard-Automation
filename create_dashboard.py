import os
import json
from datadog import initialize, api
from git import Repo, GitCommandError

# Datadog API and application keys
options = {
    'api_key': os.getenv('DATADOG_API_KEY'),
    'app_key': os.getenv('DATADOG_APP_KEY'),
    'api_host': 'https://api.us5.datadoghq.com'
}

# Initialize Datadog
initialize(**options)

# File paths
client_info_path = 'client-info.json'
dashboard_path = 'dashboard.json'
state_file_path = 'state.json'

# Read client configurations from client-info.json
try:
    with open(client_info_path, 'r') as f:
        clients_info = json.load(f)
except Exception as e:
    print(f"Error reading {client_info_path}: {e}")
    exit(1)

# Read the base dashboard configuration from dashboard.json
try:
    with open(dashboard_path, 'r') as f:
        base_dashboard_config = json.load(f)
except Exception as e:
    print(f"Error reading {dashboard_path}: {e}")
    exit(1)

# Read the state file to get already processed clients
if os.path.exists(state_file_path):
    try:
        with open(state_file_path, 'r') as f:
            processed_clients = json.load(f)
        # Ensure processed_clients is a list
        if not isinstance(processed_clients, list):
            raise ValueError("State file does not contain a list.")
    except Exception as e:
        print(f"Error reading {state_file_path}: {e}")
        processed_clients = []
else:
    processed_clients = []

# Create dashboards for each new client
new_clients = [client for client in clients_info if client["client_name"] not in processed_clients]

for client_info in new_clients:
    client_name = client_info["client_name"]
    
    # Convert the base dashboard config to a string
    dashboard_config_str = json.dumps(base_dashboard_config)
    
    # Replace the placeholder with the actual client name
    dashboard_config_str = dashboard_config_str.replace("{{client_name}}", client_name)
    
    # Convert the string back to a dictionary
    dashboard_config = json.loads(dashboard_config_str)
    
    try:
        # Create the dashboard
        response = api.Dashboard.create(**dashboard_config)
        print(f"Dashboard created for {client_name}: {response}")
    except Exception as e:
        print(f"Error creating dashboard for {client_name}: {e}")
        continue
    
    # Update the state file with the new client
    processed_clients.append(client_name)

# Write the updated processed clients list back to the state file
try:
    with open(state_file_path, 'w') as f:
        json.dump(processed_clients, f)
except Exception as e:
    print(f"Error writing to {state_file_path}: {e}")
    exit(1)

# Commit changes to the Git repository
try:
    repo = Repo('.')
    repo.index.add([state_file_path])
    repo.index.commit('Update processed clients list')
    origin = repo.remote(name='origin')

    # Set up credentials for pushing
    with repo.config_writer() as git_config:
        git_config.set_value('user', 'name', 'github-actions')
        git_config.set_value('user', 'email', 'github-actions@github.com')

    origin.push()
except GitCommandError as e:
    print(f"Git command error: {e}")
    exit(1)
except Exception as e:
    print(f"General error: {e}")
    exit(1)
