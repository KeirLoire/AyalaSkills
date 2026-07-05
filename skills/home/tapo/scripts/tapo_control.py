import argparse
import asyncio
import json
import os
import socket
import sys
import warnings
from dotenv import load_dotenv, find_dotenv
from tapo import ApiClient

# Suppress unclosed client session warnings from aiohttp/python-kasa on exit
warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*")

# Load environment variables
load_dotenv(find_dotenv())

CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tapo_cache.json")
SUPPORTED_MODELS = ["p110", "l530", "l510", "p100", "p105", "p115", "p300"]

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_cache(cache):
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=2)
    except Exception:
        pass

def get_local_subnet():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 1))
        local_ip = s.getsockname()[0]
        s.close()
        parts = local_ip.split(".")
        if len(parts) == 4:
            return ".".join(parts[:3]) + "."
    except Exception:
        pass
    return "192.168.1."

async def check_port(ip, port=80, timeout=0.8):
    try:
        conn = asyncio.open_connection(ip, port)
        reader, writer = await asyncio.wait_for(conn, timeout=timeout)
        writer.close()
        await writer.wait_closed()
        return ip
    except Exception:
        return None

async def get_device_object(client, ip, cached_type=None):
    # If we have a cached device type, try that first to save time
    types_to_try = [cached_type] if cached_type else []
    types_to_try.extend([t for t in SUPPORTED_MODELS if t != cached_type])
    
    for model_type in types_to_try:
        try:
            device_method = getattr(client, model_type)
            device = await device_method(ip)
            # Try to fetch info to verify connection and auth
            await device.get_device_info()
            return device, model_type
        except Exception as e:
            # Raise if we hit an auth error so we know the device exists but lacks permissions
            if "Unauthorized" in str(e) or "Forbidden" in str(e):
                raise PermissionError(f"Unauthorized: Make sure 'Third-Party Compatibility' is enabled in the Tapo app for the device at {ip}.")
            continue
    raise ConnectionError(f"Could not establish connection to Tapo device at {ip}.")

async def get_device_by_alias(alias, username, password):
    client = ApiClient(username, password)
    cache = load_cache()
    
    # Direct IP address support
    parts = alias.split(".")
    if len(parts) == 4 and all(p.isdigit() for p in parts):
        try:
            device, model_type = await get_device_object(client, alias)
            return device, alias
        except Exception as e:
            print(f"Error: Failed to connect directly to IP {alias}. {e}", file=sys.stderr)
            sys.exit(1)
            
    cached_info = cache.get(alias)
    
    # 1. Try direct connection using cached IP
    if cached_info and "ip" in cached_info:
        cached_ip = cached_info["ip"]
        cached_type = cached_info.get("type")
        try:
            device, model_type = await get_device_object(client, cached_ip, cached_type)
            return device, cached_ip
        except PermissionError as pe:
            print(f"Error: {pe}", file=sys.stderr)
            sys.exit(1)
        except Exception:
            pass

    # 2. Sweep network if cache fails
    print(f"Scanning local network to discover '{alias}'...", file=sys.stderr)
    discovered = await discover_all_devices(username, password, silent=True)
    
    for d in discovered:
        if d["alias"].lower() == alias.lower():
            if d.get("unauthorized"):
                print(f"Error: Device '{alias}' found at {d['ip']} but connection was forbidden. Please enable 'Third-Party Compatibility' for this device in the Tapo app (Me > Third-Party Services).", file=sys.stderr)
                sys.exit(1)
            try:
                device, model_type = await get_device_object(client, d["ip"], d["type"])
                return device, d["ip"]
            except Exception:
                pass
                
    return None, None

