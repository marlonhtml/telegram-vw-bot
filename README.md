# VimeWorld Telegram Bot

A Telegram bot for VimeWorld (Minecraft server) player stats and server information.

## Features

- **Player Search** - Get player info: username, ID, rank, level, playtime, and online status
- **Server Online** - View current online count and top 5 game modes
- **Staff Online** - See which moderators and admins are online
- **Help** - Bot commands and features

## Installation

### Requirements

- Python 3.8+
- Required packages:

```bash
pip install aiogram requests python-dotenv
```

### Setup

1. Create a `.env` file with your tokens:

```env
TELEGRAM_TOKEN=your_telegram_bot_token
ACCESS_TOKEN=your_vimeworld_api_token
```

2. Get tokens:

   - **TELEGRAM_TOKEN**: Get from [@BotFather](https://t.me/BotFather)
   - **ACCESS_TOKEN**: Get from [VimeWorld Developer Portal](https://vimeworld.com/developer)
3. Run the bot:

```bash
python bot_vw.py
```

## Usage

Start the bot with `/start` command in Telegram, then use the buttons to navigate.

**Commands:**

- `/start` - Main menu
- `/help` - Bot help

## Project Structure

```
bot_vimeworld/
├── bot_vw.py           # Main bot file
├── config.py           # Configuration
├── .env                # Environment variables
├── handlers/
│   └── routes.py       # Command handlers
└── README.md
```

## TODO

- [ ] Add guild viewing
- [ ] Add player tracking notifications

## Author

Created by [marlonhtml](https://guns.lol/marlonhd)
