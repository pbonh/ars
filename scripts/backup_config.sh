#!/usr/bin/env bash

# Define the list of configuration paths to back up (files and directories)
declare -a config_paths=("~/.bashrc" "~/.bashrc.d" "~/.cshrc" "~/.config")

# Create a backup directory with current date and time to store backups
backup_dir="$HOME/config_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$backup_dir"

# Log file to record the backup process
log_file="$backup_dir/backup_log.txt"

# Function to backup a file or directory
backup_path() {
    local path=$1
    local dest=$2

    if [[ -e "$path" ]]; then
        if [[ -d "$path" ]]; then
            # It's a directory, use -r to copy recursively
            cp -r "$path" "$dest"
            echo "Backed up directory: $path" | tee -a "$log_file"
        elif [[ -f "$path" ]]; then
            # It's a file, copy normally
            cp "$path" "$dest"
            echo "Backed up file: $path" | tee -a "$log_file"
        fi
    else
        echo "Path not found: $path" | tee -a "$log_file"
    fi
}

# Iterating over each configuration path
for path in "${config_paths[@]}"; do
    # Expanding the tilde to the user's home directory
    expanded_path=$(eval echo "$path")

    # Destination path in the backup directory
    dest_path="$backup_dir/$(basename "$expanded_path")"

    # Perform the backup
    backup_path "$expanded_path" "$dest_path"
done

# Complete message
echo "Backup process complete. Check $log_file for details." | tee -a "$log_file"

