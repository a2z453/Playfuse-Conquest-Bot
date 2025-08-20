# Minecraft Guild Plot Monitor Bot

This Discord bot watches your Minecraft guild's plots and sends alerts to a Discord channel when a non-guild player enters them. It’s designed to work with a map server like `map.playfuse.org` and is easy to set up for your own guild. Just edit a config file, and you’re good to go!

## What It Does
- Checks your guild’s plots every 5 seconds (or your chosen interval).
- Sends Discord alerts with the player’s name, coordinates, and a map link when someone enters a plot.
- Updates alerts if the player moves within the plot or after 5 minutes.
- Ignores your guild members to avoid spam.
- Saves plot data in `guild_plots.json` for tracking.

## Prerequisites
- **Python 3.8+**: Install Python from [python.org](https://www.python.org/downloads/). Check with `python --version`.
- **Discord Bot Token**: Get one from the [Discord Developer Portal](https://discord.com/developers/applications).
- A Discord server where you have permission to add bots and manage channels.
- Access to your Minecraft server’s map API (e.g., `map.playfuse.org/`).

## Setup Instructions

### 1. Download The Latest Release
Download the code by cloning the repo or downloading the ZIP and extracting it to a folder.

