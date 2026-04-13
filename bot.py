import os
import base64
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)
from anthropic import Anthropic

# ─── Logging ───────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ─── Clients ───────────────────────────────────────────────
anthropic = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# ─── System Prompt ─────────────────────────────────────────
SYSTEM_PROMPT = """Сен — профессиональды трейдинг AI анализаторысың. 
Сенің міндетің: SBProX, Quantower немесе кез-келген trading платформасының скриншотын талдау.

Скриншотты көргенде МІНДЕТТІ түрде талда:

1. 📊 VOLUME АНАЛИЗ
   - Доминантты volume зоналары қайда?
   - Volume spike бар ма? Қашан, қай бағада?
   - POC (Point of Control) деңгейі

2. ⚖️ DELTA АНАЛИЗ (Bid/Ask)
   - Купон/сату қысымы қандай?
   - Delta divergence бар ма?
   - Cumulative delta тренді

3. 🎯 CLUSTER ЗОНАЛАРЫ
   - Ірі ойыншылардың жинақтау зоналары
   - Absorption аймақтары
   - Imbalance зоналары

4. 📈 ТРЕНД БАҒЫТЫ
   - Негізгі тренд (бычий/медвежий/боковой)
   - Тренд күші (1-10 шкала)
   - Тренд өзгеру сигналдары

5. 🚀 ENTRY/EXIT НҮКТЕЛЕРІ
   - Потенциальды лонг entry нүктелері (бағасымен)
   - Потенциальды шорт entry нүктелері (бағасымен)  
   - Stop-loss деңгейлері
   - Take-profit мақсаттары

6. ⚠️ РИСК ЕСКЕРТУІ
   - Жалпы рыноктық риск деңгейі
   - Негізгі қауіп зоналары

Жауапты ҚАЗАҚША + ОРЫСША жаз (маңызды терминдерді екі тілде).
Форматты сақта: эмодзи, бөлімдер, нақты баға деңгейлері.
Соңында қысқаша ҚОРЫТЫНДЫ (2-3 сөйлем) жаз.

МАҢЫЗДЫ: Егер скриншотта нақты баға деңгейлері көрінсе — нақты цифрлармен жаз.
Егер граф түсініксіз болса — нені көре алатыныңды жаз, болжам жасама."""

# ─── Analysis Function ─────────────────────────────────────
async def analyze_chart(image_data: bytes, mime_type: str = "image/jpeg") -> str:
    """Send image to Claude for analysis."""
    b64_image = base64.standard_b64encode(image_data).decode("utf-8")

    response = anthropic.messages.create(
        model="claude-opus-4-5",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": mime_type,
                            "data": b64_image,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Осы trading скриншотын толық талда. Барлық бөлімдерді қамт."
                    }
                ],
            }
        ],
    )
    return response.content[0].text

