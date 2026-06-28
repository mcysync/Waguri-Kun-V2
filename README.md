# Waguri-Kun-V2
```markdown
# 🌸 Waguri Bot 

**Waguri** is an enterprise-grade, production-ready Telegram moderation, administration, AI, and utility bot. Written entirely in Python 3.12+ using Pyrogram and fully asynchronous architecture, Waguri is designed for massive scalability, high concurrency, and premium community management.

She combines a friendly, elegant, and anime-inspired personality with strict, professional moderation capabilities.

---

## ✨ Key Features

### 🛡️ Enterprise Moderation & Security
*   **Advanced Punishments:** Bans, Temporary Bans, Shadow Bans, Mutes, Media/Voice Locks, and Kicks.
*   **Automated Security:** Scam detection, malicious file scanning, and link/invite filtering.
*   **Anti-Spam & Anti-Flood:** Intelligent cache-based spam detection with automatic mute/ban triggers.
*   **Anti-Raid:** Join burst detection and automatic chat lockdown modes.
*   **Welcome Captcha:** Inline button verification to filter out bot accounts.

### 🧠 Artificial Intelligence
*   **OpenAI Integration:** Chat with Waguri natively using GPT-3.5/4.
*   **Smart Utilities:** Chat summarization, automated grammar correction, and intelligent replies.

### 💴 Economy & Engagement
*   **Economy System:** Daily claims, wallets, banking, and peer-to-pay functionality.
*   **Leveling System:** Adaptive XP gaining with automatic rank updates.
*   **Reputation:** Allow users to thank each other and build credibility scores.

### 🎌 Anime & Fun
*   **MyAnimeList Integration:** Search for anime, stats, and synopses natively.
*   **Interactive Commands:** Waifu generation, random anime quotes, and roleplay actions (slaps, hugs).
*   **Giveaways:** Built-in interactive giveaway hosting.

### 🛠️ Utility & Maintenance
*   **No External Database Required:** Runs 100% offline using `aiosqlite` with automatic WAL checkpointing, schema migrations, and connection pooling.
*   **Utility Tools:** Base64, UUID generation, Hash generation, JSON formatting, and Weather fetching.
*   **Enterprise Backups:** Create, download, and restore full database backups securely via Telegram.
*   **Internal API:** Built-in FastAPI server for external webhook triggers and dashboard integrations.

---

## 🚀 Prerequisites

Before installing Waguri, ensure you have the following:

1. **Python 3.12** or higher.
2. A **Telegram API ID** and **API Hash** (Get it from [my.telegram.org](https://my.telegram.org)).
3. A **Bot Token** (Get it from [@BotFather](https://t.me/BotFather)).

> **Note:** Waguri does **not** require MongoDB, Redis, or any external online database service. She works straight out of the box using a high-performance local SQLite architecture.

---

## 💻 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/WaguriBot.git
   cd WaguriBot
   ```

2. **Create a virtual environment (Recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the Environment:**
   Create a `.env` file in the root directory and configure your keys:
   ```env
   # Telegram API Configuration
   API_ID=1234567
   API_HASH=your_api_hash_here
   BOT_TOKEN=your_bot_token_here
   
   # Privileged Users
   OWNER_ID=123456789
   SUDO_USERS=987654321 112233445
   
   # Optional API Keys
   OPENAI_API_KEY=sk-your_openai_api_key_here
   
   # Feature Toggles
   ENABLE_AI=True
   ENABLE_ECONOMY=True
   ENABLE_ANIME=True
   
   # Customization
   BOT_USERNAME=YourWaguriBot
   ```

---

## ⚙️ Running Waguri

Once configured, simply run the main script:

```bash
python bot.py
```

Waguri will automatically:
1. Create the `data/` directories.
2. Initialize and migrate the local SQLite database.
3. Start the background APScheduler tasks.
4. Start the internal FastAPI server.
5. Log into Telegram and begin listening for updates.

---

## 📂 Project Architecture

Waguri follows SOLID principles and clean, enterprise-level architecture:

```text
WaguriBot/
├── bot.py                # Main entry point & Pyrogram client initialization
├── config.py             # Environment variables and configuration class
├── utils.py              # Decorators, time parsers, and shared helpers
├── requirements.txt      # Dependency manifest
├── data/                 # Auto-generated folder for DB, logs, and backups
│   └── database.db       # Primary SQLite database
└── modules/              # Pluggable feature modules
    ├── database.py       # Asynchronous Database Abstraction Layer
    ├── moderation.py     # Core punishment commands
    ├── antispam.py       # Algorithmic spam detection
    ├── security.py       # Malware and Phishing protection
    ├── economy.py        # Coins, wallets, and payments
    ├── ai.py             # LLM implementations
    └── ... (40+ more specialized modules)
```

---

## 📝 Command Highlights

*Here are just a few of the 250+ commands available in Waguri:*

**Moderation:** `/ban`, `/tban`, `/mute`, `/kick`, `/warn`, `/purge`, `/lock`, `/unlock`  
**Security:** `/raidmode`, `/antispam`, `/security`, `/captcha`, `/lockdown`  
**Economy:** `/daily`, `/balance`, `/pay`, `/rank`, `/rep`  
**AI & Fun:** `/ask`, `/summarize`, `/grammar`, `/anime`, `/waifu`, `/quote`  
**Administration:** `/settings`, `/setwelcome`, `/filter`, `/notes`, `/backup`, `/stats`  

*Use `/help` inside the bot to see the full, dynamically generated list of features.*

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! 
Feel free to check the [issues page](https://github.com/yourusername/WaguriBot/issues).

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
*Built with ❤️ and elegant code. "Waguri is ready for action~ 🌸"*
```
