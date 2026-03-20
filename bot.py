import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

user_last_message = {}

KEYWORDS = {
    "notes": "📚 Notes link: https://your-link.com/notes",
    "pyqs": "📄 PYQs link: https://your-link.com/pyqs",
    "quantum": "📘 Quantum link: https://your-link.com/quantum",
    "important question": "✅ Important Questions: https://your-link.com/important"
}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text.lower()

    for key, reply_text in KEYWORDS.items():
        if key in text:
            unique_key = f"{chat_id}_{user_id}_{key}"

            if unique_key in user_last_message:
                try:
                    await context.bot.delete_message(
                        chat_id=chat_id,
                        message_id=user_last_message[unique_key]
                    )
                except Exception:
                    pass

            sent_message = await update.message.reply_text(reply_text)
            user_last_message[unique_key] = sent_message.message_id
            break

if __name__ == "__main__":
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not found in environment variables.")

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()
