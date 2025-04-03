#!/bin/bash
# Simple script to list WebDAV directory contents
# Usage: ./webdav-ls.sh [URL] [USERNAME] [TOKEN]

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found."
    exit 1
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Get arguments
URL="${1:-}"
USERNAME="${2:-}"
TOKEN="${3:-}"

# Check for required arguments
if [ -z "$URL" ] || [ -z "$USERNAME" ] || [ -z "$TOKEN" ]; then
    echo "Usage: $0 [URL] [USERNAME] [TOKEN]"
    echo "Example: $0 https://nextcloud.example.com/remote.php/dav/files/user/folder/ username token"
    exit 1
fi

# Run the Python script
python3 "${SCRIPT_DIR}/parse-webdav-xml.py" "$URL" -u "$USERNAME" -t "$TOKEN"
