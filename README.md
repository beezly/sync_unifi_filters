# Sync Unifi Filters

A command-line tool to manage Unifi Network Controller content filtering rules. Fetch filter domains from your Unifi controller to stdout or files, and sync domain lists back to the controller.

## Features

- **Fetch filters**: Download content filter domains from Unifi Controller
- **Output to stdout**: Easy piping and command composition
- **File sync**: Update Unifi filters from text files
- **Generic**: Works with any content filter name
- **Flexible**: Save to files or work with pipes

## Requirements

- **Python 3.6 or higher** (uses f-strings and type hints)
- `requests` library (>=2.25.0)
- Unifi Network Controller with content filtering enabled

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/sync_unifi_filters.git
cd sync_unifi_filters
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install requests
```

## Configuration

The script requires authentication credentials to connect to your Unifi Controller. You can provide these in two ways:

### Method 1: Environment Variables (Recommended)

Set environment variables before running commands:

```bash
export UNIFI_HOST="https://192.168.1.1"      # Your Unifi Controller URL
export UNIFI_USERNAME="admin"                # Controller admin username
export UNIFI_PASSWORD="your_password"        # Controller password
export UNIFI_SITE="default"                  # Site name (optional, defaults to "default")
```

Then run commands normally:
```bash
./sync_unifi_filters.py fetch "Samsung Adblock"
```

### Method 2: Inline Environment Variables

Provide credentials inline with each command:

```bash
UNIFI_HOST=https://192.168.1.1 \
UNIFI_USERNAME=admin \
UNIFI_PASSWORD=your_password \
./sync_unifi_filters.py fetch "Samsung Adblock"
```

### Method 3: Edit the Script

Modify the default values in `sync_unifi_filters.py` (lines 13-16):

```python
UNIFI_HOST = os.getenv("UNIFI_HOST", "https://192.168.1.1")
UNIFI_USERNAME = os.getenv("UNIFI_USERNAME", "admin")
UNIFI_PASSWORD = os.getenv("UNIFI_PASSWORD", "your_password")
SITE_NAME = os.getenv("UNIFI_SITE", "default")
```

### Configuration Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `UNIFI_HOST` | **Yes** | Full URL to your Unifi Controller (including `https://`) | `https://192.168.1.1` or `https://unifi.local` |
| `UNIFI_USERNAME` | **Yes** | Admin username for the controller | `admin` |
| `UNIFI_PASSWORD` | **Yes** | Password for the admin account | `your_password` |
| `UNIFI_SITE` | No | Site name in multi-site setups | `default` (default), `office`, `home`, etc. |

**Security Note**: Avoid storing passwords in shell history. Consider using exported environment variables in your shell profile or a `.env` file (not committed to git).

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

## Important Notes

### Prerequisites: Creating a Content Filter

Before using this tool, you **must create a content filter in the Unifi Controller UI first**. The script can only update existing filters, not create new ones.

#### Setting Up a Content Filter in Unifi

1. **Navigate to**: Settings → Security → Content Filtering
2. **Click**: "Create New Content Filtering Rule"
3. **Configure the filter**:
   - **Name**: Choose a descriptive name (e.g., "Samsung Adblock")
   - **Categories**: Select "Basic" filtering (you do NOT need CyberSecure Enhanced subscription)
   - **Ad Block**: NOT required - you can leave this disabled
   - **Sources**: **Important** - Define which networks or client devices this filter applies to
     - Select specific networks (e.g., IoT network, Guest network)
     - Or select specific client devices by MAC address
   - **Block List**: You can leave this empty or add a few sample domains - the script will overwrite it
4. **Save** the filter

**Important**: The filter name in the Unifi UI must exactly match the name you use in the script commands (case-sensitive).

**Reference**: For more information about Unifi Content Filtering, see the [official Unifi documentation](https://help.ui.com/hc/en-us/articles/12568927589143-Content-and-Domain-Filtering-in-UniFi).

#### Subscription Requirements

- **No CyberSecure Enhanced subscription required**
- Basic content filtering is available in all Unifi Network Controller installations
- You only need "Basic" category filtering enabled
- Ad Block features are NOT required for this tool to work

### Undocumented API

This tool uses **undocumented Unifi Network Controller APIs** (`/proxy/network/v2/api/site/{site}/content-filtering`). These endpoints are not part of the official API specification and may:

- Change without notice in future controller updates
- Behave differently across controller versions
- Be removed or modified in future releases

**Tested with**: Unifi Network Controller 10.1.68

### SSL Verification

The script disables SSL verification for self-signed certificates by default. If you have a valid certificate, you may want to modify this behavior in the code.

## Troubleshooting

**Filter not found**:
- Ensure the filter exists in your Unifi Controller UI (Settings → Security → Content Filtering)
- The filter name must match exactly (case-sensitive)
- See "Prerequisites: Creating a Content Filter" above for setup instructions

**Authentication errors**:
- Verify your `UNIFI_USERNAME` and `UNIFI_PASSWORD` are correct
- Ensure your user has admin permissions on the controller

**Connection errors**:
- Check that your Unifi Controller is accessible at the configured `UNIFI_HOST` URL
- Verify the URL includes `https://` (e.g., `https://192.168.1.1`)
- If using a hostname, ensure it resolves correctly

**403 Forbidden errors**:
- This typically indicates CSRF token issues (should be fixed in current version)
- Try logging out and back in to the Unifi UI
- Ensure you're using an admin account with full permissions

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - See LICENSE file for details

## Disclaimer

This is an unofficial tool that uses undocumented APIs. Use at your own risk. Always backup your Unifi configuration before making changes.
