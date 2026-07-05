import sys
import os
import asyncio
from fbchat_muqit import Client, Message, EventType
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

# Add the Tapo scripts path to sys.path to reuse its control functions
TAPO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "home", "tapo", "scripts"))
sys.path.append(TAPO_PATH)

try:
    from tapo_control import get_device_by_alias, discover_all_devices
except ImportError:
    # Fallback to dummy functions if Tapo skill is not present
    get_device_by_alias = None
    discover_all_devices = None

# Load authorized users
AUTH_USERS_RAW = os.getenv("AUTHORIZED_FB_USERS", "")
AUTHORIZED_USERS = [uid.strip() for uid in AUTH_USERS_RAW.split(",") if uid.strip()]

# Load Tapo credentials
TAPO_USER = os.getenv("TAPO_USERNAME")
TAPO_PASS = os.getenv("TAPO_PASSWORD")

COOKIES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fb_cookies.json")

if not os.path.exists(COOKIES_PATH):
    print(f"Error: fb_cookies.json not found at {COOKIES_PATH}.", file=sys.stderr)
    print("Please export your Facebook session cookies to this file to start the bot.", file=sys.stderr)
    # Don't exit immediately so the syntax check still works during validation, but prevent run
    client = None
else:
    client = Client(cookies_file_path=COOKIES_PATH)

if client:
    @client.event
    async def on_message(message: Message):
        # Ignore messages sent by the bot itself
        if message.sender_id == client.uid:
            return
            
        text = message.text or ""
        if not text.startswith("!"):
            return
            
        # Check authorization
        if message.sender_id not in AUTHORIZED_USERS:
            print(f"Unauthorized command attempt from user ID {message.sender_id}: {text}")
            await client.send_message("Unauthorized: You are not permitted to control this bot.", message.thread_id)
            return
            
        print(f"Command received from {message.sender_id}: {text}")
        parts = text[1:].strip().split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if command == "ping":
            await client.send_message("Pong! 🏡 Bot is online and listening.", message.thread_id)
            
        elif command == "list":
            if not discover_all_devices or not TAPO_USER or not TAPO_PASS:
                await client.send_message("Tapo integration is not loaded or configured.", message.thread_id)
                return
                
            await client.send_message("Scanning local network for Tapo devices... 🔍", message.thread_id)
            try:
                devices = await discover_all_devices(TAPO_USER, TAPO_PASS, silent=True)
                if not devices:
                    await client.send_message("No Tapo devices found on the local network.", message.thread_id)
                    return
                    
                response = "Discovered Tapo Devices:\n"
                for d in devices:
                    state_str = "ON" if d["is_on"] else "OFF"
                    if d["unauthorized"]:
                        state_str = "LOCKED (Need Third-Party Compatibility)"
                    response += f"• {d['alias']} ({d['model']}): {state_str} at {d['ip']}\n"
                await client.send_message(response.strip(), message.thread_id)
            except Exception as e:
                await client.send_message(f"Error scanning network: {str(e)}", message.thread_id)
                
        elif command in ["on", "off", "toggle", "status"]:
            if not get_device_by_alias or not TAPO_USER or not TAPO_PASS:
                await client.send_message("Tapo integration is not loaded or configured.", message.thread_id)
                return
                
            if not args:
                await client.send_message(f"Please specify a device name or IP, e.g. !{command} Living Room Plug", message.thread_id)
                return
                
            await client.send_message(f"Contacting device '{args}'...", message.thread_id)
            try:
                dev, ip = await get_device_by_alias(args, TAPO_USER, TAPO_PASS)
                if not dev:
                    await client.send_message(f"Device '{args}' not found on the local network.", message.thread_id)
                    return
                    
                info = await dev.get_device_info()
                info_dict = info.to_dict()
                alias = info_dict.get("nickname", args)
                model = info_dict.get("model", "Unknown")
                is_on = info_dict.get("device_on", False)
                
                if command == "on":
                    await dev.on()
                    await client.send_message(f"Success: Turned ON '{alias}' ({model}).", message.thread_id)
                elif command == "off":
                    await dev.off()
                    await client.send_message(f"Success: Turned OFF '{alias}' ({model}).", message.thread_id)
                elif command == "toggle":
                    if is_on:
                        await dev.off()
                        await client.send_message(f"Success: Toggled OFF '{alias}' ({model}).", message.thread_id)
                    else:
                        await dev.on()
                        await client.send_message(f"Success: Toggled ON '{alias}' ({model}).", message.thread_id)
                elif command == "status":
                    state_str = "ON" if is_on else "OFF"
                    response = f"Device Status for '{alias}':\n• Model: {model}\n• IP: {ip}\n• State: {state_str}"
                    if hasattr(dev, "get_current_power"):
                        try:
                            power = await dev.get_current_power()
                            power_dict = power.to_dict()
                            response += f"\n• Power Draw: {power_dict.get('current_power', 0) / 1000.0:.2f} W"
                        except Exception:
                            pass
                    await client.send_message(response, message.thread_id)
            except Exception as e:
                await client.send_message(f"Error controlling device: {str(e)}", message.thread_id)
                
        else:
            await client.send_message(f"Unknown command: !{command}. Try !ping, !list, !on, !off, !toggle, or !status.", message.thread_id)

def start_bot():
    if not client:
        print("Could not start bot. Ensure fb_cookies.json is present.", file=sys.stderr)
        return
    print("Starting Facebook Messenger Bot...")
    print(f"Authorized users: {AUTHORIZED_USERS}")
    client.run()

if __name__ == "__main__":
    start_bot()
