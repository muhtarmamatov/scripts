import tkinter as tk
import requests
import os



# Get access token, username, and repo slug from Windows environment variables
api_token = os.environ.get('<ENVIROMENT_BITBUCKET_ACCESS_TOKEN>')
workspace = os.environ.get('<ENVIROMENT_BITBUCKET_WORKSPACE>')
repo_slug = os.environ.get('<ENVIROMENT_BITBUCKET_REPO_SLUG>')


#Bitbucket repository access information
api_token = "<BITBUCKET_API_ACCESS_TOKEN>"
workspace = "<BITBUCKET_WORKSPACE>"
repo_slug="<BITBUCKET_REPO_SLUG>"

start_date_entry = None
end_date_entry = None
username_entry = None

def get_pr_count():
    global start_date_entry, end_date_entry, username_entry
    
    start_date = start_date_entry.get()
    end_date = end_date_entry.get()
    target_user = username_entry.get()

    url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests"
    headers = {"Authorization": f"Bearer {api_token}", "Accept": "application/json"}
    params = {"created_on_start": start_date + "T00:00:00Z", "created_on_end": end_date + "T23:59:59Z"}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        prs = response.json()["values"]
        prs_by_user = [pr for pr in prs if pr["author"]["display_name"] == target_user]
        pr_count = len(prs_by_user)
        if pr_count > 0:
            result_text = f"TOTAL AMOUNT OF PRs by {target_user} is: {pr_count}"
            display_result_window(result_text)
        else:
            result_text = f"User {target_user} has not made any PR"
            display_result_window(result_text)
    else:
        text = "Error: Unable to fetch PR count."
        display_result_window(text)

def open_get_pr_count():
    global start_date_entry, end_date_entry, username_entry,pr_count_window
    
    window.withdraw()  # Hide the main window
    pr_count_window = tk.Toplevel()
    pr_count_window.title("Get User's PR Count")
    pr_count_window.geometry("500x200")

    start_date_label = tk.Label(pr_count_window, text="Start Date (YYYY-MM-DD):")
    start_date_label.pack()
    start_date_entry = tk.Entry(pr_count_window)
    start_date_entry.insert(0, "YYYY-MM-DD")
    start_date_entry.pack()

    end_date_label = tk.Label(pr_count_window, text="End Date (YYYY-MM-DD):")
    end_date_label.pack()
    end_date_entry = tk.Entry(pr_count_window)
    end_date_entry.insert(0, "YYYY-MM-DD")
    end_date_entry.pack()

    username_label = tk.Label(pr_count_window, text="Username:")
    username_label.pack()
    username_entry = tk.Entry(pr_count_window)
    username_entry.pack()

    submit_button = tk.Button(pr_count_window, text="Submit", command=get_pr_count)
    submit_button.pack()

    pr_count_window.protocol("WM_DELETE_WINDOW", show_main_window)  # Show main window on close

def show_main_window():
    global pr_count_window
    window.deiconify()  # Show the main window
    pr_count_window.destroy()  # Close the PR count window

def display_result_window(result_text):
    result_window = tk.Toplevel()
    result_window.title("Result")
    
    result_label = tk.Label(result_window, text=result_text)
    result_label.pack()
    
    ok_button = tk.Button(result_window, text="OK", command=result_window.destroy)
    ok_button.pack()

# Create the main window
window = tk.Tk()
window.title("PR Tool")
window.geometry("500x200")

# Calculate the vertical and horizontal padding
vertical_padding = 20
horizontal_padding = 50

get_user_pr_button = tk.Button(window, text="Amount of User's PRs", command=open_get_pr_count)
get_user_pr_button.pack(pady=vertical_padding)
get_user_pr_button.place(relx=0.5, rely=0.5, anchor='center')

get_user_pr_state = tk.Button(window, text="Amount of PRs State")
get_user_pr_state.pack(pady=vertical_padding)

window.mainloop()
