from azureml.core import Workspace
from azureml.core.compute import ComputeInstance, ComputeTarget

ws = Workspace.from_config()

targets_to_shutdown = []
compute_targets  = ws.compute_targets

for ct_name, ct in compute_targets.items():
    if (isinstance(ct, ComputeInstance) and ct.get_status().state == "Running"):
        targets_to_shutdown.append(ct)

print("Will shut down the following Compute Instances:", targets_to_shutdown)

for ct in targets_to_shutdown:
    ct.stop(wait_for_completion=False, show_output=False)