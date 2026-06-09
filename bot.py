import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from videocr import extract_subtitles

# Setup Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Get token from environment variable
BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! I am a Hard Subtitle Extractor Bot.\n"
        "Please send me a short video file, and I will extract the subtitles for you."
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    video_file = message.video or message.document
    
    if not video_file:
        await message.reply_text("Please send a valid video file.")
        return

    status_message = await message.reply_text("📥 Downloading video... Please wait.")

    try:
        file = await context.bot.get_file(video_file.file_id)
        video_path = "video.mp4"
        await file.download_to_drive(video_path)
        
        await status_message.edit_text("⚙️ Extracting subtitles (OCR)... This may take a moment.")

        output_srt = "subtitle.srt"
        # Extract English subtitles
        extract_subtitles(video_path, output_srt, lang='eng', sim_threshold=80)

        await status_message.edit_text("📤 Subtitle file is ready! Sending now...")
        with open(output_srt, 'rb') as doc:
            await message.reply_document(document=doc, filename="extracted_subtitle.srt")

    except Exception as e:
        await status_message.edit_text(f"❌ An error occurred: {str(e)}")
    
    finally:
        if os.path.exists("video.mp4"): 
            os.remove("video.mp4")
        if os.path.exists("subtitle.srt"): 
            os.remove("subtitle.srt")

def main():
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN environment variable not set.")
        return

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.Category("video/mp4"), handle_video))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
  
