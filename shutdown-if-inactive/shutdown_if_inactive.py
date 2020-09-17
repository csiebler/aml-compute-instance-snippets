import os.path
import requests
import json
from azureml.core import Workspace
from azureml.core.compute import ComputeInstance
from datetime import datetime

idle_threshold_in_sec = 3600

# Jupyter runs on Compute Instance on http on port 8888
notebook_session_url = f'http://localhost:8888/api/sessions'

def get_compute_instance_details():
    instance = None
    ci_path = "/mnt/azmnt/.nbvm"
    if os.path.isfile(ci_path):
        with open(ci_path, 'r') as f:
            instance = dict(x.strip().split('=') for x in f)
    return instance

def get_notebook_sessions():
    response = requests.get(notebook_session_url)
    response = response.json()  
    notebooks = []
    for nb in response:
        path = nb['path']
        state = nb['kernel']['execution_state']
        num_connections = nb['kernel']['connections']
        last_activity = nb['kernel']['last_activity']
        notebooks.append({
            "path": path,
            "state": state,
            "num_connections": num_connections,
            "last_activity": last_activity
        })
    return notebooks

def is_notebook_busy(notebook):
    last_activity = datetime.strptime(notebook['last_activity'],"%Y-%m-%dT%H:%M:%S.%fz")
    return (datetime.now() - last_activity).total_seconds() < idle_threshold_in_sec

def is_instance_idle(notebooks):
    for n in notebooks:
        if (n['state'] != 'idle' or
            n['num_connections'] > 0 or
            is_notebook_busy(n)):
            return False
    return True

compute_instance = get_compute_instance_details()
ci_name = compute_instance['instance']

notebooks = get_notebook_sessions()

print(compute_instance)
print(json.dumps(notebooks, indent=2))

if is_instance_idle(notebooks):
    print(f'Compute Instance {ci_name} will be shut down!')
    ws = Workspace.from_config()
    ct = ComputeInstance(ws, ci_name)
    ct.stop(wait_for_completion=False, show_output=False)
else:
    print(f'Compute Instance {ci_name} still has notebooks running, will not shut it down')