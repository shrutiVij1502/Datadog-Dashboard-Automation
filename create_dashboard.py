import os
import json
import re
from datadog import initialize, api
from git import Repo, GitCommandError

# Initialize Datadog APIs
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

# Initialize the Git repository
try:
    repo = Repo('.')
except Exception as e:
    print(f"Error initializing Git repository: {e}")
    exit(1)

# Check if there are previous commits
commits = list(repo.iter_commits())
if len(commits) < 2:
    print("Not enough commits to determine differences.")
    exit(0)

# Get the diff of client-info.json from the previous commit
try:
    diff_output = repo.git.diff('HEAD~1', client_info_path)
except GitCommandError as e:
    print(f"Error getting git diff for {client_info_path}: {e}")
    exit(1)

# Parse the diff to find added client names
new_clients = []
diff_lines = diff_output.split('\n')
for line in diff_lines:
    if line.startswith('+') and not line.startswith('+++'):
        match = re.search(r'"client_name":\s*"([^"]+)"', line)
        if match:
            new_clients.append(match.group(1))

# Read current client configurations from client-info.json
try:
    with open(client_info_path, 'r') as f:
        current_clients_info = json.load(f)
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

# Create dashboards for each new client
for client_info in current_clients_info:
    client_name = client_info["client_name"]
    if client_name in new_clients:
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
