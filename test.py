import os
import json
import hashlib
from datadog import initialize, api

# Initialize Datadog API
options = {
    'api_key': os.getenv('DATADOG_API_KEY'),
    'app_key': os.getenv('DATADOG_APP_KEY'),
    'api_host': 'https://api.us5.datadoghq.com'
}

initialize(**options)

# Function to compute the checksum of a file
def compute_checksum(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

# Load client data
def load_client_data():
    with open('client-info.json', 'r') as file:
        return json.load(file)

# Load dashboard template
def load_dashboard_template():
    with open('dashboard_template.json', 'r') as file:
        return json.load(file)

# Create or update dashboard
def create_or_update_dashboard(client_data, dashboard_data):
    response = api.Dashboard.create(**dashboard_data)
    print(f"Dashboard created for {client_data['client_name']}: {response}")
    return response

# Render dashboard template with client data
def render_dashboard_template(client_data, template):
    dashboard = json.loads(json.dumps(template))  # Deep copy the template
    dashboard['title'] = dashboard['title'].format(**client_data)
    for widget in dashboard['widgets']:
        for request in widget['definition'].get('requests', []):
            request['q'] = request['q'].format(**client_data)
    return dashboard

# Load previous state from file
state_file = 'state.json'
if os.path.exists(state_file):
    with open(state_file, 'r') as file:
        previous_state = json.load(file)
else:
    previous_state = {}

# Load the dashboard template
dashboard_template = load_dashboard_template()

# Load and process all clients from client-info.json
client_data_list = load_client_data()
current_state = {}

for client_data in client_data_list:
    client_name = client_data['client_name']
    client_json_path = 'client-info.json'
    
    checksum = compute_checksum(client_json_path)
    current_state[client_name] = checksum

    if previous_state.get(client_name) != checksum:
        print(f'Processing dashboard for {client_name}')
        dashboard_data = render_dashboard_template(client_data, dashboard_template)
        response = create_or_update_dashboard(client_data, dashboard_data)
        current_state[client_name] = response['id']
    else:
        print(f'Skipping {client_name}, no changes detected.')

# Save current state to file
with open(state_file, 'w') as file:
    json.dump(current_state, file)
