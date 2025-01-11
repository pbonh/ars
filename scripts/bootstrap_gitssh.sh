#!/usr/bin/env bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to ensure necessary commands are available
ensure_commands() {
    local missing_cmds=()

    # Check for git
    if ! command_exists git; then
        missing_cmds+=("git")
    fi

    # Handle missing commands
    if [ ${#missing_cmds[@]} -ne 0 ]; then
        echo "The following commands are not available but are required: ${missing_cmds[*]}"
        echo "Please install them and rerun the script."
        exit 1
    fi
}

# Check if necessary commands are available
ensure_commands

# Function to update .gitconfig with user's name, email, and ghq settings
update_gitconfig() {
    local name="$1"
    local email="$2"
    local domain="$3"
    local username="$4"
    local checkout_dir="$5"

    # Configure user name and email
    git config --global user.name "$name"
    git config --global user.email "$email"

    # Configure Git settings
    git config --global init.defaultBranch main

    # Configure ghq settings
    git config --global "ghq.ssh://git@$domain/$username.vcs" git
    git config --global "ghq.ssh://git@$domain/$username.root" "$HOME/$checkout_dir"
}

# Function to create directory for code checkouts
create_checkout_dir() {
    local checkout_dir="$1"

    # Check if directory exists
    if [[ -d "$HOME/$checkout_dir" ]]; then
        echo "Directory $HOME/$checkout_dir already exists."
    else
        # Create directory
        mkdir -p "$HOME/$checkout_dir"
        echo "Directory $HOME/$checkout_dir created."
    fi
}

# Function to create directory for code checkouts
create_ssh_key() {
    local email="$1"
    local ssh_key=".ssh/id_ed25519.pub"

    # Check if ssh key exists
    if [[ -f "$HOME/$ssh_key" ]]; then
        echo "SSH Key $HOME/$ssh_key already exists."
    else
        # Create SSH Key
        ssh-keygen -t ed25519 -C "$email"
        echo "SSH Key $HOME/$ssh_key created."
    fi
}

# Main script execution starts here

# Prompt for user details
read -p "Enter your first and last name: " full_name
read -p "Enter your email address: " email
read -p "Enter the domain name for GHQ (e.g., git.example.com): " domain
read -p "Enter your GHQ username (repos name): " username
read -p "Enter the directory path for coding checkouts: " checkout_dir

# Update .gitconfig with the provided details
update_gitconfig "$full_name" "$email" "$domain" "$username" "$checkout_dir"

# Create the coding checkout directory
create_checkout_dir "$checkout_dir"

# Create SSH Key
create_ssh_key "$email"

echo "Setup complete."

