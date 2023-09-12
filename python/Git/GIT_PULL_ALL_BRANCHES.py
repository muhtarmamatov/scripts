import subprocess
import re
import sys

# Class Exception for non-zero exit code 
class NotGitRepositoryError(Exception):
    pass

def is_git_installed():
    try:
        # Run the git command with the "--version" flag to check if Git is installed
        subprocess.run(['git', '--version'], capture_output=True, check=True)
        return True
    except FileNotFoundError:
        return False
    except subprocess.CalledProcessError:
        return False
    
# Reading script configuration form file 
def read_configuration_from_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    configuration = {}

    for line in lines:
        line = line.strip()
        if line:
            try:
                key, *value_parts = line.split('=')
                value = '='.join(value_parts)
                configuration[key.strip()] = value.strip()
            except ValueError:
                print(f"Skipping line: {line}. Invalid format.")

    return configuration


# Parse script configuration 
def configuration_format(configuration_file_path):
    CONFIGURATION = read_configuration_from_file(configuration_file_path)
    REPO_PATH = CONFIGURATION.get('REPO_PATH', '')
    BRANCHES = CONFIGURATION.get('BRANCHES', '')
    branches = [branch.strip().strip('[]"\'') for branch in BRANCHES.split(',')]    
    return REPO_PATH,branches

# Check if passed path is Git repository
def is_git_repository(repo_path):
    if is_git_installed():
        try:
            subprocess.check_output(['git', 'rev-parse'], cwd=repo_path)
            return True
        except subprocess.CalledProcessError:
            raise NotGitRepositoryError(f"================= Path '{repo_path}' is not a git repository. ==================")
    else:
        print("============================== Git is not installed in the system please install it. ====================================")
        sys.exit()
    

def git_track_all_remote_braches(repo_path):
    
    print("===================== Strt to tracking remote branches locally ============================")
    # Run the command and capture the output
    command = "git branch -r"
    output = subprocess.check_output(command, cwd=repo_path).decode()

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

# Pull changes form remote for specific branches
def git_pull(repo_path, branches):
    is_repository = is_git_repository(repo_path)
    if(is_repository):
        try:
            for branch in branches:
                print(f"Pulling changes for the branch: {branch}")
                subprocess.check_output(['git', 'checkout', '--quiet', branch], cwd=repo_path)
                subprocess.check_output(['git', 'pull'], cwd=repo_path)
            print("Git pull successful for specified branches")
        except subprocess.CalledProcessError as e:
            print(f'Git pull failed: {e}')


# FILE PATH TO READ DATABASE CONFIGURATION
CONFIGURATION_FILE_PATH = "./config/script_configuration.txt"

# SET UP DATABASE CONNECTION INFORMATION
REPO_PATH,BRACNHES = configuration_format(CONFIGURATION_FILE_PATH)


# TRACK ALL REMOTE BRANCHES LOCALLY
#git_track_all_remote_braches(REPO_PATH)

# PULL ALL CHANGES FROM REMOTE BEFORE BUILDING STATISTICS
git_pull(REPO_PATH,BRACNHES)




