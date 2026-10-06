#!/usr/bin/env python3
"""
clay-tesla - Tesla Vehicle Control CLI
Control your Tesla from the command line using the Tesla API.
"""

import argparse
import asyncio
import json
import os
import sys
import aiohttp
from pathlib import Path
import getpass

# Try to import teslajsonpy
try:
    from teslajsonpy.controller import Controller
    from teslajsonpy import TeslaCar
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


async def authenticate_async(email, password):
    """Authenticate with Tesla API and save tokens."""
    print(f"Authenticating with Tesla API for {email}...")
    try:
        async with aiohttp.ClientSession() as session:
            controller = Controller(session)
            await controller.async_login(email, password)
            
            # Save tokens
            tokens = {
                'access_token': controller.access_token,
                'refresh_token': controller.refresh_token,
                'expiration': controller.token_expiration
            }
            save_tokens(tokens)
            
            # Get vehicles
            await controller.async_get_vehicles()
            
            print("✅ Authentication successful! Tokens saved.")
            return controller
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None


def get_controller():
    """Get authenticated Tesla Controller instance."""
    tokens = load_tokens()
    if not tokens:
        print("❌ Not authenticated. Run: clay_tesla.py auth <email>")
        print("   (Password will be prompted securely)")
        return None
    
    try:
        async def run():
            async with aiohttp.ClientSession() as session:
                controller = Controller(session)
                controller.access_token = tokens.get('access_token')
                controller.refresh_token = tokens.get('refresh_token')
                controller.token_expiration = tokens.get('expiration', 0)
                
                # Test and refresh if needed
                await controller.async_get_vehicles()
                return controller
        
        return asyncio.run(run())
    except Exception as e:
        print(f"❌ Error connecting to Tesla API: {e}")
        print("   Try re-authenticating with: clay_tesla.py auth <email>")
        return None


def list_vehicles(controller):
    """List all vehicles associated with the account."""
    try:
        vehicles = controller.cars
        print(f"\n🚗 Your Tesla Vehicles:")
        print("-" * 50)
        for i, v in enumerate(vehicles):
            print(f"  {i+1}. {v.display_name}")
            print(f"      VIN: {v.vin[-6:]}")
            print(f"      ID: {v.vin}")
        print("-" * 50)
        return vehicles
    except Exception as e:
        print(f"❌ Error listing vehicles: {e}")
        return []


def get_status(controller):
    """Get vehicle status."""
    try:
        vehicles = controller.cars
        if not vehicles:
            print("❌ No vehicles found")
            return
        
        vehicle = vehicles[0]
        
        print(f"\n🚗 {vehicle.display_name} Status")
        print("=" * 50)
        
        # Charge state
        print(f"🔋 Battery: {vehicle.battery_level}%")
        print(f"   Charging: {vehicle.charging_state}")
        print(f"   Range: {vehicle.battery_range} miles")
        print(f"   Charge Limit: {vehicle.charge_limit_soc}%")
        
        # Climate
        print(f"🌡️ Climate:")
        print(f"   Cabin Temp: {vehicle.driver_temp_setting}°F")
        print(f"   Outside Temp: {vehicle.outside_temp}°F")
        print(f"   Climate On: {vehicle.is_climate_on}")
        
        # Location
        print(f"📍 Location:")
        print(f"   Shift State: {vehicle.shift_state or 'Parked'}")
        print(f"   Speed: {vehicle.speed} mph")
        if vehicle.latitude and vehicle.longitude:
            print(f"   Coordinates: {vehicle.latitude}, {vehicle.longitude}")
        
        # Vehicle state
        print(f"🚙 Vehicle:")
        print(f"   Locked: {vehicle.locked}")
        print(f"   Frunk Open: {vehicle.frunk_open}")
        print(f"   Trunk Open: {vehicle.trunk_open}")
        print(f"   Windows Open: {vehicle.windows_open}")
        print(f"   Sentry Mode: {vehicle.sentry_mode}")
        
        # Software
        print(f"💾 Software: {vehicle.car_version}")
        
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error getting status: {e}")


