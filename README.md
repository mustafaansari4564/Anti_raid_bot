# Discord Role-Control Bot

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Create your `.env` file
Copy `.env.example` → `.env` and fill in your values:

| Key | Where to get it |
|-----|----------------|
| `DISCORD_TOKEN` | [Discord Developer Portal](https://discord.com/developers/applications) → Your App → Bot → Token |
| `GUILD_ID` | Right-click your server icon → **Copy Server ID** |
| `ROLE_ID` | Server Settings → Roles → right-click the role → **Copy Role ID** |

> **Enable Developer Mode:** User Settings → Advanced → Developer Mode ✓

### 3. Required Bot Permissions
When inviting the bot, make sure it has:
- **Manage Roles** — to add/remove roles and edit role permissions
- **Manage Channels** — to set per-channel overwrites during `!burn`
- **Read Messages / View Channels**

> ⚠️ The bot's own role must be **higher** than the target role in the role hierarchy.

### 4. Required Privileged Intents
In the Developer Portal → Your App → Bot, enable:
- ✅ **Server Members Intent**
- ✅ **Message Content Intent**

### 5. Run the bot
```bash
python bot.py
```

---

## Commands (admin-only, silently ignored for others)

| Command | What it does |
|---------|-------------|
| `!burn` | Strips **all** permissions from the target role AND adds explicit deny overwrites on every channel — members can't chat, read, react, join/speak in VC, nothing. Permissions are saved so `!unburn` can restore them. |
| `!unburn` | Restores the role's original permissions and removes all channel overwrites added by `!burn`. |
| `!kill` | Removes the target role from **every** member who currently has it. Saves the list so `!revive` can undo this. |
| `!revive` | Re-adds the target role to every member affected by the last `!kill`. Members who left the server are skipped. |

## Auto-role on join
Every new member who joins the server automatically receives the configured role.

## State persistence
`!kill`/`!revive` and `!burn`/`!unburn` state is saved to `data.json` in the same directory.
This means the bot survives restarts without losing track of who was killed or what permissions were saved.
