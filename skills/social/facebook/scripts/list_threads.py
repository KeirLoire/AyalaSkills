import asyncio
import os
import sys
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from fbchat_muqit import Client
except ImportError:
    print("Error: fbchat-muqit not found.", file=sys.stderr)
    sys.exit(1)

import json

COOKIES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fb_cookies.json")

# Write session cookies from env to file if configured
FB_COOKIES_ENV = os.getenv("FB_COOKIES", "")
if FB_COOKIES_ENV:
    try:
        cookies_data = json.loads(FB_COOKIES_ENV)
        with open(COOKIES_PATH, "w", encoding="utf-8") as f:
            json.dump(cookies_data, f, indent=4)
    except Exception as e:
        print(f"Warning: Failed to parse FB_COOKIES env variable in list_threads: {e}", file=sys.stderr)

async def list_threads():
    if not os.path.exists(COOKIES_PATH):
        print(f"Error: Cookies file not found at {COOKIES_PATH} and FB_COOKIES env variable is not configured.", file=sys.stderr)
        return
        
    client = Client(cookies_file_path=COOKIES_PATH)
    await client.start()
    try:
        print("\nFetching active Messenger threads for the bot account...")
        threads = await client.fetch_thread_list(limit=15)
        if not threads:
            print("No active threads found.")
            return
            
        print(f"\n{'Thread Name / Alias':<40} | {'Thread ID':<20} | {'Type':<10}")
        print("-" * 76)
        for thread in threads:
            name = thread.name or "Unnamed Thread"
            print(f"{name:<40} | {thread.thread_id:<20} | {thread.thread_type.name:<10}")
            
    except Exception as e:
        print(f"Error fetching threads: {e}", file=sys.stderr)
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(list_threads())
