import subprocess
from datetime import datetime, timedelta






def is_git_repository(directory):

    try:
        subprocess.check_output(['git', 'rev-parse'], cwd=directory)
        return True
    except subprocess.CalledProcessError:
        return False

def git_pull(directory, branches):
    try:
        for branch in branches:
            print(f"Pulling changes for the branch: {branch}")
            subprocess.check_output(['git', 'checkout', '--quiet', branch], cwd=directory)
            subprocess.check_output(['git', 'pull'], cwd=directory)
        print("Git pull successful for specified branches")
    except subprocess.CalledProcessError as e:
        print(f'Git pull failed: {e}')


def commit_statistics(repo_path):
    weeks_ago = 1  # Number of weeks ago to retrieve commits
    start_date = datetime.now() - timedelta(weeks=weeks_ago)
    formatted_date = start_date.strftime('%Y-%m-%d %H:%M:%S')
    git_cmd = f'git -C "{repo_path}" log --all --after="{formatted_date}" --pretty=format:"%H|%an|%d|%ci|%s"'
    output = subprocess.check_output(git_cmd, shell=True).decode().strip().split('\n')

    return output

def statistics_write_to_DB(output,connection):
    for line in output:
        commit_id, ldap_user, branch, commit_date, comment = line.split('|')

        # Clean up branch name
        branch = branch.replace('(origin/', '').replace(')', '').strip()
        # branch = branch.replace('(HEAD ->', '').replace('(', '').split(',')[0].strip()

        # Convert commit date to datetime object
        commit_date = datetime.strptime(commit_date, '%Y-%m-%d %H:%M:%S %z')

        print(f"Author: {ldap_user}, Commit ID: {commit_id}, Branch: {branch}, Commit Date: {commit_date}, Comments: {comment}\n")
        # connection.execute("""
        #     INSERT INTO commit_table (commit_id, ldap_user, branch, commit_date, comment)
        #     VALUES (%s, %s, %s, %s, %s)
        # """, (commit_id, ldap_user, branch, commit_date, comment))



REPO_PATH = "E:\Muktarbek\FinanceSoft\onlinebank"
BRANCHES = ["KSB/Develop","KSB/Release","KG/UnitedDevelop"]



if is_git_repository(REPO_PATH):
    git_pull(REPO_PATH,BRANCHES)

    OUTPUT = commit_statistics(REPO_PATH)

    statistics_write_to_DB(OUTPUT, "")
else:
    print(f"Path {REPO_PATH} is not a Git repository. Please pass correct repository path...............")



