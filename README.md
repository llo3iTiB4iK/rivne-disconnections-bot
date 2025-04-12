# 🔌 Rivne Disconnections Bot

A Telegram bot that helps residents of Rivne region, Ukraine stay informed about scheduled and emergency power outages. The bot parses up-to-date data from official energy provider sources and delivers personalized, real-time notifications to thousands of users.

---

## 📲 Features

- 🔎 **Search by address** — instantly get the disconnection schedule for your address
- 📅 **Daily schedule notifications** — sent automatically each morning
- ⚠️ **Emergency alerts** — receive instant updates when outages are added or cancelled
- 🔁 **Real-time updates** — data is parsed and synchronized continuously
- 👥 **Group support** — bot works both in private and group chats
- 📈 **Used by over 13,000+ users**

---

## 🛠️ Tech Stack

- **Python 3.10+**
- `aiogram` — Telegram bot framework (async)
- `requests` — HTTP requests
- `aiosqlite` — async database queries
- `BeautifulSoup` — web scraping
- `asyncio` — task scheduling
- `sqlite` — lightweight persistent database

---

## 🗂️ Repository Structure

```
rivne-disconnections-bot/
├── forms/              # Finite state machine (FSM) definitions for managing user interaction flows
├── functions/          # Core logic: data fetching, parsing, notifications, and utility functions
├── handlers/           # Telegram bot handlers and message formatting
├── bot.py              # Bot entry point: initializes and starts the Telegram bot
├── config.py           # Configuration settings and environment variables
└── requirements.txt    # Project dependencies
```

---

## ⚙️ Setup

### 1. Clone the repo

```bash
git clone https://github.com/llo3iTiB4iK/rivne-disconnections-bot.git
cd rivne-disconnections-bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

Create a `.env` file in the root directory:

```
TEST_BOT_TOKEN=bot_token_for_development_environment
PROD_BOT_TOKEN=bot_token_for_production_environment
ADMIN_USER_ID=admin_user_telegram_id
```

### 4. Run the bot

```bash
python bot.py
```

> ⚠️ **Note:** Make sure the parsing source URL is still accessible and has not changed.
