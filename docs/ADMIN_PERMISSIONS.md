# 🔐 Admin Permissions System

## Overview

The goobie-bot uses a multi-layered permission system to restrict certain commands to authorized users only. This ensures that sensitive operations like cache management and trivia administration are only available to trusted users.

## Protected Commands

The following commands require admin permissions:

- **`!cache <action>`** - Cache statistics and management
- **`!trivia-admin <action>`** - Trivia system administration

**Note**: These are text commands (not slash commands) and are completely hidden from Discord's UI. Users must type them manually.

## Permission Levels

The system checks permissions in the following order:

### 1. User ID Whitelist (Highest Priority)

If `ADMIN_USER_IDS` is configured in the `.env` file, users with those IDs will have admin access regardless of their roles.

```bash
# Example: Grant admin access to specific users
ADMIN_USER_IDS=123456789012345678,987654321098765432
```

### 2. Guild Administrator Role

Users with the "Administrator" permission in the Discord server will have admin access.

### 3. Guild Owner

The server owner will always have admin access.

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# Optional: Admin user IDs (comma-separated)
ADMIN_USER_IDS=123456789012345678,987654321098765432
```

### Discord Role Permissions

Alternatively, you can grant admin access by:

1. **Creating an Admin Role**: Create a role with "Administrator" permission
2. **Assigning Users**: Give the role to users who need admin access
3. **No Environment Variable**: Leave `ADMIN_USER_IDS` empty or unset

## How It Works

### Command Protection

Admin commands are implemented as text commands (not slash commands), which:

- Completely hides the commands from Discord's UI
- Provides maximum security through obscurity
- Requires users to know the exact command syntax
- Prevents accidental discovery by unauthorized users

### Runtime Permission Checks

Each protected command also performs runtime permission checks using `require_admin_permissions()`:

```python
# Check admin permissions
if not require_admin_permissions(interaction):
    return
```

This ensures that even if someone bypasses the UI restrictions, they still can't execute the commands.

### Error Messages

When a user without permissions tries to use a protected command, they receive a clear error message:

```
❌ Access Denied
You don't have permission to use this command.

Required Permissions:
• Administrator role, OR
• Guild owner, OR
• Whitelisted user ID

Contact a server administrator for access
```

## Security Features

### Multi-Layer Protection

1. **Discord UI**: Commands are hidden from unauthorized users
2. **Runtime Checks**: Permission validation on every command execution
3. **Logging**: All admin command usage is logged for security auditing

### Flexible Configuration

- **User ID Whitelist**: For specific trusted users
- **Role-Based**: For broader team access
- **Hybrid**: Combine both approaches for maximum flexibility

### Audit Trail

All admin command usage is logged with:

- User ID and username
- Command executed
- Timestamp
- Server information

## Best Practices

### For Server Administrators

1. **Use Role-Based Access**: Create an "Admin" role for team members
2. **Limit User ID Whitelist**: Only use for specific trusted individuals
3. **Regular Audits**: Check logs for admin command usage
4. **Principle of Least Privilege**: Only grant admin access to users who need it

### For Bot Developers

1. **Always Use Permission Checks**: Even for hidden commands
2. **Clear Error Messages**: Help users understand why access was denied
3. **Logging**: Record all admin actions for security
4. **Documentation**: Clearly document which commands require admin access

## Troubleshooting

### Command Not Visible

- Check if user has Administrator role
- Verify `ADMIN_USER_IDS` configuration
- Ensure user is server owner

### Permission Denied Error

- User doesn't meet any of the permission criteria
- Check server permissions and roles
- Verify environment variable configuration

### Logging Issues

- Check bot logs for permission check results
- Verify user IDs in whitelist are correct
- Ensure bot has proper logging configuration

## Usage Examples

### Cache Management

```
!cache stats          # View cache statistics
!cache clear          # Clear all cache data
!cache cleanup        # Clean up expired entries
!cache                # Show help message
```

### Trivia Administration

```
!trivia-admin stats   # View trivia system statistics
!trivia-admin add     # Instructions for adding questions
!trivia-admin reset   # Reset daily trivia (emergency)
!trivia-admin         # Show help message
```

## Configuration Examples

### Basic Setup (Role-Based)

```bash
# .env file
DISCORD_TOKEN=your_token_here
# No ADMIN_USER_IDS needed - use Discord roles
```

### Specific User Access

```bash
# .env file
DISCORD_TOKEN=your_token_here
ADMIN_USER_IDS=123456789012345678
```

### Team Access

```bash
# .env file
DISCORD_TOKEN=your_token_here
ADMIN_USER_IDS=123456789012345678,987654321098765432,555666777888999000
```

## Security Considerations

- **Environment Variables**: Keep `.env` file secure and don't commit it to version control
- **User ID Privacy**: Be careful when sharing user IDs in logs or documentation
- **Regular Reviews**: Periodically review who has admin access
- **Bot Permissions**: Ensure the bot has only the permissions it needs
- **Server Security**: Use Discord's built-in security features like 2FA for admin users
