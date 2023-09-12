import subprocess

# List of script file paths to be executed
script_files = ['GIT_PULL_ALL_BRANCHES.py','GIT_COMMIT_STATISTICS.py','GIT_CHANGED_STATISTICS.py','USER_PR_COMMENTS_STATISTICS.py']

for script_file in script_files:
    print(f"+++++++++++++++++++++++++++++++++++++++++++ START OF RUNNING SCRIPT {script_file} ++++++++++++++++++++++++++++++++++++++")
    subprocess.run(['python', script_file])
    print(f"+++++++++++++++++++++++++++++++++++++++++++ END OF RUNNING SCRIPT {script_file} ++++++++++++++++++++++++++++++++++++++")
