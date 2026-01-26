#!/usr/bin/env bash

# Check for Xcode Command Line Tools
if ! xcode-select -p >/dev/null 2>&1; then
  echo "Xcode Command Line Tools are not installed. Install via 'xcode-select --install' or install Xcode from the App Store, then rerun this script." >&2
  exit 1
fi

echo "Xcode Command Line Tools are installed."
echo "Reminder: install GnuPG (GPG Suite) from https://gpgtools.org/"
