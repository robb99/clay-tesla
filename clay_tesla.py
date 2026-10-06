#!/usr/bin/env python3
"""
clay-tesla - Tesla Vehicle Control CLI
Control your Tesla from the command line using the Tesla API.
"""

import argparse
import json
import os
import sys
import subprocess
from pathlib import Path

# Try to import teslajsonpy
try:
    import teslajsonpy
    from teslajsonpy import Tesla
    from teslajsonpy.controller import Controller
except ImportError:
    print("ERROR: teslajsonpy not installed. Run: pip install teslajsonpy")
    sys.exit(1)

# Config paths
CONFIG_DIR = Path.home() / ".clay" / "tesla"
CONFIG_FILE = CONFIG_DIR / "config.json"
TOKEN_FILE = CONFIG_DIR / "tokens.json"

# Ensure config directory exists
CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_tokens():
    """Load Tesla API tokens from file."""
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, 'r') as f:
            return json.load(f)
    return None


def save_tokens(tokens):
    """Save Tesla API tokens to file."""
    with open(TOKEN_FILE, 'w') as f:
        json.dump(tokens, f, indent=2)


def authenticate(email, password):
    """Authenticate with Tesla API and save tokens."""
    print(f"Authenticating with Tesla API for {email}...")
    try:
        # Create API connection
        api = Tesla(email, password)
        
        # Get tokens
        tokens = api.get_tokens()
        
        if tokens:
            save_tokens(tokens)
            print("✅ Authentication successful! Tokens saved.")
            return True
        else:
            print("❌ Authentication failed - no tokens received")
            return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False


def get_api():
    """Get authenticated Tesla API instance."""
    tokens = load_tokens()
    if not tokens:
        print("❌ Not authenticated. Run: clay_tesla.py auth <email> <password>")
        return None
    
    try:
        # Re-authenticate with stored tokens
        api = Tesla(tokens['tokens']['access_token'], tokens['tokens']['refresh_token'], tokens['vehicle_id'])
        return api
    except Exception as e:
        print(f"❌ Error connecting to Tesla API: {e}")
        return None


def list_vehicles(api):
    """List all vehicles associated with the account."""
    try:
        vehicles = api.get_vehicles()
        print(f"\n🚗 Your Tesla Vehicles:")
        print("-" * 50)
        for i, v in enumerate(vehicles):
            print(f"  {i+1}. {v['display_name']}")
            print(f"      VIN: {v['vin'][-6:]}")
            print(f"      ID: {v['id']}")
        print("-" * 50)
        return vehicles
    except Exception as e:
        print(f"❌ Error listing vehicles: {e}")
        return []


def status(api, vehicle_id=None):
    """Get vehicle status."""
    try:
        vehicles = api.get_vehicles()
        
        # Select vehicle
        if vehicle_id:
            vehicle = next((v for v in vehicles if str(v['id']) == str(vehicle_id)), None)
            if not vehicle:
                print(f"❌ Vehicle {vehicle_id} not found")
                return
        else:
            vehicle = vehicles[0] if vehicles else None
            
        if not vehicle:
            print("❌ No vehicles found")
            return
        
        # Get vehicle data
        vehicle_data = api.get_vehicle_data(vehicle['id'])
        
        print(f"\n🚗 {vehicle['display_name']} Status")
        print("=" * 50)
        
        # Charge state
        charge = vehicle_data.get('charge_state', {})
        print(f"🔋 Battery: {charge.get('battery_level', 'N/A')}%")
        print(f"   Charging: {charge.get('charging_state', 'N/A')}")
        print(f"   Range: {charge.get('battery_range', 'N/A')} miles")
        if charge.get('charge_limit_soc'):
            print(f"   Charge Limit: {charge.get('charge_limit_soc')}%")
        
        # Climate
        climate = vehicle_data.get('climate_state', {})
        print(f"🌡️ Climate:")
        print(f"   Cabin Temp: {climate.get('cabin_temp_driver_set', 'N/A')}°F")
        print(f"   Outside Temp: {climate.get('outside_temp', 'N/A')}°F")
        print(f"   Running: {climate.get('is_climate_on', False)}")
        
        # Location
        drive = vehicle_data.get('drive_state', {})
        print(f"📍 Location:")
        print(f"   Shift State: {drive.get('shift_state', 'Parked')}")
        print(f"   Speed: {drive.get('speed', '0')} mph")
        lat = drive.get('latitude')
        lon = drive.get('longitude')
        if lat and lon:
            print(f"   Coordinates: {lat}, {lon}")
        
        # Vehicle state
        vehicle_state = vehicle_data.get('vehicle_state', {})
        print(f"🚙 Vehicle:")
        print(f"   Locked: {vehicle_state.get('locked', 'N/A')}")
        print(f"   Frunk: {vehicle_state.get('frunk_open', 'N/A')}")
        print(f"   Trunk: {vehicle_state.get('trunk_open', 'N/A')}")
        print(f"   Windows Open: {vehicle_state.get('windows_open', 'N/A')}")
        print(f"   Sentry Mode: {vehicle_state.get('sentry_mode', 'N/A')}")
        
        # Software
        print(f"💾 Software: {vehicle_state.get('car_version', 'N/A')}")
        
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error getting status: {e}")


