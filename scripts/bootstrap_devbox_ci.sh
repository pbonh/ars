#!/usr/bin/env bash

# Nix via Determinate Systems
curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install --no-confirm
. /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh

# Devbox
curl -fsSL https://get.jetpack.io/devbox | bash -s -- -f

eval "$(devbox global shellenv --recompute)"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}


# Function to ensure necessary commands are available
ensure_commands() {
    local missing_cmds=()

    # # Install Nix
    # if ! command_exists nix; then
    #     just nix-install
    # fi
    if ! command_exists devbox; then
        missing_cmds+=("devbox")
    fi

    # Handle missing commands
    if [ ${#missing_cmds[@]} -ne 0 ]; then
        echo "The following commands are not available but are required: ${missing_cmds[*]}"
        echo "Please install them and rerun the script."
        exit 1
    fi
}

# Function to setup Bash
setup_bashrc() {
    # Define the directory and file path
    bashrc_d_dir="$HOME/.bashrc.d"
    devbox_file="$bashrc_d_dir/devbox"

    # Create the ~/.bashrc.d directory if it does not exist
    if [[ ! -d "$bashrc_d_dir" ]]; then
        mkdir -p "$bashrc_d_dir"
        echo "Created directory: $bashrc_d_dir"
    fi

    # Create and populate the devbox file if it does not exist
    if [[ ! -f "$devbox_file" ]]; then
        cat <<-EOF > "$devbox_file"
        # Add nix to PATH manually
        export PATH=\$PATH:/nix/var/nix/profiles/default/bin
        # Source Devbox Global
        eval "\$(devbox global shellenv --init-hook)"
EOF
        echo "Created and initialized file: $devbox_file"
    else
        echo "File already exists: $devbox_file"
    fi
}

# Install Tools(Devbox)
install_prereq() {
    devbox global add ansible just
    eval "$(devbox global shellenv --preserve-path-stack -r)" && hash -r
    cp ./vars/example.yml ./vars/term-dev.yml
    just devbox
    eval "$(devbox global shellenv --preserve-path-stack -r)" && hash -r
}

# Install Dotfiles(Devbox)
install_dotfiles() {
    just dot-all
}

ensure_commands
setup_bashrc
install_prereq
install_dotfiles
