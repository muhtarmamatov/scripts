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


def file_changes_statistics(repo_path):
    weeks_ago = 1  # Number of weeks ago to retrieve commits
    start_date = datetime.now() - timedelta(weeks=weeks_ago)
    formatted_date = start_date.strftime('%Y-%m-%d %H:%M:%S')

    # Get the commit information using git log command
    git_log_command = f'git -C "{repo_path}" log --all --after="{formatted_date}" --stat --pretty=format:"%H" --name-status'
    git_log_output = subprocess.check_output(git_log_command, shell=True, universal_newlines=True)

    # Split the output by commit
    commits = git_log_output.strip().split("\ncommit ")

    return commits


def extract_statistics(commit):
    commit_lines = commit.strip().split("\n")
    commit_hash = commit_lines[0]
    file_changes = commit_lines[1:]

    # Initialize counters
    added_lines = 0
    changed_lines = 0
    removed_lines = 0

    # Extract file path and change statistics
    for line in file_changes:
        parts = line.split("\t")

        # Skip lines that don't represent file changes
        if len(parts) != 3:
            continue

        file_status, file_path, stat_info = parts

        # Extract the number of added, changed, and removed lines
        stats = stat_info.split(", ")
        added_lines += int(stats[0].split()[0])
        changed_lines += int(stats[1].split()[0])
        removed_lines += int(stats[2].split()[0])

    return commit_hash, added_lines, changed_lines, removed_lines


def statistics_write_to_console(commits):
    for commit in commits:
        commit_hash, added_lines, changed_lines, removed_lines = extract_statistics(commit)
        print("Commit:", commit_hash)
        print("Added lines:", added_lines)
        print("Changed lines:", changed_lines)
        print("Removed lines:", removed_lines)
        print("---")


REPO_PATH = "<FULL_REPOSITORY_PATH"
BRANCHES = ["<LIST_OF_BRANCHES>"]

# git_pull(REPO_PATH,BRANCHES)

commits = file_changes_statistics(REPO_PATH)
statistics_write_to_console(commits)