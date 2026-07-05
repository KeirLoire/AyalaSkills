# Facebook Messenger Control

This skill enables a Facebook Messenger chatbot to listen for commands in group chats and perform household automations, such as controlling Tapo smart devices.

## Purpose

To allow authorized family members to query and control smart home devices directly from Facebook Messenger chats.

---

## Prerequisites

1.  **Export Session Cookies**:
    - Unofficial Facebook APIs cannot log in via username/password due to Facebook's security algorithms. You must use session cookies.
    - Log in to Facebook in your browser.
    - Install a cookie exporter extension (such as **Cookie Editor** or **C3C UFC Utility**).
    - Open Facebook, click the extension, export the cookies in **JSON** format, and save the content to a file named `fb_cookies.json` inside the script directory:
      `skills/social/facebook/scripts/fb_cookies.json`.
2.  **Authorized User IDs**:
    - To prevent strangers from controlling your home, obtain your personal Facebook User ID.
    - Add your ID to the `AUTHORIZED_FB_USERS` list in the local `.env` file (e.g. `AUTHORIZED_FB_USERS=10000213456789,10000876543210`).

---

## Inputs

1.  **Session Cookies**: A valid `fb_cookies.json` file in the script directory.
2.  **Configuration**: `AUTHORIZED_FB_USERS`, `KASA_USERNAME`, and `KASA_PASSWORD` set in the local `.env` file.

---

## Detailed Steps

1.  **Set Up the Environment**:
    - Ensure a Python virtual environment is activated and dependencies from `requirements.txt` are installed.
    - Place `fb_cookies.json` in the script directory.
2.  **Start the Bot**:
    - Run the command to start the bot listening:
      ```powershell
      python fb_bot.py
      ```
3.  **Use the Bot**:
    - Create a group chat in Messenger and add both your personal account and the bot's Facebook account.
    - Send commands (starting with `!`) in the chat from an authorized account.

---

## Chat Commands

Only messages from users listed in `AUTHORIZED_FB_USERS` will trigger actions.

*   **`!ping`**: Returns a simple "Pong!" response to verify the bot is online.
*   **`!list`**: Scans the local network and lists all active Tapo devices and their current states.
*   **`!on <IP_or_Alias>`**: Turns on a specific Tapo device (e.g. `!on 192.168.1.18` or `!on Living Room Plug`).
*   **`!off <IP_or_Alias>`**: Turns off a specific Tapo device.
*   **`!toggle <IP_or_Alias>`**: Toggles the power state of a Tapo device.

---

## Edge Cases & Constraints

- **Session Expiration**: Facebook session cookies expire periodically or when you manually log out of that browser session. If the bot fails to connect or logs "Unauthorized/Forbidden", export a fresh `fb_cookies.json`.
- **Account Block Warning**: Using automated bots on personal Facebook accounts violates Facebook's Terms of Service. Always use a secondary/dummy account for the bot.
- **E2EE Limitations**: Due to End-to-End Encryption (E2EE), the bot cannot read or reply to direct messages (one-to-one chats) with other users. It **must be used within Group Chats**, Room Chats, or on Facebook Pages.

---

## Checklist

- [ ] Is `fb_cookies.json` placed in the `scripts/` directory?
- [ ] Is your personal Facebook ID listed in `AUTHORIZED_FB_USERS` in `.env`?
- [ ] Are Tapo credentials set correctly in `.env`?
- [ ] Does the bot successfully connect and respond to `!ping` in a group chat?
