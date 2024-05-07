# GummyBot
## Overview
### About
GummyBot was created to use in a few servers that I'm active in. It started simple, but I've been slowly adding more features and commands. The bot is updated regularly and I'm always open to ideas for commands.
### Playback in Voice Channel
The main purpose of the bot is to allow audio playback in a voice channel. Users can submit YouTube or Spotify track links and the bot will playback the audio in whatever voice channel that you are in. There are many bots available online that provide this, but I wanted to make one of my own to avoid outages for maintenance.
### Battlepass
The secondary purpose of the bot is to maintain a _battlepass_ for users in the server. You can register for the battlepass, gain points, level up, and purchase items from a _shop_. These points, levels, and items have zero application, but it's there to give users something to do periodically.

## Code Structure
### Entry Point
`bot.py` is the entry point for the application. The client is instantiated and commands are loaded through _cogs_. The bot API key is also supplied here.
### Cogs
Cogs allow a way to organize commands into separate classes, depending on their funcitonality. Commands fall into one of the following cogs: basics, battlepass, misc, moderation, music, and shop.