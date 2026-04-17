import os
import logging
import anthropic
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import PyPDF2
import docx
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8679225471:AAE0JLV-u_ixJiRfsFaXuxywCoNrr5JYgMM")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "YOUR_CLAUDE_API_KEY")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """Ты — опытный юрист-эксперт по российскому праву. Твоя задача — анализировать договоры и юридические документы компании.

При анализе документа всегда давай структурированный ответ по следующему плану:

1. 📋 ТИП ДОКУМЕНТА — что это за договор/документ
2. ⚠️ РИСКИ — юридические риски, невыгодные условия, опасные пункты
3. ✅ СИЛЬНЫЕ СТОРОНЫ — что прописано хорошо и защищает интересы компании
4. ❌ ПРОБЛЕМНЫЕ ПУНКТЫ — конкретные пункты требующие правки (с номерами)
5. 📝 РЕКОМЕНДАЦИИ — что добавить, изменить или убрать
6. 🔴 ИТОГОВАЯ ОЦЕНКА — можно подписывать / нужны правки / не рекомендуется подписывать

Отвечай на русском языке. Будь конкретным, указывай номера пунктов. Не давай общих слов — только по делу."""


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(file_bytes))
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я юридический ассистент ZAZIKI.\n\n"
        "📎 Отправь мне договор или документ (PDF или Word) — я проанализирую его и укажу:\n"
        "• Юридические риски\n"
        "• Проблемные пункты\n"
        "• Рекомендации по правкам\n"
        "• Итоговую оценку\n\n"
        "Также можешь задать любой юридический вопрос текстом."
    )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    file_name = doc.file_name or ""

    await update.message.reply_text("⏳ Анализирую документ, подождите...")

    try:
        file = await context.bot.get_file(doc.file_id)
        file_bytes = await file.download_as_bytearray()

        if file_name.lower().endswith(".pdf"):
            text = extract_text_from_pdf(bytes(file_bytes))
        elif file_name.lower().endswith((".docx", ".doc")):
            text = extract_text_from_docx(bytes(file_bytes))
        else:
            await update.message.reply_text("❌ Поддерживаются только PDF и Word (.docx) файлы.")
            return

        if not text.strip():
            await update.message.reply_text("❌ Не удалось извлечь текст из документа. Попробуй другой файл.")
            return

        # Ограничиваем текст чтобы не превысить лимиты API
        if len(text) > 50000:
            text = text[:50000] + "\n\n[Документ обрезан для анализа]"

        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Проанализируй этот документ:\n\nНазвание файла: {file_name}\n\n{text}"
                }
            ]
        )

        response_text = message.content[0].text

        # Telegram ограничивает сообщения 4096 символами
        if len(response_text) > 4000:
            chunks = [response_text[i:i+4000] for i in range(0, len(response_text), 4000)]
            for chunk in chunks:
                await update.message.reply_text(chunk)
        else:
            await update.message.reply_text(response_text)

    except Exception as e:
        logger.error(f"Error processing document: {e}")
        await update.message.reply_text("❌ Ошибка при обработке документа. Попробуй ещё раз.")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    await update.message.reply_text("⏳ Думаю над ответом...")

    try:
        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )

        response_text = message.content[0].text
        await update.message.reply_text(response_text)

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await update.message.reply_text("❌ Ошибка. Попробуй ещё раз.")


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    logger.info("Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()
