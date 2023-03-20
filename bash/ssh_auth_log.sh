#!/bin/bash

# Set the log file location
LOG_FILE="/var/log/auth.log"

# Get the current date and time
DATE=$(date +"%Y-%m-%d %H:%M:%S")

# Use grep to filter out failed authentication attempts
FAILED_AUTH=$(grep "Failed password for" $LOG_FILE)

# Check if there are any failed attempts
if [ -z "$FAILED_AUTH" ]; then
  echo -e "\033[32;5m$DATE:==> No failed SSH authentication attempts. <==\033[0m"
else
  echo -e "\033[31;5m$DATE:==> Failed SSH authentication attempts: <==\033[0m"
  echo -e "\033[31m$FAILED_AUTH\033[0m"
fi
