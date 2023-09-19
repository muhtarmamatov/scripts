import requests
import sys
import json
import os
import ast
from datetime import datetime, timedelta
import random
import logging


# Set the log directory and filename format
log_dir = "logs"
log_filename_format = "pull_request_lb_%Y-%m-%d.log"

# Create the log directory if it doesn't exist
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Configure the logger
logger = logging.getLogger("pull_request_lb")
logger.setLevel(logging.DEBUG)

# Create a formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Create a handler to write log messages to a file
log_file = os.path.join(log_dir, datetime.now().strftime(log_filename_format))
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


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
                logger.error(f"An error occured when reading script configuration {file_path} file")
    return configuration

# Format configuration 
def configuration_format(configuration_file_path):
    CONFIGURATION = read_configuration_from_file(configuration_file_path)

    API_TOKEN = CONFIGURATION.get('API_TOKEN', '')
    WORKSPACE = CONFIGURATION.get('WORKSPACE', '')
    REPO_SLUG = CONFIGURATION.get('REPO_SLUG', '')

    return API_TOKEN,WORKSPACE,REPO_SLUG

# Reading and formating passed arguments
def read_pr_arguments(args):
    if len(args) != 5:
        error_message = f"Expected 4 arguments: int, str, list, str. Passed arguments: {args}"
        logger.error(error_message)
        raise ValueError("Expected 4 arguments: int, str, list, str")
    
    pr_id = int(args[1])
    dest_branch = args[2]
    reviewers_str = args[3]
    pr_author = args[4]
    
    reviewers_list = ast.literal_eval(reviewers_str)
    
    if not isinstance(reviewers_list, list):
        error_message = "Reviewers argument should be a format of \"['Developer1', 'Developer2']\""
        logger.error(error_message)
        raise ValueError("Reviewers argument should be a format of \"['Developer1', 'Developer2']\"")
    
    return pr_id, dest_branch, reviewers_list, pr_author

# geting pull requests from bitbucket
def get_pull_requests(url, headers, state='OPEN'):
    
    params = {}
    counter = 0
    
    if state == 'MERGED':
        current_date = datetime.datetime.now()
        last_week_start = current_date - datetime.timedelta(days=current_date.weekday() + 7)
        date_from = last_week_start + datetime.timedelta(days=6)
        date_from_formatted = date_from.strftime('%Y-%m-%d')
        params = {
            'state': 'MERGED',
            'fields': 'values.reviewers,next',
            'q': f'created_on>={date_from_formatted}'
        }
    else:  
        params = {
            'state': 'OPEN',
            'fields': 'values.reviewers,next'
        }
        
    pull_requests = []
    
    while url:
        response = requests.get(url, headers=headers, params=params)
        
        counter += 1
        
        print(f"Downloading url: {url}")
        try:
            response.raise_for_status()

            data = response.json()
        except (requests.HTTPError, requests.exceptions.RequestException) as e:
            error_message = f"Error retrieving pull requests: {str(e)}"
            logger.error(error_message)
            print("Error retrieving pull requests:", str(e))
            sys.exit()

        pull_requests.extend(data.get("values", []))
        url = data.get("next")
        
        params.pop('state', None)
        params.pop('fields', None)
        params.pop('q', None)
    logger.info(f"Total number of pull requestes downloaded: {counter} ")
    return pull_requests

# merge pull request into one list
def merged_prs(prs_open_data, prs_merged_data):
    combined_prs = prs_open_data + prs_merged_data
    return combined_prs

# reading and formating user configuration file
def read_user_config_file(rules_file_path):
    try:
        if os.path.exists(rules_file_path):
            with open(rules_file_path, 'r', encoding="utf-8") as rules_file:
                data = json.load(rules_file)
            
            rules = data.get('Rules', {})
            day_offs = data.get('DayOffs', [])
            uuids = data.get('UUIDS', [])
            return rules, day_offs,uuids
        else:
            error_message = f"Configuration file not found in path {rules_file_path}"
            logger.error(error_message)
            raise FileNotFoundError(f"Configuration file not found in path {rules_file_path}")
    except json.JSONDecodeError as e:
        error_message = f"Error decoding JSON in file {rules_file_path}: {e}"
        logger.error(error_message)
        raise ValueError(f"Error decoding JSON in file {rules_file_path}: {e}")

# parsing specific rule for argument passed branch    
def get_rules_for_branch(branch, rules):
    branch_parts = branch.split('/')
    if len(branch_parts) > 1:
        branch_name = branch_parts[0]
        if branch_name in rules:
            return rules[branch_name]
    info_message = f"Argument passed branch name {branch} not exist in rules"
    logger.info(info_message)
    return None

