# clay-tesla 🏎️

CLI tool to control your Tesla vehicle via the Tesla API.

## Prerequisites

- Python 3.9+
- `teslajsonpy` library (pre-installed)
- Tesla account with vehicle

## Installation

```bash
# Already available in your workspace
ln -s projects/clay-tesla/clay_tesla.py tools/clay_tesla.py
```

## Authentication

First, authenticate with your Tesla account:

```bash
python3 tools/clay_tesla.py auth <email> <password>
```

Example:
```bash
python3 tools/clay_tesla.py auth robb99@gmail.com MySecretPassword123
```

Tokens are saved to `~/.clay/tesla/tokens.json` for future use.

## Commands

### List Vehicles
```bash
python3 tools/clay_tesla.py list
```

### Get Vehicle Status
```bash
python3 tools/clay_tesla.py status
```

Shows:
- 🔋 Battery level and charging status
- 🌡️ Cabin temperature and climate state
- 📍 Location (shift state, speed, coordinates)
- 🚙 Lock status, windows, trunk, sentry mode
- 💾 Software version

### Lock/Unlock
```bash
python3 tools/clay_tesla.py lock      # Lock vehicle
python3 tools/clay_tesla.py unlock    # Unlock vehicle
```

### Climate Control
```bash
python3 tools/clay_tesla.py climate 72     # Set temp to 72°F
python3 tools/clay_tesla.py climate-on     # Turn on climate
python3 tools/clay_tesla.py climate-off    # Turn off climate
```

### Honk & Flash
```bash
python3 tools/clay_tesla.py honk    # Honk the horn
python3 tools/clay_tesla.py flash  # Flash lights
```

### Charging
```bash
python3 tools/clay_tesla.py charge-start   # Start charging
python3 tools/clay_tesla.py charge-stop   # Stop charging
```

### Wake Vehicle
```bash
python3 tools/clay_tesla.py wake    # Wake up vehicle (required for commands)
```

### Open Trunk/Frunk
```bash
python3 tools/clay_tesla.py trunk           # Open rear trunk
python3 tools/clay_tesla.py trunk frunk    # Open frunk
```

## JSON Output

All commands support `--json` for scripting:

```bash
python3 tools/clay_tesla.py status --json
```

## Use Cases

- **Pre-condition**: Set climate before leaving
- **Find car**: Flash lights in a parking lot
- **Check charge**: Verify battery level remotely
- **Lock check**: Verify car is locked
- **Wake**: Wake up vehicle before remote commands
- **Delivery**: Open trunk for package delivery

## Troubleshooting

**"Not authenticated"**: Run `auth` command first

**"Vehicle asleep"**: Run `wake` command, wait a few seconds, then retry command

**Token expired**: Re-run `auth` command to refresh tokens

## File Location

- Token storage: `~/.clay/tesla/tokens.json`
- Project: `projects/clay-tesla/`

## GitHub

https://github.com/robb99/clay-tesla
