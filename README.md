# Dane

## Dane is a general purpose Discord Bot written in Python using the [discord.py](https://github.com/Rapptz/discord.py) library.

### It supports many features that help improve the quality and security of your Discord server. Some features including:
- ### Anti-spam and auto-moderation
    - Mutes users that bypass the cooldown limit
    - Keeps track of all infractions (bans, kicks, mutes, warnings)
- ### Levels and Economy System
    - Gain virtual points and levels on your server based on your activity (messages sent, duration in voice, etc.)
    - A virtual economy system for users to:
        - Acquire a virtual currency
        - Buy/Sell virtual items with virtual currency

- ### Awesome rich commands and real time data provided by third-party services
    - Real-time and accurate weather forecasts and conditions

# Commands

There are different commands that Dane supports, separated into a few categories:
- Administration
- Server
- General
- Voice
- Music
- Misc
### Administrator Commands

This subset of commands are only available for Guild Admins, they allow them to moderate the server and configure certain features, such as setting a moderation channel to send all information/activity from Dane, as well setting a proper Bot channel for all bot commands and activity to avoid clogging up general channels.

#### sethelp
- Sets a help message to display to users that are looking for a quick guide on how to use your server. This could technically be anything, but it's intention is used to display helpful or important information. Users can use the ?help command to see the well-formed message.

#### setmute
- Sets the role given to a user to be muted. It is the Admin's responsibility 