async def discover_all_devices(username, password, silent=False):
    subnet = get_local_subnet()
    if not silent:
        print(f"Scanning local network ({subnet}0/24) on port 80...", file=sys.stderr)
        
    # Check port 80 on all 254 IPs concurrently
    tasks = [check_port(f"{subnet}{i}") for i in range(1, 255)]
    results = await asyncio.gather(*tasks)
    active_ips = [ip for ip in results if ip is not None]
    
    client = ApiClient(username, password)
    discovered = []
    cache = load_cache()
    
    async def query_ip(ip):
        try:
            # Try to connect and determine type
            device, model_type = await get_device_object(client, ip)
            info = await device.get_device_info()
            info_dict = info.to_dict()
            alias = info_dict.get("nickname", "Unknown")
            
            # Update cache
            cache[alias] = {"ip": ip, "type": model_type}
            return {
                "ip": ip,
                "alias": alias,
                "model": info_dict.get("model", "Unknown"),
                "is_on": info_dict.get("device_on", False),
                "type": model_type,
                "unauthorized": False
            }
        except PermissionError:
            # We detected a Tapo device but it's unauthorized
            return {
                "ip": ip,
                "alias": "Unauthorized (Need Third-Party Compatibility)",
                "model": "Tapo Device",
                "is_on": False,
                "type": "tapo",
                "unauthorized": True
            }
        except Exception:
            return None

    query_tasks = [query_ip(ip) for ip in active_ips]
    query_results = await asyncio.gather(*query_tasks)
    
    discovered = [d for d in query_results if d is not None]
    save_cache(cache)
    return discovered

async def main():
    parser = argparse.ArgumentParser(description="Control TP-Link Tapo smart devices by name.")
    parser.add_argument("device_name", nargs="?", help="Name (alias) of the device to control. Omit to list all devices.")
    parser.add_argument("action", nargs="?", choices=["on", "off", "status", "toggle"], help="Action to perform on the device.")
    
    args = parser.parse_args()
    
    username = os.getenv("TAPO_USERNAME")
    password = os.getenv("TAPO_PASSWORD")
    
    if not username or not password:
        print("Error: Please set TAPO_USERNAME and TAPO_PASSWORD in your environment (or .env file).", file=sys.stderr)
        sys.exit(1)
        
    # Default to discovery and listing
    if not args.device_name:
        devices = await discover_all_devices(username, password)
        if not devices:
            print("No Tapo devices found on the network.")
            return
            
        print("\nDiscovered Tapo Devices:")
        print(f"{'Alias / Name':<45} | {'Model':<10} | {'IP Address':<15} | {'State':<6}")
        print("-" * 85)
        for d in devices:
            state_str = "ON" if d["is_on"] else "OFF"
            if d["unauthorized"]:
                state_str = "LOCKED"
            print(f"{d['alias']:<45} | {d['model']:<10} | {d['ip']:<15} | {state_str:<6}")
        print("\nNote: If a device is marked 'Unauthorized', enable 'Third-Party Compatibility' in the Tapo app (Me > Third-Party Services).\n")
        return

    action = args.action or "status"
    
    dev, ip = await get_device_by_alias(args.device_name, username, password)
    if not dev:
        print(f"Error: Device '{args.device_name}' not found or unreachable on the network.", file=sys.stderr)
        sys.exit(1)
        
    info = await dev.get_device_info()
    info_dict = info.to_dict()
    alias = info_dict.get("nickname", args.device_name)
    model = info_dict.get("model", "Unknown")
    is_on = info_dict.get("device_on", False)
    
    if action == "on":
        print(f"Turning ON '{alias}' ({model} at {ip})...")
        await dev.on()
        print("Success: Device turned ON.")
    elif action == "off":
        print(f"Turning OFF '{alias}' ({model} at {ip})...")
        await dev.off()
        print("Success: Device turned OFF.")
    elif action == "toggle":
        if is_on:
            print(f"Toggling OFF '{alias}' ({model} at {ip})...")
            await dev.off()
            print("Success: Device turned OFF.")
        else:
            print(f"Toggling ON '{alias}' ({model} at {ip})...")
            await dev.on()
            print("Success: Device turned ON.")
    elif action == "status":
        print(f"\nStatus for '{alias}':")
        print(f"  Model:        {model}")
        print(f"  IP Address:   {ip}")
        print(f"  State:        {'ON' if is_on else 'OFF'}")
        
        # Check for energy monitoring if supported (P110/P115 etc.)
        if hasattr(dev, "get_current_power"):
            try:
                power = await dev.get_current_power()
                power_dict = power.to_dict()
                print(f"  Power Draw:   {power_dict.get('current_power', 0) / 1000.0:.2f} W")
            except Exception:
                pass
        print()

if __name__ == "__main__":
    asyncio.run(main())
