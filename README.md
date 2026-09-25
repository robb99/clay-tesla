# clay-tesla 🚗

Tesla CLI control tool for Clay - Control your Tesla Model 3 via command line.

## Features

- 🔋 **Status** - Get battery, charging, climate, lock status
- 🔒 **Lock/Unlock** - Remote lock and unlock
- 📢 **Honk/Flash** - Honk horn or flash lights
- 🌡️ **Climate** - Set temperature, start/stop climate control
- 🔌 **Charge** - Set charge limit, start/stop charging
- 📍 **Location** - Get GPS coordinates
- 👜 **Trunks** - Open frunk or trunk
- 👀 **Wake** - Wake up the vehicle

## Requirements

```bash
pip install teslajsonpy
```

## Setup

### Get Tesla Refresh Token

1. Go to https://tesla-api.timdorr.org/
2. Follow the instructions to get your refresh token
3. Or use the Tesla Token Generator: https://tesla-token-generator.com/

### Configure Environment

```bash
# Add to your shell profile (.zshrc, etc.)
export TESLA_EMAIL="your@email.com"
export TESLA_TOKEN="your_refresh_token"
```

Or pass credentials via command line:
```bash
python3 clay_tesla.py --email "your@email.com" --token "your_token" status
```

## Usage

```bash
# Get vehicle status
python3 clay_tesla.py status
python3 clay_tesla.py status --verbose  # More details

# Lock/unlock
python3 clay_tesla.py lock
python3 clay_tesla.py unlock

# Honk and flash
python3 clay_tesla.py honk
python3 clay_tesla.py flash

# Climate control
python3 clay_tesla.py climate 72       # Set to 72F
python3 clay_tesla.py start-climate   # Start climate
python3 clay_tesla.py stop-climate    # Stop climate

# Charge
python3 clay_tesla.py charge 80      # Set limit to 80%
python3 clay_tesla.py start-charging
python3 clay_tesla.py stop-charging

# Trunks
python3 clay_tesla.py open trunk       # Open rear trunk
python3 clay_tesla.py open frunk       # Open frunk

# Location
python3 clay_tesla.py where            # Get GPS coordinates

# Wake
python3 clay_tesla.py wake            # Wake up vehicle

# JSON output
python3 clay_tesla.py status --json
python3 clay_tesla.py where --json
```

## Example Output

```
🚗 Model 3 Performance
   State: sleeping
   🔒 Locked: Yes
   🔋 Battery: 72% (215 mi)
   ⚡ Charging: Disconnected
   🌡️ Cabin: 68°F (outside 55°F)
   🪟 Windows: Closed
   👁️ Sentry: Off
```

## Use Cases

- **Precondition** - Start climate before leaving
- **Find car** - Flash lights in parking lot
- **Security** - Lock remotely, check status
- **Charging** - Set charge limit, monitor
- **Delivery** - Open trunk for package delivery

## Integration with Clay

This tool can be used by Clay for:
- "What's my car's status?" → Reads battery, charging, location
- "Lock the car" → Locks Tesla
- "Warm up the car" → Starts climate
- "Where is my car?" → Gets GPS location
