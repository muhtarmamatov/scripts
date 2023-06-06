# Set the API token and chat ID
API_TOKEN="<TELEGRAM_BOT_API_TOKEN>"
CHAT_ID="<TELEGRAM_GROUP_CHAT_ID>"
message="Test Message"

# Function to send email and Telegram message
send_notification() {
    #local message="$1"
    #echo "$message" | mail -s "$subject" "$recipient"
    curl -s -X POST "https://api.telegram.org/bot$API_TOKEN/sendMessage" -d "chat_id=$CHAT_ID" -d "text=$message"
}
send_notification