def honk(api, vehicle_id=None):
    """Honk the horn."""
    try:
        vehicles = api.get_vehicles()
        vehicle = vehicles[0] if not vehicle_id else next((v for v in vehicles if str(v['id']) == str(vehicle_id)), vehicles[0])
        
        api.horn(vehicle['id'])
        print("📢 Honk! Honk! 🔊")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def flash(api, vehicle_id=None):
    """Flash the lights."""
    try:
        vehicles = api.get_vehicles()
        vehicle = vehicles[0] if not vehicle_id else next((v for v in vehicles if str(v['id']) == str(vehicle_id)), vehicles[0])
        
        api.flash_lights(vehicle['id'])
        print("💡 Lights flashed!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def lock(api, vehicle_id=None):
    """Lock the vehicle."""
    try:
        vehicles = api.get_vehicles()
        vehicle = vehicles[0] if not vehicle_id else next((v for v in vehicles if str(v['id']) == str(vehicle_id)), vehicles[0])
        
        api.lock(vehicle['id'])
        print("🔒 Vehicle locked!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def unlock(api, vehicle_id=None):
    """Unlock the vehicle."""
    try:
        vehicles = api.get_vehicles()
        vehicle = vehicles[0] if not vehicle_id else next((v for v in vehicles if str(v['id']) == str(vehicle_id)), vehicles[0])
        
        api.unlock(vehicle['id'])
        print("🔓 Vehicle unlocked!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def climate(api, temp, vehicle_id=None):
    """Set climate temperature."""
    try:
        vehicles = api.get_vehicles()
        vehicle = vehicles[0] if not vehicle_id else next((v for v in vehicles if str(v['id']) == str(vehicle_id)), vehicles[0])
        
        api.set_temps(vehicle['id'], temp, temp)
        print(f"🌡️ Climate set to {temp}°F!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def climate_on(api, vehicle_id=None):
    """Turn on climate control."""
    try:
        vehicles = api.get_vehicles()
        vehicle = vehicles[0] if not vehicle_id else next((v for v in vehicles if str(v['id']) == str(vehicle_id)), vehicles[0])
        
        api.set_auto_conditioning_on(vehicle['id'])
        print("🌡️ Climate control ON!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def climate_off(api, vehicle_id=None):
    """Turn off climate control."""
    try:
        vehicles = api.get_vehicles()
        vehicle = vehicles[0] if not vehicle_id else next((v for v in vehicles if str(v['id']) == str(vehicle_id)), vehicles[0])
        
        api.set_auto_conditioning_on(vehicle['id'], False)
        print("🌡️ Climate control OFF!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def start_charging(api, vehicle_id=None):
    """Start charging."""
    try:
        vehicles = api.get_vehicles()
        vehicle = vehicles[0] if not vehicle_id else next((v for v in vehicles if str(v['id']) == str(vehicle_id)), vehicles[0])
        
        api.start_charging(vehicle['id'])
        print("🔌 Charging started!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def stop_charging(api, vehicle_id=None):
    """Stop charging."""
    try:
        vehicles = api.get_vehicles()
        vehicle = vehicles[0] if not vehicle_id else next((v for v in vehicles if str(v['id']) == str(vehicle_id)), vehicles[0])
        
        api.stop_charging(vehicle['id'])
        print("🔌 Charging stopped!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def wake(api, vehicle_id=None):
    """Wake up the vehicle."""
    try:
        vehicles = api.get_vehicles()
        vehicle = vehicles[0] if not vehicle_id else next((v for v in vehicles if str(v['id']) == str(vehicle_id)), vehicles[0])
        
        api.wake_up(vehicle['id'])
        print("☀️ Vehicle waking up...")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def open_trunk(api, which="rear", vehicle_id=None):
    """Open trunk or frunk."""
    try:
        vehicles = api.get_vehicles()
        vehicle = vehicles[0] if not vehicle_id else next((v for v in vehicles if str(v['id']) == str(vehicle_id)), vehicles[0])
        
        if which == "frunk":
            api.actuate_trunk(vehicle['id'], 0)  # 0 = frunk
            print("👜 Frunk opening...")
        else:
            api.actuate_trunk(vehicle['id'], 1)  # 1 = rear trunk
            print("🚗 Trunk opening...")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Clay Tesla - Control your Tesla from command line",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  clay_tesla.py auth email@example.com password    Authenticate with Tesla
  clay_tesla.py list                                List your vehicles
  clay_tesla.py status                             Get vehicle status
  clay_tesla.py lock                               Lock the car
  clay_tesla.py unlock                             Unlock the car
  clay_tesla.py climate 72                        Set temp to 72F
  clay_tesla.py climate-on                        Turn on climate
  clay_tesla.py honk                               Honk the horn
  clay_tesla.py flash                              Flash lights
  clay_tesla.py charge-start                      Start charging
  clay_tesla.py wake                              Wake up vehicle
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Auth
    auth_parser = subparsers.add_parser('auth', help='Authenticate with Tesla')
    auth_parser.add_argument('email', help='Tesla account email')
    auth_parser.add_argument('password', help='Tesla account password')
    
    # List vehicles
    subparsers.add_parser('list', help='List all vehicles')
    
    # Status
    status_parser = subparsers.add_parser('status', help='Get vehicle status')
    status_parser.add_argument('--id', help='Vehicle ID', default=None)
    
    # Lock/Unlock
    subparsers.add_parser('lock', help='Lock vehicle')
    subparsers.add_parser('unlock', help='Unlock vehicle')
    
    # Honk/Flash
    subparsers.add_parser('honk', help='Honk the horn')
    subparsers.add_parser('flash', help='Flash lights')
    
    # Climate
    climate_parser = subparsers.add_parser('climate', help='Set climate temperature')
    climate_parser.add_argument('temp', type=float, help='Temperature in Fahrenheit')
    
    subparsers.add_parser('climate-on', help='Turn on climate control')
    subparsers.add_parser('climate-off', help='Turn off climate control')
    
    # Charging
    subparsers.add_parser('charge-start', help='Start charging')
    subparsers.add_parser('charge-stop', help='Stop charging')
    
    # Wake
    subparsers.add_parser('wake', help='Wake up vehicle')
    
    # Trunk
    trunk_parser = subparsers.add_parser('trunk', help='Open trunk/frunk')
    trunk_parser.add_argument('which', nargs='?', choices=['frunk', 'rear'], default='rear', help='Which to open')
    
    # JSON output
    parser.add_argument('--json', action='store_true', help='JSON output')
    
    args = parser.parse_args()
    
    # Handle commands
    if args.command == 'auth':
        success = authenticate(args.email, args.password)
        sys.exit(0 if success else 1)
    
    # Get API for other commands
    api = get_api()
    if not api and args.command not in ['auth']:
        sys.exit(1)
    
    if args.command == 'list':
        list_vehicles(api)
    elif args.command == 'status':
        status(api, args.id)
    elif args.command == 'lock':
        lock(api)
    elif args.command == 'unlock':
        unlock(api)
    elif args.command == 'honk':
        honk(api)
    elif args.command == 'flash':
        flash(api)
    elif args.command == 'climate':
        climate(api, args.temp)
    elif args.command == 'climate-on':
        climate_on(api)
    elif args.command == 'climate-off':
        climate_off(api)
    elif args.command == 'charge-start':
        start_charging(api)
    elif args.command == 'charge-stop':
        stop_charging(api)
    elif args.command == 'wake':
        wake(api)
    elif args.command == 'trunk':
        open_trunk(api, args.which)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
