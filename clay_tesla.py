#!/usr/bin/env python3
"""
clay-tesla - Tesla CLI control tool

Control your Tesla Model 3 via command line using the Tesla API.

Usage:
    python3 clay_tesla.py status              # Get vehicle status
    python3 clay_tesla.py climate 72         # Set climate to 72F
    python3 clay_tesla.py lock               # Lock the car
    python3 clay_tesla.py unlock             # Unlock the car
    python3 clay_tesla.py honk               # Honk the horn
    python3 clay_tesla.py flash              # Flash lights
    python3 clay_tesla.py start              # Start remote control
    python3 clay_tesla.py stop               # Stop remote control
    python3 clay_tesla.py open frunk         # Open frunk
    python3 clay_tesla.py open trunk         # Open trunk
    python3 clay_tesla.py charge 80          # Set charge limit %
    python3 clay_tesla.py wake               # Wake up the car
    python3 clay_tesla.py where             # Get location

Requirements:
    pip install teslajsonpy

Setup:
    Set environment variables:
        TESLA_EMAIL - your Tesla account email
        TESLA_TOKEN - your Tesla refresh token
    Or pass --email and --token flags
"""

import os
import sys
import argparse
import json
from datetime import datetime

try:
    import teslajsonpy
except ImportError:
    print("ERROR: teslajsonpy not installed.")
    print("Install with: pip install teslajsonpy")
    sys.exit(1)


