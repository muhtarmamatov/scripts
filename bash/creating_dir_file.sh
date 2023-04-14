#! /bin/bash

echo "==> Enter full path to file"

read -p "Path: " path

dir=$(dirname "$path")
file=$(basename "$path")

if [[ -d $dir && -f "$dir/$file" ]]; then
	echo "==> Directory $dir and file known_hosts exist."
else
	echo "==> Directory or file does not exist."
	select yn in "Create directory" "Exit"; do
		case $yn in
			"Create directory" ) mkdir -p $dir; touch "$dir/$file"; break;;
			"Exit" ) exit;;
		esac
	done
fi

echo "==> Done."

