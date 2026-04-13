import os
import base64
import logging
import requests as req
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

SYSTEM_PROMPT = """Сен — профессиональды трейдинг AI анализаторысың. 
Скриншотты көргенде МІНДЕТТІ түрде талда:

1. 📊 VOLUME АНАЛИЗ — POC, HVN/LVN зоналары, Volume spike
2. ⚖️ DELTA АНАЛИЗ — Bid/Ask қысымы, Delta divergence, Cumulative delta
3. 🎯 CLUSTER ЗОНАЛАРЫ — Ірі ойыншылар, Absorption, Imbalance
4. 📈 ТРЕНД БАҒЫТЫ — Бычий/медвежий/боковой, күші 1-10
5. 🚀 ENTRY/EXIT — Лонг/шорт нүктелері, нақты бағалар
6. 🛑 STOP-LOSS / TAKE-PROFIT деңгейлері
7. ⚠️ РИСК деңгейі

Қазақша + Орысша жаз. Нақты баға деңгейлерін көрсет."""


def analyze_chart(image_data: bytes) -> str:
    b64 = base64.standard_b64encode(image_data).decode("utf-8")
    
    response = req.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-opus-4-5",
            "max_tokens": 2000,
            "system": SYSTEM_PROMPT,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": b64,
                            },
                        },
                        {
                            "type": "text",
                            "text": "Осы trading скриншотын толық талда."
                        }
                    ],
                }
            ],
        },
        timeout=60,
    )
    
    if response.status_code != 200:
        raise Exception(f"API қате: {response.status_code} — {response.text[:300]}")
    
    data = response.json()
    return data["content"][0]["text"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📖 Қалай қолдану?", callback_data="how_to_use")],
        [InlineKeyboardButton("ℹ️ Бот туралы", callback_data="about")],
    ]
    await update.message.reply_text(
        "🤖 *SBProX AI Анализ Боты*\n\n"
        "Сәлем! Скриншот жібер — AI анализ жасайды.\n\n"
        "📸 *Қолдану:*\n"
        "1️⃣ SBProX-та графикті аш\n"
        "2️⃣ Скриншот жаса\n"
        "3️⃣ Маған жібер\n"
        "4️⃣ Толық анализ ал!\n\n"
        "👇 Скриншотты осы жерге жібер!",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "how_to_use":
        await query.message.reply_text(
            "📖 *Қалай қолдану:*\n\n"
            "1. SBProX / Quantower / TradingView ашасың\n"
            "2. Скриншот жасайсың\n"
            "3. Ботқа жібересің\n"
            "4. 10-20 секундта анализ аласың!\n\n"
            "🎯 *AI нені анализдейді:*\n"
            "• Volume зоналары мен POC\n"
            "• Delta (Bid/Ask) қысымы\n"
            "• Cluster зоналары\n"
            "• Тренд бағыты\n"
            "• Entry/Exit нүктелері\n"
            "• Stop-loss / Take-profit",
            parse_mode="Markdown"
        )
    elif query.data == "about":
        await query.message.reply_text(
            "🤖 *Бот туралы:*\n\n"
            "Claude AI (Anthropic) технологиясын қолданады.\n\n"
            "⚠️ *Ескерту:*\n"
            "Бұл бот трейдерге көмек құрал ғана.\n"
            "Барлық шешімді өзің қабылда!",
            parse_mode="Markdown"
        )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    thinking_msg = await update.message.reply_text(
        "🔍 *Скриншот алынды...*\n"
        "⏳ AI анализ жасап жатыр...\n"
        "_10-20 секунд күт_",
        parse_mode="Markdown"
    )
    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        image_data = await file.download_as_bytearray()

        analysis = analyze_chart(bytes(image_data))

        await thinking_msg.delete()

        header = "📊 *AI ТРЕЙДИНГ АНАЛИЗІ*\n" + "─" * 30 + "\n\n"
        full_msg = header + analysis

        if len(full_msg) > 4000:
            await update.message.reply_text(full_msg[:4000], parse_mode="Markdown")
            await update.message.reply_text(analysis[3700:], parse_mode="Markdown")
        else:
            await update.message.reply_text(full_msg, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Қате: {e}")
        await thinking_msg.edit_text(
            f"❌ *Қате пайда болды:*\n`{str(e)[:300]}`\n\nҚайта жіберіп көр.",
            parse_mode="Markdown"
        )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if doc.mime_type and doc.mime_type.startswith("image/"):
        thinking_msg = await update.message.reply_text("🔍 Файл алынды... AI анализ жасап жатыр...")
        try:
            file = await context.bot.get_file(doc.file_id)
            image_data = await file.download_as_bytearray()
            analysis = analyze_chart(bytes(image_data))
            await thinking_msg.delete()
            header = "📊 *AI ТРЕЙДИНГ АНАЛИЗІ*\n" + "─" * 30 + "\n\n"
            await update.message.reply_text((header + analysis)[:4000], parse_mode="Markdown")
        except Exception as e:
            await thinking_msg.edit_text(f"❌ Қате: {str(e)[:200]}")
    else:
        await update.message.reply_text("⚠️ Тек сурет файлдарын жіберіңіз (PNG, JPG)")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Скриншот жіберіңіз — мен анализ жасаймын!\n/start — басты мәзір"
    )


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN қойылмаған!")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.IMAGE, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("🚀 Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
