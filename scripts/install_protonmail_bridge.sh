#!/usr/bin/env bash

protonmail_bridge_version="3.21.2-1"
protonmail_bridge_arch="x86_64"

rpm-ostree install https://proton.me/download/bridge/protonmail-bridge-$protonmail_bridge_version.$protonmail_bridge_arch.rpm
