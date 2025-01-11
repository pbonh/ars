#!/usr/bin/env bash

# Install Devbox Tools
devbox global add \
    gcc \
    joplin \
    zellij \
    tmux \
    oil \
    tcsh \
    zsh \
    zoxide \
    zsh-powerlevel10k \
    atuin \
    starship \
    xcp \
    nushell \
    carapace \
    gum \
    glow \
    just \
    direnv \
    nix-direnv \
    rargs \
    fzf \
    tree \
    fd \
    ripgrep \
    ugrep \
    bat \
    exa \
    lsd \
    kmon \
    navi \
    skim \
    hyperfine \
    procs \
    ouch \
    sd \
    rnr \
    diskonaut \
    du-dust \
    tokei \
    bottom \
    choose \
    grex \
    curl \
    delta \
    git \
    gitAndTools.gh \
    act \
    lazygit \
    gitflow \
    gitui \
    gitoxide \
    soft-serve \
    diffr \
    difftastic \
    python39Packages.pipx \
    btop \
    clifm \
    ranger \
    xplr \
    yazi \
    joshuto \
    eva \
    erdtree \
    felix \
    fend \
    gotop \
    screenfetch \
    macchina \
    mprocs \
    jq \
    yq \
    fx \
    nnn \
    fff \
    ghq \
    broot \
    lf \
    watchman \
    aspell \
    bc \
    gdb \
    emscripten \
    nox \
    cookiecutter \
    helix \
    neovim \
    neovim-remote \
    tree-sitter \
    python39Packages.pynvim \
    nodejs \
    yarn \
    ctags \
    nodePackages.prettier \
    nodePackages.bash-language-server \
    nodePackages.yaml-language-server \
    sumneko-lua-language-server \
    shfmt

    # ast-grep

# Refresh Global Environment
eval "$(devbox global shellenv --preserve-path-stack -r)"


# Insecure Packages
# sc-im
