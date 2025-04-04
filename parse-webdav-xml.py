#!/usr/bin/env python3
import sys
import os
import xml.etree.ElementTree as ET
import subprocess
from datetime import datetime
import argparse

def parse_webdav_xml(xml_content):
    """Parse WebDAV XML response and extract file information."""
    # Define the namespaces used in the XML
    namespaces = {
        'd': 'DAV:',
    }
    
    # Parse the XML
    root = ET.fromstring(xml_content)
    
    # List to store file information
    files = []
    
    # Process each response element (each file/directory)
    for response in root.findall('.//d:response', namespaces):
        file_info = {}
        
        # Get the href (path)
        href = response.find('./d:href', namespaces)
        if href is not None:
            path = href.text
            # Extract filename from path
            file_info['filename'] = os.path.basename(path.rstrip('/'))
            if file_info['filename'] == '':
                # This is the current directory, skip it
                continue
        
        # Check if it's a collection (directory)
        resource_type = response.find('./d:propstat/d:prop/d:resourcetype/d:collection', namespaces)
        file_info['is_directory'] = resource_type is not None
        
        # Get the size
        size = response.find('./d:propstat/d:prop/d:getcontentlength', namespaces)
        if size is not None and size.text is not None:
            file_info['size'] = int(size.text)
        else:
            file_info['size'] = 0
        
        # Get the last modified date
        modified = response.find('./d:propstat/d:prop/d:getlastmodified', namespaces)
        if modified is not None:
            try:
                # Try to parse the date format
                date_str = modified.text
                # RFC 1123 date format: Mon, 12 Jan 2020 12:34:56 GMT
                date_obj = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')
                file_info['modified'] = date_obj.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                file_info['modified'] = modified.text
        else:
            file_info['modified'] = 'Unknown'
        
        files.append(file_info)
    
    return files

def format_size(size):
    """Format file size in human-readable format."""
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size/1024:.1f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size/(1024*1024):.1f} MB"
    else:
        return f"{size/(1024*1024*1024):.1f} GB"

def fetch_and_parse_directory(webdav_url, username, token):
    """Fetch directory listing using curl and parse the results."""
    try:
        # Run curl command to get WebDAV PROPFIND response
        cmd = [
            'curl', '-s', '-X', 'PROPFIND', 
            '-u', f'{username}:{token}',
            '-H', 'Depth: 1',
            webdav_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Parse the XML response
        files = parse_webdav_xml(result.stdout)
        
        return files
    except subprocess.CalledProcessError as e:
        print(f"Error running curl command: {e}")
        print(f"Command output: {e.stderr}")
        sys.exit(1)
    except ET.ParseError as e:
        print(f"Error parsing XML response: {e}")
        print("XML content may be invalid or not a WebDAV response.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='List WebDAV directory contents in a readable format')
    parser.add_argument('url', help='WebDAV URL to list')
    parser.add_argument('-u', '--username', required=True, help='WebDAV username')
    parser.add_argument('-t', '--token', required=True, help='WebDAV password or token')
    
    args = parser.parse_args()
    
    # Ensure URL ends with a slash
    url = args.url if args.url.endswith('/') else args.url + '/'
    
    print(f"Listing contents of: {url}")
    print("-" * 80)
    
    # Fetch and parse directory
    files = fetch_and_parse_directory(url, args.username, args.token)
    
    # Sort files (directories first, then alphabetically)
    files.sort(key=lambda x: (not x['is_directory'], x['filename'].lower()))
    
    # Two output modes - pretty table with truncation and full filename list
    
    # Pretty table with truncation first
    max_name_width = 40  # Set default width for display
    
    # Print headers for pretty display
    print(f"{'Type':<4} {'Name':<{max_name_width}} {'Size':<10} {'Modified':<19}")
    print(f"{'-'*4} {'-'*max_name_width} {'-'*10} {'-'*19}")
    
    # Print file listing with truncated names for readability
    for file in files:
        file_type = "DIR" if file['is_directory'] else "FILE"
        name = file['filename']
        display_name = name
        if len(name) > max_name_width:
            display_name = name[:max_name_width-3] + "..."
        
        size = "-" if file['is_directory'] else format_size(file['size'])
        modified = file['modified']
        
        print(f"{file_type:<4} {display_name:<{max_name_width}} {size:<10} {modified}")
    
    print("-" * 80)
    print(f"Total: {len(files)} items")
    
    # Now print full filenames for easy copy/paste
    print("\nFull filenames (for download references):")
    print("-" * 80)
    for file in files:
        file_type = "DIR" if file['is_directory'] else "FILE"
        print(f"{file_type}: {file['filename']}")
    
    print("-" * 80)
    print(f"Total: {len(files)} items")

if __name__ == "__main__":
    main()