# ─── Handlers ──────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 Қалай қолдану?", callback_data="how_to_use")],
        [InlineKeyboardButton("ℹ️ Бот туралы", callback_data="about")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🤖 *SBProX AI Анализ Боты*\n\n"
        "Сәлем! Мен сенің trading скриншоттарыңды талдаймын.\n\n"
        "📸 *Қолдану өте қарапайым:*\n"
        "1️⃣ SBProX-та графикті аш\n"
        "2️⃣ Скриншот жаса\n"
        "3️⃣ Маған жібер\n"
        "4️⃣ AI анализді ал\n\n"
        "👇 Скриншотты осы жерге жібер!",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "how_to_use":
        await query.message.reply_text(
            "📖 *Қалай қолдану керек:*\n\n"
            "1. SBProX / Quantower / TradingView ашасың\n"
            "2. Volume, Delta, Cluster графигін дайындайсың\n"
            "3. Screenshot жасайсың (Win+Shift+S немесе Snipping Tool)\n"
            "4. Скриншотты осы ботқа жібересің\n"
            "5. 10-15 секундта толық анализ аласың\n\n"
            "🎯 *AI нені анализдейді:*\n"
            "• Volume зоналары мен POC\n"
            "• Delta (Bid/Ask) қысымы\n"
            "• Cluster зоналары\n"
            "• Тренд бағыты\n"
            "• Entry/Exit нүктелері\n"
            "• Stop-loss / Take-profit деңгейлері",
            parse_mode="Markdown"
        )
    elif query.data == "about":
        await query.message.reply_text(
            "🤖 *SBProX AI Bot туралы:*\n\n"
            "Бұл бот Claude AI (Anthropic) технологиясын қолданады.\n\n"
            "📊 *Мүмкіндіктер:*\n"
            "• Кез-келген trading платформа скриншоты\n"
            "• Volume профиль анализі\n"
            "• Footprint chart анализі\n"
            "• Cluster зоналар анализі\n\n"
            "⚠️ *Ескерту:*\n"
            "Бұл бот трейдерге көмек құрал ғана.\n"
            "Барлық шешімді өзің қабылда!",
            parse_mode="Markdown"
        )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming photos."""
    thinking_msg = await update.message.reply_text(
        "🔍 *Скриншот алынды...*\n"
        "⏳ AI анализ жасап жатыр...\n\n"
        "_Бұл 10-20 секунд алуы мүмкін_",
        parse_mode="Markdown"
    )

    try:
        # Get highest quality photo
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        image_data = await file.download_as_bytearray()

        # Analyze with Claude
        analysis = await analyze_chart(bytes(image_data), "image/jpeg")

        # Delete thinking message
        await thinking_msg.delete()

        # Send analysis
        header = "📊 *AI ТРЕЙДИНГ АНАЛИЗІ*\n" + "─" * 30 + "\n\n"

        # Telegram message limit is 4096 chars
        full_message = header + analysis
        if len(full_message) > 4000:
            # Split into chunks
            await update.message.reply_text(
                header + analysis[:3800] + "\n\n_...жалғасы_",
                parse_mode="Markdown"
            )
            await update.message.reply_text(
                "_...жалғасы:_\n\n" + analysis[3800:],
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(full_message, parse_mode="Markdown")

        # Follow-up keyboard
        keyboard = [[InlineKeyboardButton("📸 Тағы бір скриншот анализ", callback_data="new_analysis")]]
        await update.message.reply_text(
            "✅ Анализ дайын! Тағы скриншот жіберсең болады.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    except Exception as e:
        logger.error(f"Analysis error: {e}")
        await thinking_msg.edit_text(
            "❌ *Қате пайда болды*\n\n"
            f"Себебі: {str(e)[:200]}\n\n"
            "Қайта скриншот жіберіп көр немесе /start басып бастан баста.",
            parse_mode="Markdown"
        )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle image documents (uncompressed photos)."""
    doc = update.message.document
    if doc.mime_type and doc.mime_type.startswith("image/"):
        thinking_msg = await update.message.reply_text(
            "🔍 *Файл алынды...*\n⏳ AI анализ жасап жатыр...",
            parse_mode="Markdown"
        )
        try:
            file = await context.bot.get_file(doc.file_id)
            image_data = await file.download_as_bytearray()
            mime = doc.mime_type or "image/png"
            analysis = await analyze_chart(bytes(image_data), mime)
            await thinking_msg.delete()
            header = "📊 *AI ТРЕЙДИНГ АНАЛИЗІ*\n" + "─" * 30 + "\n\n"
            await update.message.reply_text(header + analysis[:4000], parse_mode="Markdown")
        except Exception as e:
            await thinking_msg.edit_text(f"❌ Қате: {str(e)[:200]}", parse_mode="Markdown")
    else:
        await update.message.reply_text(
            "⚠️ Тек сурет файлдарын жіберіңіз (PNG, JPG, JPEG)"
        )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages."""
    await update.message.reply_text(
        "👋 Скриншот жіберіңіз — мен анализ жасаймын!\n\n"
        "📸 SBProX → Screenshot → осы жерге жіберіңіз\n\n"
        "/start — басты мәзір",
        parse_mode="Markdown"
    )

# ─── Main ──────────────────────────────────────────────────
def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set!")

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
