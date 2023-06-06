#!/bin/bash

# Email configuration
#recipient="your_email@example.com"
#subject="Backup Status"

#SUCCESS_MESSAGE="MySQL full backup at the start of the month: Success"
#ERROR_MESSAGE="MySQL full backup at the start of the month: Failure"

# Set the API token and chat ID
API_TOKEN="< TELEGRAM_CHAT_BOT_API_TOKEN>"
CHAT_ID="< TELEGRAM_GROUP_CHAT_ID >"

BACKUP_PATH="< PATH_TO_BACKUP_FOLDER >"
# Function to send email and Telegram message
send_notification() {
    local message="$1"
    #echo "$message" | mail -s "$subject" "$recipient"
    curl -s -X POST "https://api.telegram.org/bot$API_TOKEN/sendMessage" -d "chat_id=$CHAT_ID" -d "text=$message"
}

# MySQL full backup at the start of the month
if [ "$(date +%d)" -eq 1 ]; then
     mysqldump -u <db_user> -p<PASSWORD>  --single-transaction --flush-logs <DATA_BASE_NAME> > $BACKUP_PATH/MYSQL-BACKUP/full_backup_$(date +%Y%m%d).sql
    if [ $? -eq 0 ]; then
        send_notification "MySQL full backup at the start of the month: Success"
        find $BACKUP_PATH/MYSQL-BACKUP -name "*_backup_$(date -d 'last month' +%Y%m)*.sql" -delete
        if [ $? -eq 0 ]; then
            send_notification "Success: Successfully deleted previuos month backups"
        else
            send_notification " Error: Failed to delete previous month backups please check errors"
        fi
    else
        send_notification "MySQL full backup at the start of the month: Failure"
    fi
fi

# Incremental MySQL backup at 11 p.m.
if [ "$(date +%d)" -ge 2 && "$(date +%H)" -eq 23 ]; then
    mysqldump -u <db_user> -p<PASSWORD>  --single-transaction --flush-logs <DATA_BASE_NAME> > $BACKUP_PATH/MYSQL-BACKUP/incremental_backup_$(date +%Y%m%d%H%M%S).sql
    if [ $? -eq 0 ]; then
        send_notification "Incremental MySQL backup at 11 p.m.: Success"
    else
        send_notification "Incremental MySQL backup at 11 p.m.: Failure"
    fi
fi

# File and image backup (using rsync)
rsync -avz  --no-o --no-g --no-perms <PATH_TO_BACKUP_FILES> $BACKUP_PATH/FILES-BACKUP
if [ $? -eq 0 ]; then
    send_notification "File and image backup: Success"
else
    send_notification "File and image backup: Failure"
fi