# filter user if passed reviewers are not in dayoffs
def filter_users_not_on_dayoffs(rule, dayoffs):
    # Extract the SeniorReviewers and NonSeniorReviewers from the rules
    senior_reviewers = rule.get("SeniorReviewers", [])
    non_senior_reviewers = rule.get("NonSeniorReviewers", [])
    
    # Filter out users who are not in the day-offs list from both Senior and Non-Senior Reviewers
    senior_reviewers_filtered = [user for user in senior_reviewers if user not in dayoffs]
    non_senior_reviewers_filtered = [user for user in non_senior_reviewers if user not in dayoffs]
    return {
        "SeniorReviewers": senior_reviewers_filtered,
        "NonSeniorReviewers": non_senior_reviewers_filtered
    }

# calculate assigned pull requests per user    
def calculate_reviewers_per_pr(prs_data, senior_users, nonsenior_users):
    senior_reviewer_counts = {user: 0 for user in senior_users}
    nonsenior_reviewer_counts = {user: 0 for user in nonsenior_users}
    if prs_data:
        for pr in prs_data:
            reviewers = [reviewer["display_name"] for reviewer in pr["reviewers"]]
            
            for reviewer in reviewers:
                if reviewer in senior_users:
                    senior_reviewer_counts[reviewer] += 1
                elif reviewer in nonsenior_users:
                    nonsenior_reviewer_counts[reviewer] += 1

    return {
            "SeniorReviewerCounts": senior_reviewer_counts,
            "NonSeniorReviewerCounts": nonsenior_reviewer_counts
    }
        
# find who has minimum pull requests
def users_with_min_pr(senior_users, non_senior_users, min_senior_users, min_reviewers):
    # Sort senior users by PR count in ascending order
    sorted_senior_users = sorted(senior_users.items(), key=lambda x: x[1])

    # Sort non-senior users by PR count in ascending order
    sorted_non_senior_users = sorted(non_senior_users.items(), key=lambda x: x[1])

    selected_senior_users = []
    selected_non_senior_users = []

    # Select at least min_senior_users senior reviewers
    for user, pr_count in sorted_senior_users[:min_senior_users]:
        selected_senior_users.append((user, pr_count))

    # Calculate the number of remaining reviewers needed to reach min_reviewers
    remaining_reviewers = max(min_reviewers - len(selected_senior_users), 0)

    # Select the remaining reviewers from non-senior users
    for user, pr_count in sorted_non_senior_users[:remaining_reviewers]:
        selected_non_senior_users.append((user, pr_count))

    # Shuffle the selected users while maintaining the order of users with the same PR count
    random.shuffle(selected_senior_users)
    random.shuffle(selected_non_senior_users)

    # Combine the selected senior and non-senior users
    result_users = selected_senior_users + selected_non_senior_users

    info_message = f"Following users have minimum number of pull requests assigned: {result_users}"
    logger.info(info_message)
    return dict(result_users)

# return list of bitbucket user uuids per reviewers 
def get_uuids_by_keys(uuids_map, reviewers):
    uuid_list = [uuids_map.get(reviewer) for reviewer in reviewers]
    return uuid_list

# check if passed pull request exist
def check_if_pr_exists(pr_id, pr_api_url, api_token):
    url = f"{pr_api_url}/{pr_id}"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}"
    }
    
    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return True  # PR exists
        elif response.status_code == 404:
            error_message = f"Pull request with ID {pr_id} could not be found!!!"
            logger.error(error_message)
            return False  # PR does not exist
        else:
            print("Error checking PR existence:", response.status_code, response.text)
            error_message = f"Bitbucket API internal error wilth follwing status {response.status_code} and following error message {response.text} "
            logger.error(error_message)
            return False
    except requests.exceptions.RequestException as e:
        error_message = f"Script  or Bitbucket API internal error {str(e)}"
        logger.error(error_message)
        print("An error occurred while checking PR existence:", e)
        return False

# load balance reviewers per pull request
def update_pr_user_reviewers(pr_id, reviewers_uuid, pr_api_url, api_token):

    url = f"{pr_api_url}/{pr_id}"

    reviewers_list = [{"uuid": uuid} for uuid in reviewers_uuid]
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}"
    }
    payloads = json.dumps({
        "reviewers": reviewers_list
    })

    try:
        response = requests.put(url, data=payloads, headers=headers)

        if response.status_code == 200:
            print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
            print("+++++++++++++++ Successfully added reviewers ++++++++++++++++")
        else:
            print("----------------------- Failed to update reviewers ----------------", response.status_code, response.text)
    except requests.exceptions.RequestException as e:
        print("An error occurred while making the request: ", e)
        