async def honk_async(controller):
    """Honk the horn."""
    try:
        vehicle = controller.cars[0]
        await vehicle.async_honk()
        print("📢 Honk! Honk! 🔊")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def flash_async(controller):
    """Flash the lights."""
    try:
        vehicle = controller.cars[0]
        await vehicle.async_flash_lights()
        print("💡 Lights flashed!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def lock_async(controller, lock=True):
    """Lock or unlock the vehicle."""
    try:
        vehicle = controller.cars[0]
        if lock:
            await vehicle.async_lock()
            print("🔒 Vehicle locked!")
        else:
            await vehicle.async_unlock()
            print("🔓 Vehicle unlocked!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def climate_async(controller, temp):
    """Set climate temperature."""
    try:
        vehicle = controller.cars[0]
        await vehicle.async_set_temps(temp, temp)
        print(f"🌡️ Climate set to {temp}°F!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def climate_on_async(controller):
    """Turn on climate control."""
    try:
        vehicle = controller.cars[0]
        await vehicle.async_set_climate_state(on=True)
        print("🌡️ Climate control ON!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def climate_off_async(controller):
    """Turn off climate control."""
    try:
        vehicle = controller.cars[0]
        await vehicle.async_set_climate_state(on=False)
        print("🌡️ Climate control OFF!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def charge_async(controller, start=True):
    """Start or stop charging."""
    try:
        vehicle = controller.cars[0]
        if start:
            await vehicle.async_start_charging()
            print("🔌 Charging started!")
        else:
            await vehicle.async_stop_charging()
            print("🔌 Charging stopped!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def wake_async(controller):
    """Wake up the vehicle."""
    try:
        vehicle = controller.cars[0]
        await vehicle.async_wake_up()
        print("☀️ Vehicle waking up...")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def trunk_async(controller, which="rear"):
    """Open trunk or frunk."""
    try:
        vehicle = controller.cars[0]
        if which == "frunk":
            await vehicle.async_actuate_trunk(0)
            print("👜 Frunk opening...")
        else:
            await vehicle.async_actuate_trunk(1)
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
  clay_tesla.py auth email@example.com    Authenticate with Tesla
  clay_tesla.py list                     List your vehicles
  clay_tesla.py status                  Get vehicle status
  clay_tesla.py lock                    Lock the car
  clay_tesla.py unlock                  Unlock the car
  clay_tesla.py climate 72              Set temp to 72F
  clay_tesla.py climate-on              Turn on climate
  clay_tesla.py honk                    Honk the horn
  clay_tesla.py flash                   Flash lights
  clay_tesla.py charge-start            Start charging
  clay_tesla.py wake                    Wake up vehicle
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Auth
    auth_parser = subparsers.add_parser('auth', help='Authenticate with Tesla')
    auth_parser.add_argument('email', nargs='?', help='Tesla account email')
    
    # List vehicles
    subparsers.add_parser('list', help='List all vehicles')
    
    # Status
    subparsers.add_parser('status', help='Get vehicle status')
    
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
    
    # Handle auth command
    if args.command == 'auth':
        if not args.email:
            email = input("Tesla email: ")
        else:
            email = args.email
        
        password = getpass.getpass("Tesla password: ")
        
        controller = asyncio.run(authenticate_async(email, password))
        sys.exit(0 if controller else 1)
    
    # Get controller for other commands
    controller = get_controller()
    if not controller and args.command not in ['auth']:
        sys.exit(1)
    
    # Execute commands
    if args.command == 'list':
        list_vehicles(controller)
    elif args.command == 'status':
        get_status(controller)
    elif args.command == 'lock':
        asyncio.run(lock_async(controller, lock=True))
    elif args.command == 'unlock':
        asyncio.run(lock_async(controller, lock=False))
    elif args.command == 'honk':
        asyncio.run(honk_async(controller))
    elif args.command == 'flash':
        asyncio.run(flash_async(controller))
    elif args.command == 'climate':
        asyncio.run(climate_async(controller, args.temp))
    elif args.command == 'climate-on':
        asyncio.run(climate_on_async(controller))
    elif args.command == 'climate-off':
        asyncio.run(climate_off_async(controller))
    elif args.command == 'charge-start':
        asyncio.run(charge_async(controller, start=True))
    elif args.command == 'charge-stop':
        asyncio.run(charge_async(controller, start=False))
    elif args.command == 'wake':
        asyncio.run(wake_async(controller))
    elif args.command == 'trunk':
        asyncio.run(trunk_async(controller, args.which))
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
