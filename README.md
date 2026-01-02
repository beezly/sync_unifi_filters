# Sync Unifi Filters

A command-line tool to manage Unifi Network Controller content filtering rules. Fetch filter domains from your Unifi controller to stdout or files, and sync domain lists back to the controller.

## Features

- **Fetch filters**: Download content filter domains from Unifi Controller
- **Output to stdout**: Easy piping and command composition
- **File sync**: Update Unifi filters from text files
- **Generic**: Works with any content filter name
- **Flexible**: Save to files or work with pipes

## Requirements

- Python 3.6+
- `requests` library
- Unifi Network Controller with content filtering enabled

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/sync_unifi_filters.git
cd sync_unifi_filters
```

2. Install dependencies:
```bash
pip install requests
```

3. Configure environment variables (or edit the script):
```bash
export UNIFI_HOST="https://unifi.local"
export UNIFI_USERNAME="admin"
export UNIFI_PASSWORD="your_password"
export UNIFI_SITE="default"  # optional, defaults to "default"
```

## Usage

### Fetch Filters

Fetch filter domains and output to stdout:
```bash
./sync_unifi_filters.py fetch "Samsung Adblock"
```

Fetch and save to a file:
```bash
./sync_unifi_filters.py fetch "Samsung Adblock" -o filters.txt
```

### Sync Filters

Update a Unifi filter from a text file:
```bash
./sync_unifi_filters.py sync "Samsung Adblock" filters.txt
```

### Advanced Examples

Count domains in a filter:
```bash
./sync_unifi_filters.py fetch "My Filter" | wc -l
```

Search for specific domains:
```bash
./sync_unifi_filters.py fetch "My Filter" | grep example.com
```

Backup all filters:
```bash
./sync_unifi_filters.py fetch "Ad Blocker" -o backup_ads.txt
./sync_unifi_filters.py fetch "Tracking Blocker" -o backup_tracking.txt
```

Combine multiple filter lists:
```bash
cat list1.txt list2.txt | sort -u > combined.txt
./sync_unifi_filters.py sync "Combined Filter" combined.txt
```

## Filter File Format

Filter files are simple text files with one domain per line:
```
# Comments start with #
example.com
ads.example.net
tracking.example.org
```

## Configuration

Set these environment variables or edit the script directly:

| Variable | Description | Default |
|----------|-------------|---------|
| `UNIFI_HOST` | Unifi Controller URL | `https://unifi.local` |
| `UNIFI_USERNAME` | Controller username | `admin` |
| `UNIFI_PASSWORD` | Controller password | `password` |
| `UNIFI_SITE` | Site name | `default` |

## Important Notes

### Undocumented API

This tool uses **undocumented Unifi Network Controller APIs** (`/proxy/network/v2/api/site/{site}/content-filtering`). These endpoints are not part of the official API specification and may:

- Change without notice in future controller updates
- Behave differently across controller versions
- Be removed or modified in future releases

**Tested with**: Unifi Network Controller 10.1.68

### SSL Verification

The script disables SSL verification for self-signed certificates by default. If you have a valid certificate, you may want to modify this behavior in the code.

### Prerequisites

You must **create the content filter in the Unifi UI first** before using this tool. The script can only update existing filters, not create new ones.

## Troubleshooting

**Filter not found**: Ensure the filter exists in your Unifi Controller UI and the name matches exactly (case-sensitive).

**Authentication errors**: Verify your credentials and that your user has sufficient permissions.

**Connection errors**: Check that your Unifi Controller is accessible at the configured URL.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - See LICENSE file for details

## Disclaimer

This is an unofficial tool that uses undocumented APIs. Use at your own risk. Always backup your Unifi configuration before making changes.
