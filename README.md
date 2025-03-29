# Suggon

**Suggon** is a FastAPI-powered microservice that manages a pool of SeleniumBase browser instances to scrape JavaScript-heavy, bot-protected websites like those using Cloudflare Turnstile. Designed to be async-friendly, resource-efficient, and resistant to blocking.
If you don't like it, then SUGGON DEEZNUTS

---
## ⚙️ Features
- 🚀 FastAPI + `asyncio.Queue` to manage browser workers
- 🚀 Avg 7 secs response on heavy Turnstile websites
- 🧠 Prewarmed SeleniumBase instances for fast scraping
- 🔐 Proxy rotation support
- 🤖 Anti-bot detection handling (recaptcha, hcaptcha, rate-limit pages)
- 🤖 Seleniumbase headless drivers for speed and efficieny. You can edit the driver configs on workers.py and increase instances on main.py
- 🧼 Graceful shutdown: kills all chromedriver processes on server exit
- 🪄 Self-restarting stale or blocked drivers
---

## 📦 Requirements

- Python 3.10+
- Google Chrome installed
- `proxies.txt` file (one proxy per line in `ip:port:user:pass` format)

### 📥 Install Dependencies

```bash
pip install -r requirements.txt```

### 🔧 Run the server

uvicorn main:app --host 0.0.0.0 --port 8000 --reload



📤 Make a scrape request
  POST /scrape
  Content-Type: application/json
  
  {
    "url": "https://example.com"
  }



📤 Response
  {
    "html": "<!DOCTYPE html>...",
    "blocked": false
  }


