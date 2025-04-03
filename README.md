# WebDAV Directory Tools

A set of utilities for listing and downloading files from WebDAV servers (like Nextcloud, OwnCloud, etc.) from the command line.

## Features

- List WebDAV directory contents in a readable, formatted table
- Display file types, names, sizes, and modification dates
- Support for authenticated WebDAV servers
- Compatible with Nextcloud, OwnCloud, and other WebDAV-compliant servers

## Requirements

- Python 3.6 or higher
- curl (installed on most Unix-like systems by default)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/webdav-tools.git
   cd webdav-tools
   ```

2. Make the scripts executable:
   ```bash
   chmod +x parse-webdav-xml.py webdav-ls.sh
   ```

## Usage

### Listing Directory Contents

Use the `webdav-ls.sh` script to list the contents of a WebDAV directory:

```bash
./webdav-ls.sh [URL] [USERNAME] [TOKEN/PASSWORD]
```

Example:
```bash
./webdav-ls.sh https://nextcloud.example.com/remote.php/dav/files/user/folder/ username password
```

### Sample Output

```
Listing contents of: https://nextcloud.example.com/remote.php/dav/files/user/folder/
--------------------------------------------------------------------------------
Type Name                                     Size       Modified           
---- ---------------------------------------- ---------- -------------------
DIR  subfolder1                               -          2023-01-15 12:34:56
DIR  subfolder2                               -          2023-01-15 12:34:56
FILE example.dat                              1.2 MB     2023-01-15 12:34:56
FILE data.txt                                 45.3 KB    2023-01-15 12:34:56
--------------------------------------------------------------------------------
Total: 4 items
```

### Downloading Files

Once you've identified the file you want to download, use curl directly:

```bash
curl -u USERNAME:TOKEN URL_TO_FILE --output local_filename
```

Example:
```bash
curl -u username:password https://nextcloud.example.com/remote.php/dav/files/user/folder/example.dat --output example.dat
```

For large files, you can add a progress indicator:
```bash
curl -# -u username:password https://nextcloud.example.com/remote.php/dav/files/user/folder/example.dat --output example.dat
```

## Advanced Usage

### Python Script Direct Usage

You can also use the Python script directly:

```bash
python3 parse-webdav-xml.py [URL] -u [USERNAME] -t [TOKEN/PASSWORD]
```

### Batch Downloading

To download all files in a directory, you can combine the listing script with curl:

```bash
# First, list and save the filenames
./webdav-ls.sh https://nextcloud.example.com/remote.php/dav/files/user/folder/ username password > file_list.txt

# Then parse the output and download each file (example using awk and bash)
awk '/^FILE/ {print $2}' file_list.txt | while read filename; do
  curl -u username:password "https://nextcloud.example.com/remote.php/dav/files/user/folder/$filename" --output "$filename"
  echo "Downloaded $filename"
done
```