class TeslaController:
    def __init__(self, email: str = None, token: str = None):
        self.email = email or os.environ.get('TESLA_EMAIL')
        self.token = token or os.environ.get('TESLA_TOKEN')
        
        if not self.email or not self.token:
            raise ValueError("Tesla email and token required. Set TESLA_EMAIL and TESLA_TOKEN env vars or use --email and --token flags.")
        
        self.controller = teslajsonpy.Controller()
        self.controller.api_login(self.email, self.token)
        self.vehicles = self.controller.api('vehicles')['response']
        
        if not self.vehicles:
            raise ValueError("No vehicles found linked to this Tesla account.")
        
        # Use the first vehicle (Robb's Model 3)
        self.vehicle = self.vehicles[0]
        self.vin = self.vehicle['vin']
        
    def get_vehicle(self):
        """Get full vehicle data"""
        return self.controller.api(f'vehicles/{self.vin}/vehicle_data')['response']
    
    def wake(self):
        """Wake up the vehicle"""
        result = self.controller.api(f'vehicles/{self.vin}/wake_up')['response']
        return result
    
    def status(self, verbose: bool = False):
        """Get vehicle status"""
        data = self.get_vehicle()
        
        # Extract key info
        state = data.get('vehicle_state', {})
        charge = data.get('charge_state', {})
        climate = data.get('climate_state', {})
        drive = data.get('drive_state', {})
        loc = data.get('drive_state', {}).get('gps_as_of', 0)
        
        result = {
            'name': self.vehicle['display_name'],
            'state': data.get('state', 'unknown'),
            'locked': state.get('locked', True),
            'frunk_open': state.get('front_trunk_open', False),
            'rear_trunk_open': state.get('rear_trunk_open', False),
            'windows_open': any(state.get('windows_state', {}).values()) if state.get('windows_state') else False,
            'sentry_mode': state.get('sentry_mode', False),
            ' battery': charge.get('battery_level', 0),
            'charging': charge.get('charging_state', 'Disconnected'),
            'charge_limit': charge.get('charge_limit_soc', 100),
            'range_miles': charge.get('est_battery_range', 0),
            'temp_outside': climate.get('outside_temp', 0),
            'temp_cabin': climate.get('cabin_temp', 0),
            'driver_temp': climate.get('driver_temp_setting', 0),
            'passenger_temp': climate.get('passenger_temp_setting', 0),
            'climate_on': climate.get('is_climate_on', False),
        }
        
        if verbose:
            result.update({
                'speed': drive.get('speed', 0),
                'heading': drive.get('heading', 0),
                'shift_state': drive.get('shift_state', 'P'),
                'location': f"{drive.get('latitude', 0)}, {drive.get('longitude', 0)}" if drive.get('latitude') else "Unknown",
            })
        
        return result
    
    def lock(self):
        """Lock the vehicle"""
        return self.controller.api(f'vehicles/{self.vin}/command/doors', {'lock': True})['response']
    
    def unlock(self):
        """Unlock the vehicle"""
        return self.controller.api(f'vehicles/{self.vin}/command/doors', {'lock': False})['response']
    
    def honk(self):
        """Honk the horn"""
        return self.controller.api(f'vehicles/{self.vin}/command/honk_horn')['response']
    
    def flash(self):
        """Flash the lights"""
        return self.controller.api(f'vehicles/{self.vin}/command/flash_lights')['response']
    
    def climate(self, temp: float):
        """Set climate temperature"""
        return self.controller.api(f'vehicles/{self.vin}/command/set_temps', {
            'driver_temp': temp,
            'passenger_temp': temp
        })['response']
    
    def start_climate(self):
        """Start climate control"""
        return self.controller.api(f'vehicles/{self.vin}/command/auto_conditioning_start')['response']
    
    def stop_climate(self):
        """Stop climate control"""
        return self.controller.api(f'vehicles/{self.vin}/command/auto_conditioning_stop')['response']
    
    def start(self):
        """Start remote control (allows driving)"""
        return self.controller.api(f'vehicles/{self.vin}/command/remote_start', {'password': ''})['response']
    
    def stop(self):
        """Stop remote control"""
        # Actually this just locks after valet mode
        return self.controller.api(f'vehicles/{self.vin}/command/door_lock', {'lock': True})['response']
    
    def open_trunk(self, which: str = 'rear'):
        """Open trunk or frunk"""
        if which == 'frunk' or which == 'front':
            return self.controller.api(f'vehicles/{self.vin}/command/trunk', {'which_trunk': 'front'})['response']
        else:
            return self.controller.api(f'vehicles/{self.vin}/command/trunk', {'which_trunk': 'rear'})['response']
    
    def charge_limit(self, percent: int):
        """Set charge limit (0-100)"""
        percent = max(0, min(100, percent))
        return self.controller.api(f'vehicles/{self.vin}/command/set_charge_limit', {'percent': percent})['response']
    
    def start_charging(self):
        """Start charging"""
        return self.controller.api(f'vehicles/{self.vin}/command/charge_start')['response']
    
    def stop_charging(self):
        """Stop charging"""
        return self.controller.api(f'vehicles/{self.vin}/command/charge_stop')['response']
    
    def where(self):
        """Get vehicle location"""
        data = self.get_vehicle()
        drive = data.get('drive_state', {})
        
        return {
            'latitude': drive.get('latitude'),
            'longitude': drive.get('longitude'),
            'heading': drive.get('heading'),
            'speed': drive.get('speed'),
            'gps_as_of': drive.get('gps_as_of')
        }


