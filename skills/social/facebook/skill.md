# Facebook Messenger Control & Agent Bridge

This skill enables a Facebook Messenger chatbot to listen for commands in group chats and perform household automations, and provides a messaging bridge for other AI agents to communicate with the user.

## Purpose

1.  **Household Control**: To allow authorized family members to query and control smart home devices (like Tapo) directly from Facebook Messenger using strict or natural language commands.
2.  **Agent Communication**: To allow AI agents running on the local machine to send status notifications or prompt the user for input via Messenger.

---

## Prerequisites

1.  **Export Session Cookies**:
    - Unofficial Facebook APIs cannot log in via username/password due to Facebook's security algorithms. You must use session cookies.
    - Log in to Facebook in your browser.
    - Install a cookie exporter extension (such as **Cookie Editor** or **C3C UFC Utility**).
    - Open Facebook, click the extension, export the cookies in **JSON** format, and save the content to a file named `fb_cookies.json` inside the script directory:
      `skills/social/facebook/scripts/fb_cookies.json`.
2.  **Configurations**:
    - `TAPO_USERNAME` and `TAPO_PASSWORD` in the local `.env` file (for Tapo control).
    - `AUTHORIZED_FB_USERS`: List of comma-separated Facebook User IDs permitted to run commands.
    - `DEFAULT_FB_THREAD_ID`: The default group chat or thread ID used by the bot and CLI bridge.
    - `TAPO_ROOM_MAP` (Optional): Room to IP mapping for duplicate device names, e.g. `chester:192.168.1.18,garage:192.168.1.4`.

---

## Usage

### 1. Household Automation Bot (`fb_bot.py`)
This runs indefinitely in the background and responds to messages from authorized users:
```powershell
python fb_bot.py
```

**Commands available in chat (only for authorized users):**
- **Strict Commands**:
  - `!ping`: Returns a simple "Pong!" response.
  - `!list`: Scans the network and lists all Tapo devices and states.
  - `!on <device>` / `!off <device>` / `!toggle <device>`: Controls power state.
  - `!status <device>`: Checks detailed device status.
- **Natural Language Commands**:
  - *"turn on light at chester's room"* (turns on device mapped to Chester's room)
  - *"switch off light"* (turns off any light matched by alias)
  - *"check status of light"* (checks detailed device status)
- **Tag / Mention Responses**:
  - If you mention the bot name (e.g. *"hey bot"* or *"second-command"*), it will reply with a friendly help message.
- **Silent Ignoring**:
  - Normal, non-command messages that do not trigger the bot's name or direct device controls are ignored silently.

### 2. Agent Communication Bridge (`fb_message.py`)
Any AI coding agent running on the machine can execute this script to send notifications or poll for your input.

**Send a message to the user:**
```powershell
python fb_message.py send "Message from Agent: Build completed successfully!"
```

**Read the latest reply from the user:**
```powershell
python fb_message.py receive
```

**Send a message and block-wait for the user to reply:**
```powershell
python fb_message.py send "I encountered an error. Should I automatically fix it?"
python fb_message.py receive --wait
```
The `--wait` flag will poll the thread and output the first new reply sent by an authorized user after the script was launched.

---

## Edge Cases & Constraints

- **Session Expiration**: Facebook session cookies expire periodically. If the bot fails to connect or logs "Unauthorized/Forbidden", export a fresh `fb_cookies.json`.
- **E2EE Limitations**: Due to End-to-End Encryption (E2EE), the bot cannot read or reply to direct messages (one-to-one chats). It **must be used within Group Chats** or on Facebook Pages.
- **Account Protection**: Always use a secondary or dummy Facebook account for the bot to avoid risking your primary account.

---

## Checklist

- [ ] Is `fb_cookies.json` placed in the `scripts/` directory?
- [ ] Is your personal Facebook ID listed in `AUTHORIZED_FB_USERS` in `.env`?
- [ ] Is `DEFAULT_FB_THREAD_ID` set in `.env`?
- [ ] Does `python fb_message.py send "Test"` deliver a message successfully?
