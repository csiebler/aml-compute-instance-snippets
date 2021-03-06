import os.path
import requests
import json
from azureml.core import Workspace
from azureml.core.compute import ComputeInstance
from datetime import datetime

idle_threshold_in_sec = 3600

# Jupyter runs on Compute Instance on http on port 8888
notebook_session_url = f'http://localhost:8888/api/sessions'

def get_compute_instance_name():
    instance = None
    ci_path = "/mnt/azmnt/.nbvm"
    if os.path.isfile(ci_path):
        with open(ci_path, 'r') as f:
            instance = dict(x.strip().split('=') for x in f)
    return instance['instance']

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

def was_notebook_recently_updated(notebook):
    last_activity = datetime.strptime(notebook['last_activity'],"%Y-%m-%dT%H:%M:%S.%fz")
    return (datetime.now() - last_activity).total_seconds() < idle_threshold_in_sec

def are_all_notebooks_idle(notebooks):
    for n in notebooks:
        print('Notebook:',  n['path'])
        print('Notebook state:',  n['state'])
        print('Notebook connections:',  n['num_connections'])
        print('Was notebook recently updated:', was_notebook_recently_updated(n))
        if (n['state'] != 'idle' or
            n['num_connections'] > 0 or
            was_notebook_recently_updated(n)):
            return False
    return True

def get_instance_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
    return uptime_seconds

notebooks = get_notebook_sessions()
ci_name = get_compute_instance_name()

if are_all_notebooks_idle(notebooks) and get_instance_uptime() > idle_threshold_in_sec:
    print(f'Compute Instance {ci_name} will be shut down!')
    # Connect to workspace and stop instance
    ws = Workspace.from_config()
    ct = ComputeInstance(ws, ci_name)
    ct.stop(wait_for_completion=False, show_output=False)
else:
    print(f'Compute Instance {ci_name} still has notebooks running or just started, will not shut it down')
    print("Details:")
    print(json.dumps(notebooks, indent=2))