# 🤖 Anti_raid_bot

A Discord bot that automatically assigns a temporary **"NC" (new-member)** role to newly joined members and expires it automatically after a set period.

---

## ✨ Features

- 🆕 **Auto-Role on Join** — Assigns the NC role to every new member automatically
- ⏳ **Auto-Expiry** — Removes the NC role once its tracked duration is up
- 💾 **Reliable Expiry Tracking** — Tracks expiry in a local `data.json` file rather than relying on Discord's `joined_at` timestamp, so tracking survives bot restarts
- 🛡️ **Membership Screening Support** — Correctly pre-assigns the role before Discord's normal join events fire, even when Membership Screening is enabled
- 📋 **Activity Logging** — Logs every role assignment/removal to a dedicated log channel

---

## Commands (admin-only, silently ignored for others)

| Command | What it does |
|---------|-------------|
| `!burn` | Strips **all** permissions from the target role AND adds explicit deny overwrites on every channel — members can't chat, read, react, join/speak in VC, nothing. Permissions are saved so `!unburn` can restore them. |
| `!unburn` | Restores the role's original permissions and removes all channel overwrites added by `!burn`. |
| `!kill` | Removes the target role from **every** member who currently has it. Saves the list so `!revive` can undo this. |
| `!revive` | Re-adds the target role to every member affected by the last `!kill`. Members who left the server are skipped. |


---

## 🛠️ Tech Stack

| Service | Purpose |
|---|---|
| [discord.py](https://discordpy.readthedocs.io/) | Discord bot framework |
| `data.json` | Local storage for NC role expiry tracking |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | Environment variable management |


---

## 📋 Prerequisites

- Python 3.11+
- Discord Bot Token

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create `.env` file
```env
DISCORD_TOKEN=your_discord_bot_token_here
NC_ROLE_ID=your_nc_role_id_here
NC_LOG_CHANNEL_ID=your_log_channel_id_here
NC_EXPIRY_HOURS=24
```

### 4. Run the bot
```bash
python bot.py
```

---

## 📁 Project Structure

```
Anti_raid_bot/
├── README.md           # This file
├── bot.py              # Main bot code
├── data.json           # NC role expiry tracking (persist this!)
└── requirements.txt    # Python dependencies

```

---

## 🔑 Getting API Keys

### Discord Bot Token
1. Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2. Create new application → Bot → Reset Token
3. Enable **Server Members Intent**

---

## 🤝 Invite Bot to Your Server

Generate an invite link:
1. Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2. OAuth2 → URL Generator
3. Select `bot` scope
4. Select permissions: `Manage Roles`,`Manage Channels`, `Send Messages`, `Read Message History`
5. Copy and share the generated URL

---

---

## ⚠️ Important Notes

- The bot's role must sit above the NC role in the role hierarchy to assign/remove it

---

---

## Contributing

Contributions, feature requests, and bug reports are welcome.

Feel free to fork the repository and submit a pull request.

---

⭐ If this project helped you, consider giving it a star on GitHub!
