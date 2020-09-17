from azureml.core import Workspace
from azureml.core.compute import ComputeInstance, ComputeTarget

ws = Workspace.from_config()

targets_to_startup = []
compute_targets  = ws.compute_targets

for ct_name, ct in compute_targets.items():
    if (isinstance(ct, ComputeInstance) and ct.get_status().state == "Stopped"):
        targets_to_startup.append(ct)

print("Will start up the following Compute Instances:", targets_to_startup)

for ct in targets_to_startup:
    ct.start(wait_for_completion=False, show_output=False)