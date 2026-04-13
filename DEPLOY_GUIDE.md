# 🤖 SBProX AI Trading Bot — Толық Деплой Нұсқаулығы

## 📁 Файлдар құрылымы
```
trading_bot/
├── bot.py              ← Негізгі бот коды
├── requirements.txt    ← Python пакеттері
├── Dockerfile          ← Docker конфигурациясы
└── railway.toml        ← Railway деплой конфигурациясы
```

---

## 🔑 ҚАДАМ 1 — API Кілттерін алу

### Telegram Bot Token:
1. Telegram-да `@BotFather` ашасың
2. `/newbot` жазасың
3. Бот атауын бересің (мысалы: `SBProX Analyzer`)
4. Username бересің (мысалы: `sbprox_ai_bot`)
5. **TOKEN алдың** → сақта: `7123456789:AAF...`

### Anthropic API Key:
1. https://console.anthropic.com/ сайтына кіресің
2. Тіркелесің (Google account болса жеңіл)
3. `API Keys` → `Create Key`
4. **KEY алдың** → сақта: `sk-ant-...`

---

## 🚀 ҚАДАМ 2 — Railway-де деплой (ТЕГІН, ең оңай)

### 2.1 — GitHub-қа жүктеу:
```bash
# Компьютерде Git орнатылған болуы керек
git init
git add .
git commit -m "Trading bot initial commit"
```

GitHub.com-да жаңа репозиторий жаса → Push:
```bash
git remote add origin https://github.com/СЕНІҢ_USERNAME/trading-bot.git
git push -u origin main
```

### 2.2 — Railway.app-та деплой:
1. https://railway.app/ → `Login with GitHub`
2. `New Project` → `Deploy from GitHub Repo`
3. Репозиторийіңді таңда
4. **Variables** бөліміне кір:

```
TELEGRAM_BOT_TOKEN = 7123456789:AAF...бот_токенің...
ANTHROPIC_API_KEY  = sk-ant-...кілтің...
```

5. `Deploy` басасың
6. 2-3 минутта бот жұмыс істейді! ✅

---

## 🐳 ҚАДАМ 3 — Docker арқылы (VPS/сервер бар болса)

### Сервер дайындау (Ubuntu 20.04+):
```bash
# Docker орнату
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Ботты жүктеу
git clone https://github.com/СЕНІҢ_USERNAME/trading-bot.git
cd trading-bot

# .env файл жасау
cat > .env << EOF
TELEGRAM_BOT_TOKEN=7123456789:AAF...
ANTHROPIC_API_KEY=sk-ant-...
EOF

# Іске қосу
docker build -t trading-bot .
docker run -d --env-file .env --name trading-bot --restart unless-stopped trading-bot

# Логтарды тексеру
docker logs -f trading-bot
```

---

## 💻 ҚАДАМ 4 — Локальда тексеру (компьютерде)

```bash
# Python 3.10+ керек
pip install -r requirements.txt

# Windows:
set TELEGRAM_BOT_TOKEN=7123456789:AAF...
set ANTHROPIC_API_KEY=sk-ant-...
python bot.py

# Linux/Mac:
export TELEGRAM_BOT_TOKEN=7123456789:AAF...
export ANTHROPIC_API_KEY=sk-ant-...
python bot.py
```

---

## 📱 ҚОЛДАНУ

1. Telegram-да ботыңды тап: `@сенің_бот_username`
2. `/start` жаз
3. SBProX-та графикті аш
4. Screenshot жаса
5. Ботқа жібер
6. 10-20 секундта толық анализ!

---

## 🔧 Бот мүмкіндіктері

| Мүмкіндік | Сипаттама |
|-----------|-----------|
| 📊 Volume анализ | POC, HVN, LVN зоналары |
| ⚖️ Delta анализ | Bid/Ask қысымы, divergence |
| 🎯 Cluster зоналары | Ірі ойыншы аймақтары |
| 📈 Тренд | Бағыт + күш (1-10) |
| 🚀 Entry/Exit | Нақты баға деңгейлері |
| 🛑 Stop-loss | Автоматты есептеу |

---

## ⚠️ МАҢЫЗДЫ ЕСКЕРТУЛЕР

- **Anthropic API** — айына ~$5-20 кетеді (скриншот санына байланысты)
- **Railway тегін plan** — айына 500 сағат (жеткілікті)
- **Скриншот сапасы** — жақсы скриншот = жақсы анализ
- **Disclaimer** — бұл құрал, соңғы шешімді өзің қабылда!

---

## 🆘 Жиі кездесетін қателер

### "TELEGRAM_BOT_TOKEN not set":
→ Environment variables дұрыс қойылмаған

### "anthropic.AuthenticationError":
→ API key дұрыс емес немесе баланс жоқ

### Бот жауап бермесе:
```bash
docker logs trading-bot  # логтарды тексер
```

---

## 📞 Контакт
Сұрақтар болса — ботты тексер, логтарды қара!