def format_status(status: dict, verbose: bool = False) -> str:
    """Format status for display"""
    lines = [
        f"🚗 {status['name']}",
        f"   State: {status['state']}",
        f"   🔒 Locked: {'Yes' if status['locked'] else 'No'}",
        f"   🔋 Battery: {status.get(' battery', 0)}% ({status.get('range_miles', 0)} mi)",
        f"   ⚡ Charging: {status['charging']}",
        f"   🌡️ Cabin: {status.get('temp_cabin', 0)}°F (outside {status.get('temp_outside', 0)}°F)",
        f"   🪟 Windows: {'Open' if status['windows_open'] else 'Closed'}",
        f"   👁️ Sentry: {'On' if status['sentry_mode'] else 'Off'}",
    ]
    
    if verbose:
        lines.extend([
            f"   📍 Location: {status.get('location', 'Unknown')}",
            f"   🛞 Speed: {status.get('speed', 0)} mph",
            f"   ⚙️ Gear: {status.get('shift_state', 'P')}",
        ])
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Clay Tesla Control')
    parser.add_argument('--email', '-e', help='Tesla account email')
    parser.add_argument('--token', '-t', help='Tesla refresh token')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--json', '-j', action='store_true', help='JSON output')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # status
    subparsers.add_parser('status', help='Get vehicle status')
    
    # wake
    subparsers.add_parser('wake', help='Wake up the vehicle')
    
    # lock/unlock
    subparsers.add_parser('lock', help='Lock the vehicle')
    subparsers.add_parser('unlock', help='Unlock the vehicle')
    
    # honk/flash
    subparsers.add_parser('honk', help='Honk the horn')
    subparsers.add_parser('flash', help='Flash the lights')
    
    # climate
    climate_parser = subparsers.add_parser('climate', help='Set climate temperature')
    climate_parser.add_argument('temp', type=float, help='Temperature in F')
    
    # start/stop climate
    subparsers.add_parser('start', help='Start remote control')
    subparsers.add_parser('stop', help='Stop remote control')
    subparsers.add_parser('start-climate', help='Start climate control')
    subparsers.add_parser('stop-climate', help='Stop climate control')
    
    # charge
    charge_parser = subparsers.add_parser('charge', help='Set charge limit')
    charge_parser.add_argument('percent', type=int, help='Charge limit (0-100)')
    
    # open
    open_parser = subparsers.add_parser('open', help='Open trunk/frunk')
    open_parser.add_argument('which', choices=['trunk', 'frunk', 'rear', 'front'], default='trunk')
    
    # where
    subparsers.add_parser('where', help='Get vehicle location')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        controller = TeslaController(args.email, args.token)
        
        if args.command == 'status':
            status = controller.status(verbose=args.verbose)
            if args.json:
                print(json.dumps(status, indent=2))
            else:
                print(format_status(status, verbose=args.verbose))
                
        elif args.command == 'wake':
            result = controller.wake()
            print(f"🚗 Waking up... State: {result.get('state')}")
            
        elif args.command == 'lock':
            result = controller.lock()
            print(f"🔒 Locked: {result.get('response', {}).get('locked', result)}")
            
        elif args.command == 'unlock':
            result = controller.unlock()
            print(f"🔓 Unlocked: {not result.get('response', {}).get('locked', not result)}")
            
        elif args.command == 'honk':
            result = controller.honk()
            print(f"📢 Honked: {result.get('response', {}).get('honk', result)}")
            
        elif args.command == 'flash':
            result = controller.flash()
            print(f"💡 Flashed: {result.get('response', {}).get('lights', result)}")
            
        elif args.command == 'climate':
            result = controller.climate(args.temp)
            print(f"🌡️ Climate set to {args.temp}°F")
            
        elif args.command == 'start':
            result = controller.start()
            print(f"▶️ Remote start: {result}")
            
        elif args.command == 'stop':
            result = controller.stop()
            print(f"⏹️ Remote stop: {result}")
            
        elif args.command == 'start-climate':
            result = controller.start_climate()
            print(f"🌡️ Climate started: {result.get('response', result)}")
            
        elif args.command == 'stop-climate':
            result = controller.stop_climate()
            print(f"🌡️ Climate stopped: {result.get('response', result)}")
            
        elif args.command == 'charge':
            result = controller.charge_limit(args.percent)
            print(f"🔋 Charge limit set to {args.percent}%")
            
        elif args.command == 'open':
            which = args.which
            if which in ['front', 'frunk']:
                result = controller.open_trunk('front')
                print(f"👜 Frunk opened: {result.get('response', result)}")
            else:
                result = controller.open_trunk('rear')
                print(f"📦 Trunk opened: {result.get('response', result)}")
                
        elif args.command == 'where':
            loc = controller.where()
            if args.json:
                print(json.dumps(loc, indent=2))
            else:
                print(f"📍 Location: {loc.get('latitude', 0)}, {loc.get('longitude', 0)}")
                print(f"   Heading: {loc.get('heading', 0)}° | Speed: {loc.get('speed', 0)} mph")
                
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
