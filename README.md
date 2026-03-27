# 🤖 AI Portfolio Agent

An automated AI-powered portfolio tracking system that reads Zerodha Coin emails, builds your mutual fund portfolio, calculates real-time performance, and sends daily insights via email.

---

## 🚀 Features

- 📥 Reads investment emails from Gmail (Zerodha Coin)
- 📊 Parses mutual fund transactions automatically
- 💼 Builds portfolio with units & investment tracking
- 🌐 Fetches real-time NAV from AMFI
- 📈 Calculates current value & profit/loss
- 🤖 Generates AI-based financial insights (using Ollama)
- 📧 Sends daily professional email reports
- ⏰ Fully automated via scheduler

---

## 🧠 Tech Stack

- Python
- IMAP (Email parsing)
- BeautifulSoup (HTML parsing)
- Requests (API calls)
- Ollama (Local LLM)
- SMTP (Email automation)

---


## ⚙️ Setup

### 1. Clone repo
git clone https://github.com/adarsh3149/portfolio-agent.git
cd portfolio-agent

### 2. Install Dependencies
pip install -r requirements.txt

### 3. Configure Email
#### Add and Update config/settings.py
EMAIL = "your_email@gmail.com"
APP_PASSWORD = "your_app_password"
IMAP_SERVER = "imap.gmail.com"

### 4. Run
python main.py