if __name__ == "__main__":
    
    if len(sys.argv) != 5:
        print("Script requires command line arguments!!")
        print("Usage: python script.py <pr_id> <dest_branch> <reviewers> <pr_author>")
        error_message = "Script requires command line arguments!! \n Usage: python script.py <pr_id> <dest_branch> <reviewers> <pr_author>"
        logger.error(error_message)
        sys.exit(1)
        
    PR_ID, DEST_BRANCH, REVIEWERS_STR, PR_AUTHOR = read_pr_arguments(sys.argv)
      
    if REVIEWERS_STR:
        print("Reviewers alreday set to Pull Request. Exiting....")
        info_message = f"PR with ID {PR_ID} already set following reviewers: {REVIEWERS_STR} \n Compliting script compilation"
        logger.info(info_message)
        sys.exit(1)
    else:
        # FILE PATH TO READ SCRIPT CONFIGURATION
        CONFIGURATION_FILE_PATH = "./config/script_configuration.txt"

        #SET UP DATABASE CONNECTION INFORMATION
        API_TOKEN,WORKSPACE,REPO_SLUG = configuration_format(CONFIGURATION_FILE_PATH)
              
        # GLOBAL VARIABLES 
        BASE_URL = 'https://api.bitbucket.org/2.0'
        PULL_REQUEST_API_URL = f"{BASE_URL}/repositories/{WORKSPACE}/{REPO_SLUG}/pullrequests"
          
        if not check_if_pr_exists(PR_ID, PULL_REQUEST_API_URL, API_TOKEN):
            print(f"PR with {PR_ID} does not exist, cannot update reviewers.")
            sys.exit(1)
        
        
        # BITBUCKET API CONNECTION
        HEADERS = {"Authorization": f"Bearer {API_TOKEN}", "Accept": "application/json"}
        
        # READING USER CONFIGURATION FILE
        RULES, DAYOFFS, UUIDS = read_user_config_file("./config/user_config.json" )
        
        # RETURN REQUIRED RULE DEPENED ON DESTINATION BRANCH 
        RULE = get_rules_for_branch(DEST_BRANCH, RULES)
        
        # PULL OPEN STATE PULL REQUEST FROM BITBUCKET
        PRS_OPEN_DATA = get_pull_requests(PULL_REQUEST_API_URL, HEADERS)
        
        # PULL MERGED STATE PULL REQUEST FROM BITBUCKET FOR THE LAST WEEK
        PRS_MERGED_DATA = get_pull_requests(PULL_REQUEST_API_URL, HEADERS, 'MERGED')
        
        # MERGE OPEN AND MERGED PULL REQUESTS INTO ONE PULL REQUEST DATA
        PRS_DATA = merged_prs(PRS_OPEN_DATA, PRS_MERGED_DATA)
        
        # FILTER REVIEWERS IF ON DAYOFFS        
        REVIEWERS = filter_users_not_on_dayoffs(RULE, DAYOFFS)
        SENIOR_REVIEWERS = REVIEWERS['SeniorReviewers']
        NONSENIOR_REVIEWERS = REVIEWERS['NonSeniorReviewers']
        
        # CALCULATE PULL REQUEST PER PASSED REVIEWERS
        PR_PER_REVIEWERS = calculate_reviewers_per_pr(PRS_DATA, SENIOR_REVIEWERS, NONSENIOR_REVIEWERS)
        
        # GET LIST OF REVIWERS WHO HAS LEAST PR ASSIGNED DEPENDING USER CONFIGURATION FILE
        SENIOR_REVIEWERS = PR_PER_REVIEWERS['SeniorReviewerCounts']
        NONSENIOR_REVIEWERS = PR_PER_REVIEWERS['NonSeniorReviewerCounts']
        MIN_SENIOR_USER = RULE.get('MinimumSeniorReviewers')
        MIN_REVIEWERS = RULE.get('MinimumReviewers')
        PR_REVIEWERS = users_with_min_pr(SENIOR_REVIEWERS, NONSENIOR_REVIEWERS,MIN_SENIOR_USER,MIN_REVIEWERS)
        
        # GET REVIWERS BITBUCKET UUIDS 
        REVIEWER_UUIDS = get_uuids_by_keys(UUIDS, PR_REVIEWERS)
        
        # LOAD BALANCE REVIEWERS FOR SPECIFIC PR
        update_pr_user_reviewers(PR_ID, REVIEWER_UUIDS, PULL_REQUEST_API_URL, API_TOKEN)
        info_message = f"PR with ID {PR_ID} successfully updated and set following reviewers: {PR_PER_REVIEWERS}"
        print("SCRIPT SUCCESSFULLY COMPLTED")
        
    
        
        
        
        
        
        