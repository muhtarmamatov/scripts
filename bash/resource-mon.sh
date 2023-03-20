#! /bin/bash

apps=("top" "free")


echo "==> Required apps list are:  ${apps[*]}"


# Check if required apps top and free exist in system
for app in "${apps[@]}"; do
  if ! command -v "$app" >/dev/null 2>&1; then
    echo "==> Script required app $app does not exist, please install $app and run script <=="
    exit 1
  fi
done

# This script monitors CPU and memory usage

while :
do 
  # Get the current usage of CPU and memory
  cpuUsage=$(top -bn1 | awk '/Cpu/ { print $2}')
  memUsage=$(free -m | awk '/Mem/{print $3}')

  # Print the usage
  echo "==> CPU Usage: $cpuUsage%  <=="
  echo "==> Memory Usage: $memUsage MB <=="
 
  # Sleep for 1 second
  sleep 1
done

