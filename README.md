# Minecraft Guild Plot Monitor Bot

This Discord bot monitors your Minecraft guild's plots and sends alerts to a Discord channel when a non-guild player enters them. It works with any Minecraft map server (like `map.playfuse.org/tiles`) and is super easy to set up for your guild—just edit a config file and add your bot token!

## What It Does
- Checks your guild’s plots every 5 seconds (or your chosen interval).
- Sends Discord alerts with the player’s name, coordinates, and a map link when a non-guild player enters a plot.
- Updates alerts if the player moves within the plot or after 5 minutes.
- Ignores your guild members to avoid spamming you.
- Saves plot data in `guild_plots.json` for tracking.

## License
This bot is licensed under the [Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0)](https://creativecommons.org/licenses/by-nc-nd/4.0/). You **must**:
- Credit **a2z453** (GitHub: [a2z453](https://github.com/a2z453)) as the original author.
- Use the bot only for **non-commercial purposes** (no selling or using in paid services).
- Use the code **as-is** (no modifications without written permission from a2z453).

## Prerequisites
- **Python 3.8+**: Download from [python.org](https://www.python.org/downloads/). Check with `python --version`.
- **Discord Bot Token**: Get one from the [Discord Developer Portal](https://discord.com/developers/applications).
- A Discord server where you can add bots and manage channels.
- Access to your Minecraft server’s map API (e.g., `map.playfuse.org/tiles`).

## Setup Instructions

### 1. Download the Latest Release
1. Go to the [GitHub releases page](https://github.com/a2z453/Playfuse-Conquest-Bot/releases).
2. Download the latest release (look for a ZIP file under "Assets").
3. Unzip the file to a folder on your computer (e.g., `C:\GuildBot` on Windows or `~/GuildBot` on macOS/Linux).

### 2. Install Python Libraries
You need three Python libraries to run the bot: `discord.py`, `aiohttp`, and `python-dotenv`. Open a terminal (Command Prompt on Windows, Terminal on macOS/Linux) and run:

```bash
pip install discord.py aiohttp python-dotenv
```

If `pip` doesn’t work, try `pip3 install discord.py aiohttp python-dotenv`.

### 3. Create a Discord Bot
1. Visit the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click “New Application,” name it (e.g., “Guild Plot Bot”), and click “Create.”
3. Go to the “Bot” tab, click “Add Bot,” then “Yes, do it!”
4. Copy the bot’s token (click “Copy” under “Token”). **Keep this secret!**
5. Invite the bot to your Discord server:
   - Go to “OAuth2” > “URL Generator.”
   - Check the `bot` scope.
   - Select these bot permissions:
     - `Send Messages`
     - `Embed Links`
     - `Read Messages/View Channels`
   - Copy the generated URL, paste it into your browser, and add the bot to your server.

### 4. Set Up the Bot Token
The bot needs its token stored in a `.env` file for security.
1. Open the `.env` file in the unzipped folder (or create one if it’s missing).
2. Add this line, replacing `YOUR_TOKEN_HERE` with your bot token (keep the quotes):
   ```
   DISCORD_BOT_TOKEN="YOUR_TOKEN_HERE"
   ```
3. Save the `.env` file.

**Note**: Never share your `.env` file or commit it to GitHub!

### 5. Edit the Config File
Open the `config.json` file in the unzipped folder and update it with your guild’s details. Here’s an example:

```json
{
  "GUILD_NAME": "MyAwesomeGuild",
  "ROLE_TO_PING": 123456789012345678,
  "GUILD_MEMBERS": [
    "Member1",
    "Member2",
    "Member3"
  ],
  "ALERT_CHANNEL": 123456789012345678,
  "WORLD": "minecraft_custom_overworld",
  "BASE_URL": "https://map.playfuse.org/tiles",
  "PLAYER_CHECK_INTERVAL": 5,
  "MARKER_CHECK_INTERVAL": 5
}
```

- **GUILD_NAME**: Your guild’s name (e.g., `"MyAwesomeGuild"`). Must match the name on your map server exactly.
- **ROLE_TO_PING**: The Discord role ID to ping for alerts (e.g., `123456789012345678`).
- **GUILD_MEMBERS**: List of Minecraft usernames in your guild (e.g., `["Member1", "Member2"]`). Alerts ignore these players.
- **ALERT_CHANNEL**: The Discord channel ID where alerts go (e.g., `123456789012345678`).
- **WORLD**: The Minecraft world name (default: `"minecraft_custom_overworld"`). Check your map server.
- **BASE_URL**: The map server’s API URL (default: `"https://map.playfuse.org/tiles"`).
- **PLAYER_CHECK_INTERVAL**: Seconds between player checks (default: `5`). Don’t set below 3 to avoid server strain.
- **MARKER_CHECK_INTERVAL**: Seconds between plot checks (default: `5`). Don’t set below 3.

To get Discord IDs:
1. Enable Developer Mode in Discord: Go to User Settings > Appearance > Developer Mode.
2. Right-click a role or channel in your server and select “Copy ID.”

### 6. Start the Bot
1. Open a terminal and navigate to the folder with `bot.py`:
   ```bash
   cd path/to/your/bot/folder
   ```
   Example: `cd C:\GuildBot` (Windows) or `cd ~/GuildBot` (macOS/Linux).
2. Run the bot:
   ```bash
   python bot.py
   ```
   If `python` doesn’t work, try `python3 bot.py`.
3. Look for `🚀 BotName#1234 is up and running!` in the terminal to confirm it started.

### 7. Test the Bot
- Check that the bot is online in your Discord server (look in the member list).
- Ensure it has permissions to send messages in the alert channel (check channel settings).
- Have a non-guild player enter one of your guild’s plots in Minecraft. You should see an alert in your Discord channel with their name, coordinates, and a map link.

## Troubleshooting
- **Bot won’t start**:
  - **Token error**: Open `.env` and ensure `DISCORD_BOT_TOKEN` is set correctly with quotes (e.g., `DISCORD_BOT_TOKEN="abc123"`).
  - **Config error**: Check that `config.json` exists, has valid JSON (no missing commas/brackets), and includes all required fields (`GUILD_NAME`, `ROLE_TO_PING`, `GUILD_MEMBERS`, `ALERT_CHANNEL`).
- **No alerts**:
  - Verify the `ALERT_CHANNEL` ID is correct and the bot has permissions to send messages there.
  - Ensure `GUILD_NAME` matches the name on the map server (case-sensitive).
  - Check that `WORLD` and `BASE_URL` match your map server’s settings (e.g., visit `https://map.playfuse.org/tiles/players.json` in a browser to test).
- **Data fetch errors**: Open `BASE_URL/players.json` and `BASE_URL/WORLD/markers.json` in a browser to ensure they return valid JSON.
- **Plots not saving**: Ensure the bot can write to `guild_plots.json` (check folder permissions).

## Tips
- **Keep it secure**: Don’t share your `.env` or `config.json`. Add them to `.gitignore` if using Git.
- **Adjust intervals**: If alerts are too frequent, increase `PLAYER_CHECK_INTERVAL` or `MARKER_CHECK_INTERVAL` in `config.json` (e.g., to `10` seconds).
- **Run 24/7**: Use tools like `pm2` or `screen` to keep the bot running on a server.
- **Check map server**: If you’re not using `map.playfuse.org`, ask your server admin for the correct `BASE_URL` and `WORLD`.

## Need Help?
If something’s not working, double-check your `.env` and `config.json`. Open an issue on the [GitHub repo](https://github.com/a2z453/Playfuse-Conquest-Bot) or DM [a2z45](https://discord.com/users/508772310233382932) On Discord!
