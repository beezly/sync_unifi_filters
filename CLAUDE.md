# Claude AI Assistant Context

This document provides context for AI assistants (like Claude) working on this project.

## Project Overview

**sync_unifi_filters** is a Python CLI tool for managing Unifi Network Controller content filtering rules. It allows users to fetch domain block lists from Unifi controllers and sync domain lists back to the controller.

## Architecture

### Core Components

1. **UnifiContentFilter class**: Handles all API interactions with the Unifi Controller
   - `login()`: Authenticates with the controller
   - `get_content_filters()`: Retrieves all content filtering rules
   - `find_filter(name)`: Finds a specific filter by name
   - `update_content_filters(filter_name, domains)`: Updates a filter's domain list

2. **File Operations**:
   - `read_filter_file()`: Reads domains from text file, strips comments
   - `write_filter_file()`: Writes domains to text file with header

3. **CLI Interface**: Uses argparse with two subcommands:
   - `fetch`: Retrieve domains from Unifi (stdout by default, optional file output)
   - `sync`: Upload domains from file to Unifi

### Design Principles

- **Unix philosophy**: Does one thing well, outputs to stdout by default
- **Composable**: Designed to work with pipes and standard Unix tools
- **Clean separation**: Status messages to stderr, data to stdout
- **Generic**: Not tied to specific filter names or use cases

## API Details

### Undocumented API Warning

This tool uses **reverse-engineered, undocumented Unifi APIs**:

- Endpoint pattern: `/proxy/network/v2/api/site/{site}/content-filtering`
- Not in official API docs (checked against network-10.1.68.json spec)
- Uses "v2" versioning that doesn't align with documented "v1" APIs
- May break with controller updates

### API Endpoints Used

1. **Login**: `POST /api/auth/login`
   - Standard documented endpoint
   - Returns session cookie

2. **List filters**: `GET /proxy/network/v2/api/site/{site}/content-filtering`
   - Undocumented
   - Returns array of filter objects

3. **Update filter**: `PUT /proxy/network/v2/api/site/{site}/content-filtering/{id}`
   - Undocumented
   - Updates entire filter object with new `block_list`

## Development Guidelines

### Code Style

- Type hints for function parameters
- Docstrings for all public methods
- Error handling with try/except for network operations
- Print to stderr for status messages, stdout for data

### Testing Considerations

- Requires live Unifi Controller for integration tests
- SSL verification disabled by default (self-signed certs)
- Authentication state maintained in session object
- No unit tests currently (integration tests only)

### Future Enhancements

Potential improvements to consider:

1. **API version detection**: Check controller version and use appropriate endpoints
2. **Bulk operations**: Support multiple filters in one command
3. **Dry-run mode**: Preview changes before applying
4. **Filter creation**: Support creating new filters (currently requires manual UI creation)
5. **Export/import**: Backup and restore all filters at once
6. **Validation**: Check domain format before uploading
7. **Diff mode**: Show changes before applying sync
8. **Watch mode**: Auto-sync when file changes

### Known Limitations

1. **Cannot create filters**: Must exist in UI first
2. **No error recovery**: Failed updates may leave partial state
3. **No rate limiting**: Could overwhelm controller with large operations
4. **Case-sensitive names**: Filter names must match exactly
5. **No validation**: Accepts any string as domain (controller validates)

## Configuration

Environment variables (see code for defaults):
- `UNIFI_HOST`: Controller URL
- `UNIFI_USERNAME`: Admin username
- `UNIFI_PASSWORD`: Admin password
- `UNIFI_SITE`: Site name (default: "default")

## File Structure

```
sync_unifi_filters/
├── sync_unifi_filters.py  # Main script
├── README.md              # User documentation
├── CLAUDE.md              # This file (AI context)
└── .gitignore            # Git ignore rules
```

## Historical Context

Originally created as `sync_samsung_filters.py` specifically for Samsung TV ad-blocking. Refactored to be generic and work with any Unifi content filter. The refactoring included:

- Removed hardcoded "Samsung Adblock" references
- Added argparse for better CLI interface
- Made fetch output to stdout by default
- Moved all status messages to stderr for clean data output
- Renamed to reflect generic nature

## When Making Changes

### Adding Features

- Maintain Unix philosophy (composable, single-purpose)
- Keep stdout clean (data only)
- Add examples to README
- Consider backward compatibility

### Modifying API Calls

- Remember these are undocumented APIs
- Test thoroughly with actual controller
- Document controller version tested
- Consider version detection for future-proofing

### Error Handling

- Print errors to stderr
- Use appropriate exit codes (0 = success, 1 = error)
- Provide helpful error messages
- Don't expose credentials in error messages

## Testing Strategy

Since this uses undocumented APIs:

1. **Manual testing**: Primary testing method
2. **Version tracking**: Document which controller versions work
3. **Error scenarios**: Test with missing filters, wrong credentials, etc.
4. **Edge cases**: Empty filters, large domain lists, special characters

## Support and Maintenance

- Monitor Unifi controller updates for API changes
- Check community forums for reported issues
- Consider adding version detection logic
- Maintain compatibility with reasonable controller versions (e.g., last 3 major releases)

## Getting Help

For AI assistants working on this code:

1. Check the Unifi API docs first (though content-filtering isn't documented)
2. Test changes with actual Unifi controller when possible
3. Maintain the principle of least surprise for users
4. Keep the tool simple and focused
5. Document any API behavior discoveries
