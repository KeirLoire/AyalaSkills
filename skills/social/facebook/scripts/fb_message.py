import argparse
import asyncio
import os
import sys
import time
import warnings
from dotenv import load_dotenv, find_dotenv

# Set Windows asyncio SelectorEventLoop policy for Windows compatibility
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Suppress unclosed client session warnings from aiohttp/python-kasa on exit
warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*")

# Load environment variables
load_dotenv(find_dotenv())

# Add path so fbchat_muqit is found if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from fbchat_muqit import Client
except ImportError:
    print("Error: fbchat-muqit library is not installed in this environment.", file=sys.stderr)
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
        print(f"Warning: Failed to parse FB_COOKIES env variable in fb_message: {e}", file=sys.stderr)

DEFAULT_THREAD_ID = os.getenv("DEFAULT_FB_THREAD_ID")
AUTH_USERS_RAW = os.getenv("AUTHORIZED_FB_USERS", "")
AUTHORIZED_USERS = [uid.strip() for uid in AUTH_USERS_RAW.split(",") if uid.strip()]

async def send_message_async(text, thread_id):
    if not os.path.exists(COOKIES_PATH):
        print(f"Error: Cookies file not found at {COOKIES_PATH} and FB_COOKIES env variable is not configured.", file=sys.stderr)
        sys.exit(1)
        
    client = Client(cookies_file_path=COOKIES_PATH)
    await client.start()
    await client.start_listening()
    try:
        await client.send_message(text, thread_id)
        print(f"SUCCESS: Message sent to thread {thread_id}")
    except Exception as e:
        print(f"ERROR: Failed to send message: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        await client.stop_listening()
        await client.close()

async def receive_message_async(thread_id, wait_for_new, poll_interval=2):
    if not os.path.exists(COOKIES_PATH):
        print(f"Error: fb_cookies.json not found at {COOKIES_PATH}.", file=sys.stderr)
        sys.exit(1)
        
    start_time_ms = int(time.time() * 1000)
    client = Client(cookies_file_path=COOKIES_PATH)
    await client.start()
    
    try:
        if wait_for_new:
            print(f"Polling for new authorized message on thread {thread_id}...", file=sys.stderr)
            while True:
                messages = await client.fetch_thread_messages(thread_id, message_limit=5)
                # Messages are usually returned in reverse chronological order (newest first)
                for msg in messages:
                    # check if sender is authorized and message timestamp is after script start
                    if msg.sender_id in AUTHORIZED_USERS and msg.timestamp > start_time_ms:
                        print(msg.text)
                        return
                await asyncio.sleep(poll_interval)
        else:
            messages = await client.fetch_thread_messages(thread_id, message_limit=10)
            for msg in messages:
                if msg.sender_id in AUTHORIZED_USERS:
                    print(msg.text)
                    return
            print("No recent authorized messages found.", file=sys.stderr)
    except Exception as e:
        print(f"ERROR: Failed to fetch messages: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        await client.close()

def main():
    parser = argparse.ArgumentParser(description="CLI Bridge for AI agents to send and receive messages on Facebook Messenger.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Send subcommand
    send_parser = subparsers.add_parser("send", help="Send a message to the Messenger thread.")
    send_parser.add_argument("text", help="The message content to send.")
    send_parser.add_argument("--thread-id", default=DEFAULT_THREAD_ID, help="Messenger thread ID. Defaults to DEFAULT_FB_THREAD_ID.")
    
    # Receive subcommand
    receive_parser = subparsers.add_parser("receive", help="Retrieve the latest message from an authorized user.")
    receive_parser.add_argument("--thread-id", default=DEFAULT_THREAD_ID, help="Messenger thread ID. Defaults to DEFAULT_FB_THREAD_ID.")
    receive_parser.add_argument("--wait", action="store_true", help="Block and wait for a new incoming message from an authorized user.")
    
    args = parser.parse_args()
    
    thread_id = args.thread_id
    if not thread_id:
        print("Error: Thread ID must be specified via --thread-id or DEFAULT_FB_THREAD_ID in environment.", file=sys.stderr)
        sys.exit(1)
        
    if args.command == "send":
        asyncio.run(send_message_async(args.text, thread_id))
    elif args.command == "receive":
        asyncio.run(receive_message_async(thread_id, args.wait))

if __name__ == "__main__":
    main()
