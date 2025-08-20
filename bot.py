# Copyright (c) 2025 a2z453
# This code is licensed under the Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0) License.
# You may not: claim this code as your own, modify it without permission to alter the way it operates, or use it for commercial purposes.
# See LICENSE file or https://creativecommons.org/licenses/by-nc-nd/4.0/ for details.
# Contact a2z453 (via GitHub: https://github.com/a2z453) for permission requests.

import discord
import aiohttp
import asyncio
import re
import json
import os
import time
from discord.ext import tasks

# Set up Discord bot with intents
intents = discord.Intents.default()
bot = discord.Client(intents=intents)

# Load config from JSON file
CONFIG_FILE = "config.json"
try:
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
except FileNotFoundError:
    raise FileNotFoundError(f"🚫 Can't find {CONFIG_FILE}! Please create it with the required settings (see README.md).")
except json.JSONDecodeError:
    raise ValueError(f"🚫 {CONFIG_FILE} has invalid JSON! Check for typos or missing commas/brackets.")

# Required config fields
required_fields = ["GUILD_NAME", "ROLE_TO_PING", "GUILD_MEMBERS", "ALERT_CHANNEL"]
for field in required_fields:
    if field not in config:
        raise ValueError(f"🚫 Missing {field} in {CONFIG_FILE}! Add it to the config file.")

# Load config with defaults for optional fields
GUILD_NAME = config["GUILD_NAME"]
ROLE_TO_PING = config["ROLE_TO_PING"]
GUILD_MEMBERS = config["GUILD_MEMBERS"]
ALERT_CHANNEL = config["ALERT_CHANNEL"]
WORLD = config.get("WORLD", "minecraft_custom_overworld")  # Default world
BASE_URL = config.get("BASE_URL", "https://map.playfuse.org/tiles")  # Default map URL
player_check_interval = config.get("PLAYER_CHECK_INTERVAL", 5)  # Default 5 seconds
marker_check_interval = config.get("MARKER_CHECK_INTERVAL", 5)  # Default 5 seconds

# Derived URLs
PLAYERS_URL = f"{BASE_URL}/players.json"
MARKERS_URL = f"{BASE_URL}/{WORLD}/markers.json"

# Load bot token from environment variable
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("🚫 DISCORD_BOT_TOKEN not set! Set it as an environment variable (see README.md).")

# File to store plot data
PLOTS_JSON = "guild_plots.json"

# Track players in plots: {uuid: {"message_id": int, "plot_id": str, "x": float, "z": float, "last_seen": float}}
active_players = {}

# --- Helper Functions ---
def parse_popup(popup_html):
    """Grabs plot details from the HTML popup mess."""
    plot_id = re.search(r'id="ctt-(\d+)"', popup_html)
    guild_name = re.search(r'Territory of:.*?guild-name[^>]*>(.*?)</div>', popup_html, re.DOTALL)
    conqueror = re.search(r'Conqueror:.*?value">(.*?)</div>', popup_html, re.DOTALL)
    conquered_time = re.search(r'Conquered at:.*?value">(.*?)</div>', popup_html, re.DOTALL)
    
    return {
        "id": plot_id.group(1) if plot_id else "unknown_id",
        "guild": guild_name.group(1) if guild_name else "No Guild",
        "conqueror": conqueror.group(1) if conqueror else "Nobody",
        "conquered_at": conquered_time.group(1) if conquered_time else "Unknown"
    }

def save_plots(plots):
    """Saves guild plots to file, but only if we got something good."""
    if not plots:
        print(f"No plots found for {GUILD_NAME}, keeping what's in {PLOTS_JSON}")
        return
    
    current_plots = load_plots()
    # Keep non-guild plots and add new ones
    updated_plots = [p for p in current_plots if p.get("owner") != GUILD_NAME]
    updated_plots.extend(plots)
    
    with open(PLOTS_JSON, "w") as f:
        json.dump(updated_plots, f, indent=2)  # Pretty print for readability

def load_plots():
    """Loads plot data from the JSON file."""
    if os.path.exists(PLOTS_JSON):
        with open(PLOTS_JSON, "r") as f:
            return json.load(f)
    return []  # Return empty list if file doesn't exist

# Bot Events
@bot.event
async def on_ready():
    print(f"🚀 {bot.user} is up and running!")
    check_players.start()  # Start player checks
    check_claims.start()   # Start checking claims

