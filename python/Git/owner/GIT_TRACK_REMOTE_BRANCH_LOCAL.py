import subprocess
import re

REPO_PATH = "D:\FinanceSoft\onlinebank"

# Run the command and capture the output
command = "git branch -r"
output = subprocess.check_output(command, cwd=REPO_PATH).decode()

# Process the output to extract remote branches
branches = output.strip().split("\n")
remote_branches = [branch.strip() for branch in branches if "->" not in branch]

# Create and track local branches
for remote_branch in remote_branches:
    local_branch = re.sub(r'\x1B\[[0-9;]*[a-zA-Z]', '', remote_branch)
    local_branch = local_branch.replace("origin/", "")
    
    # Check if the upstream branch exists
    upstream_exists = subprocess.call(f"git show-ref --verify --quiet refs/remotes/{remote_branch}", shell=True) == 0
    
    if upstream_exists:
        command = f"git branch --track {local_branch} {remote_branch}"
        subprocess.call(command, shell=True)
    else:
        print(f"Skipping branch '{remote_branch}' as the upstream branch does not exist.")

