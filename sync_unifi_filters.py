#!/usr/bin/env python3
"""
Sync content filters between a text file and Unifi Controller
"""
import requests
import sys
import os
import argparse
import json
import base64
from typing import List

# Configuration - Can be set via environment variables or updated here
UNIFI_HOST = os.getenv("UNIFI_HOST", "https://unifi.local")
UNIFI_USERNAME = os.getenv("UNIFI_USERNAME", "admin")
UNIFI_PASSWORD = os.getenv("UNIFI_PASSWORD", "password")
SITE_NAME = os.getenv("UNIFI_SITE", "default")
FILTER_FILE = os.getenv("FILTER_FILE", "samsung_adblock_filters.txt")

class UnifiContentFilter:
    def __init__(self, host, username, password, site="default"):
        self.host = host.rstrip('/')
        self.username = username
        self.password = password
        self.site = site
        self.session = requests.Session()
        self.session.verify = False  # Disable SSL verification for self-signed certs
        self.csrf_token = None

    def _extract_csrf_token(self):
        """Extract CSRF token from JWT cookie"""
        token_cookie = self.session.cookies.get('TOKEN')
        if not token_cookie:
            return None

        try:
            # JWT format: header.payload.signature
            parts = token_cookie.split('.')
            if len(parts) != 3:
                return None

            # Decode the payload (add padding if needed for base64)
            payload = parts[1]
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += '=' * padding

            decoded = base64.urlsafe_b64decode(payload)
            payload_data = json.loads(decoded)

            return payload_data.get('csrfToken')
        except Exception as e:
            print(f"Warning: Could not extract CSRF token: {e}", file=sys.stderr)
            return None

    def login(self):
        """Login to Unifi Controller"""
        url = f"{self.host}/api/auth/login"
        data = {
            "username": self.username,
            "password": self.password
        }
        response = self.session.post(url, json=data)
        response.raise_for_status()

        # Extract CSRF token from JWT cookie
        self.csrf_token = self._extract_csrf_token()
        if self.csrf_token:
            print("✓ Logged in to Unifi Controller (CSRF token acquired)", file=sys.stderr)
        else:
            print("✓ Logged in to Unifi Controller (Warning: No CSRF token)", file=sys.stderr)

    def get_content_filters(self):
        """Get all content filtering rules"""
        url = f"{self.host}/proxy/network/v2/api/site/{self.site}/content-filtering"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def find_filter(self, filter_name: str):
        """Find a content filter rule by name"""
        filters = self.get_content_filters()
        for f in filters:
            if f.get('name') == filter_name:
                return f
        return None

    def update_content_filters(self, filter_name: str, domains: List[str]):
        """Update content filter domains"""
        content_filter = self.find_filter(filter_name)

        if not content_filter:
            print(f"✗ Filter '{filter_name}' not found. Please create it in the Unifi UI first.", file=sys.stderr)
            return False

        filter_id = content_filter['_id']
        url = f"{self.host}/proxy/network/v2/api/site/{self.site}/content-filtering/{filter_id}"

        # Update the block_list with new domains
        content_filter['block_list'] = domains

        # Add CSRF token header if available
        headers = {}
        if self.csrf_token:
            headers['X-CSRF-Token'] = self.csrf_token

        response = self.session.put(url, json=content_filter, headers=headers)
        response.raise_for_status()
        print(f"✓ Updated {len(domains)} domains on Unifi Controller", file=sys.stderr)
        return True

def read_filter_file(filepath: str, silent: bool = False) -> List[str]:
    """Read filter file and return list of domains, ignoring comments"""
    domains = []

    if not os.path.exists(filepath):
        if not silent:
            print(f"✗ Filter file '{filepath}' not found", file=sys.stderr)
        return domains

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith('#'):
                domains.append(line)

    if not silent:
        print(f"✓ Read {len(domains)} domains from {filepath}", file=sys.stderr)
    return domains

def write_filter_file(filepath: str, domains: List[str], filter_name: str = "Content Filter"):
    """Write domains to filter file"""
    with open(filepath, 'w') as f:
        f.write(f"# {filter_name}\n")
        f.write("# Lines starting with '#' are comments\n")
        f.write("# Edit this file and run 'sync' to update the Unifi controller\n\n")

        for domain in sorted(domains):
            f.write(f"{domain}\n")

    print(f"✓ Wrote {len(domains)} domains to {filepath}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(
        description='Sync content filters between a text file and Unifi Controller',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch filter and output to stdout
  %(prog)s fetch "Samsung Adblock"

  # Fetch filter and save to file
  %(prog)s fetch "Samsung Adblock" -o filters.txt

  # Sync filters from file to Unifi
  %(prog)s sync "Samsung Adblock" filters.txt
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute', required=True)

    # Fetch command
    fetch_parser = subparsers.add_parser('fetch', help='Fetch filters from Unifi Controller')
    fetch_parser.add_argument('filter_name', help='Name of the content filter in Unifi')
    fetch_parser.add_argument('-o', '--output', help='Output file (default: stdout)')

    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Sync filters from file to Unifi Controller')
    sync_parser.add_argument('filter_name', help='Name of the content filter in Unifi')
    sync_parser.add_argument('file', help='File containing filter domains')

    args = parser.parse_args()

    # Disable SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Create Unifi client
    unifi = UnifiContentFilter(UNIFI_HOST, UNIFI_USERNAME, UNIFI_PASSWORD, SITE_NAME)

    try:
        unifi.login()

        if args.command == "fetch":
            # Fetch from Unifi
            content_filter = unifi.find_filter(args.filter_name)
            if not content_filter:
                print(f"✗ Filter '{args.filter_name}' not found. Please create it in the Unifi UI first.", file=sys.stderr)
                sys.exit(1)

            domains = content_filter.get('block_list', [])
            print(f"✓ Fetched {len(domains)} domains from Unifi Controller", file=sys.stderr)

            if args.output:
                # Write to file
                write_filter_file(args.output, domains, args.filter_name)
            else:
                # Output to stdout
                for domain in sorted(domains):
                    print(domain)

        elif args.command == "sync":
            # Read from file and sync to Unifi
            domains = read_filter_file(args.file)
            if domains:
                success = unifi.update_content_filters(args.filter_name, domains)
                if not success:
                    sys.exit(1)
            else:
                print("✗ No domains to sync", file=sys.stderr)
                sys.exit(1)

    except requests.exceptions.RequestException as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