# Background Tasks
@tasks.loop(seconds=marker_check_interval)
async def check_claims():
    """Check for updates to guild plots."""
    async with aiohttp.ClientSession() as session:
        async with session.get(MARKERS_URL) as resp:
            if resp.status != 200:
                print(f"Oops, markers.json fetch failed with HTTP {resp.status}")
                return
            try:
                data = await resp.json()
            except Exception as e:
                print(f"Couldn't parse markers.json: {e}")
                return

            guild_plots = []
            for entry in data:
                if entry["id"] != "conquer_plots":
                    continue
                for marker in entry.get("markers", []):
                    if marker["type"] != "rectangle":
                        continue
                    popup_data = parse_popup(marker.get("popup", ""))
                    if popup_data["guild"] != GUILD_NAME:
                        continue
                    points = marker.get("points", [])
                    if len(points) != 2:
                        continue
                    x1, z1 = points[0]["x"], points[0]["z"]
                    x2, z2 = points[1]["x"], points[1]["z"]
                    mid_x, mid_z = (x1 + x2) / 2, (z1 + z2) / 2
                    guild_plots.append({
                        "id": popup_data["id"],
                        "world": WORLD,
                        "x1": x1, "z1": z1, "x2": x2, "z2": z2,
                        "mid_x": mid_x, "mid_z": mid_z,
                        "owner": popup_data["guild"],
                        "conqueror": popup_data["conqueror"],
                        "conquered_at": popup_data["conquered_at"]
                    })
            save_plots(guild_plots)

@tasks.loop(seconds=player_check_interval)
async def check_players():
    """Check for players in guild plots and send alerts."""
    plots = load_plots()
    if not plots:
        return  # No plots, no point checking

    async with aiohttp.ClientSession() as session:
        async with session.get(PLAYERS_URL) as resp:
            if resp.status != 200:
                print(f"Player fetch failed: HTTP {resp.status}")
                return
            try:
                data = await resp.json()
            except Exception as e:
                print(f"Error parsing players.json: {e}")
                return

            players = data.get("players", [])
            channel = bot.get_channel(ALERT_CHANNEL)
            if not channel:
                print("Channel not found, can't send alerts! Check ALERT_CHANNEL in config.json.")
                return

            now = time.time()
            current_players = set()

            for player in players:
                try:
                    # Skip your own guild members or wrong world
                    if player.get("world") != WORLD or player.get("name") in GUILD_MEMBERS:
                        continue
                    uuid = player.get("uuid")
                    if not uuid:
                        continue
                    current_players.add(uuid)

                    # Check if player is in a guild plot
                    for plot in plots:
                        if (plot["x1"] <= player["x"] <= plot["x2"] and
                            plot["z1"] <= player["z"] <= plot["z2"]):
                            map_url = f"https://map.playfuse.org/?world={WORLD}&x={player['x']}&z={player['z']}&zoom=1"
                            embed = discord.Embed(
                                title="⚠ Intruder Alert! ⚠",
                                description=(
                                    f"**{player['name']}** is in our plot at "
                                    f"(*{plot['mid_x']:.0f}, {plot['mid_z']:.0f}*)\n\n"
                                    f"[View on Map]({map_url})\n\n"
                                    f"Coords: ({player['x']:.0f}, {player['z']:.0f})"
                                ),
                                color=0xFF3333  # Bright red for alerts
                            )
                            embed.set_thumbnail(url=f"https://mc-heads.net/avatar/{uuid}/64")

                            if uuid in active_players:
                                last_seen = active_players[uuid]["last_seen"]
                                msg_id = active_players[uuid]["message_id"]
                                try:
                                    message = await channel.fetch_message(msg_id)
                                except discord.NotFound:
                                    message = None

                                # Update or send new alert if it's been a while or message is gone
                                if now - last_seen > 300 or message is None:
                                    message = await channel.send(embed=embed)
                                else:
                                    await message.edit(embed=embed)

                                active_players[uuid] = {
                                    "message_id": message.id,
                                    "plot_id": plot["id"],
                                    "x": player["x"], "z": player["z"],
                                    "last_seen": now
                                }
                            else:
                                # New player in plot
                                message = await channel.send(embed=embed)
                                active_players[uuid] = {
                                    "message_id": message.id,
                                    "plot_id": plot["id"],
                                    "x": player["x"], "z": player["z"],
                                    "last_seen": now
                                }
                            break  # Stop checking other plots for this player
                except KeyError as e:
                    print(f"Missing key in player data: {e}")
                    continue

            # Mark players who left as still active but update their last_seen
            for uuid in list(active_players.keys()):
                if uuid not in current_players:
                    active_players[uuid]["last_seen"] = now

# Start The Bot
if __name__ == "__main__":
    bot.run(BOT_TOKEN)
