from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, filters, MessageHandler
import youtube_dl as ydl
import unicodedata
import logging
import asyncio
import glob
import os

from get_token import get_token
from twitch_scraper import get_clip_data
from subs_scraper import add_subs, rmv_wtrmrk

base_folder = os.getcwd()
var_folder = datetime.now().date()
USER_STATE = {}

#region Utils
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

def clean_up() -> None:
    """
    Delete the 24h folder from 3 days ago.
    """
    today = datetime.now().date()
    termination = today - timedelta(days=3)
    strtime = termination.strftime("%Y-%m-%d")
    path = os.path.join(os.path.dirname(__file__), "Videos", f"{strtime}_24hr")
    
    if os.path.exists(path):
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(path)
        logger.info(f"\n\n[MAIN] Der Ordner {path} (3d ago) wurde gelöscht.")
    else:
        logger.info(f"\n\n[MAIN] Der Ordner {path} (3d ago) ist nicht vorhanden und wurde gegebenfalls schon gelöscht.")
#endregion

#region Download
def my_hook(d):
    if d['status'] == 'finished':
        logger.info('[YDL] Done downloading')

def title_filter(info_dict) -> None:
    title = info_dict.get('title', '')
    if all(ord(char) < 128 for char in title):
        info_dict['title'] = title.rstrip()
        return None
    else:
        video_title = unicodedata.normalize('NFKD', title).encode('ASCII', 'ignore').decode('ASCII')
        info_dict['title'] = video_title.rstrip()
        return None

def download(clip_list: list, timewindow: str, game: str) -> None:
    with ydl.YoutubeDL({
        'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        'quiet': True,
        'no_warnings': True,
        'progress_hooks': [my_hook],
        'outtmpl': f"/Videos/{game}/{datetime.now().date()}_{timewindow}/%(title)s.%(ext)s",
        'match_filter': title_filter
    }) as ydlo:
        ydlo.download(clip_list)
#endregion

def add_subtitles(language: str, timewindow: str, game: str) -> None:
    video_dir = os.path.join(f"Videos\\{game}", f"{var_folder}_{timewindow}")
    for video_file in os.listdir(video_dir):
        if video_file.endswith(".mp4") and "_merged" not in video_file:
            video_name = os.path.splitext(video_file)[0]
            if not os.path.exists(os.path.join(video_dir, f"{video_name}_merged.mp4")):
                try:
                    add_subs(f"{var_folder}_{timewindow}", video_name, language, game)
                    rmv_wtrmrk(video_dir, video_name)
                except Exception as e:
                    logger.warning(f"Error adding Subtitles: {e}")
                else:
                    logger.info(f"Finished adding Subtitles to {video_name}.")
                    logger.info("-------------------------------------------\n")

    os.chdir(os.path.join(base_folder, video_dir))
    del_list = glob.glob("*_subed.mp4")
    for file in del_list:
        os.remove(file)

#region Telegram
#region Send
async def send_merged(bot: Bot, video_path: str) -> None:
    """
    Sends all videos ending with "_merged.mp4" in the specified path to the chat.
    """
    try:
        for filename in os.listdir(video_path):
            if filename.endswith("_merged.mp4"):
                video_file = os.path.join(video_path, filename)
                await bot.send_video(chat_id=853162659, video=video_file, caption=filename)
    except Exception as e:
        logger.warning(f"An error occurred while sending the videos: {e}")

async def send(path) -> None:
    """Run the bot."""
    bot = Bot(get_token())
    await send_merged(bot, path)
#endregion

#region Input
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts the bot and asks the user to choose a game."""
    GAMES = ["league-of-legends", "valorant", "grand-theft-auto-v"]
    user_id = update.effective_user.id
    USER_STATE[user_id] = "start"

    keyboard = [
        [InlineKeyboardButton(game, callback_data=game)] for game in GAMES
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose a game:", reply_markup=reply_markup)

async def game_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asks the user to choose the number of clips."""
    user_id = update.effective_user.id
    USER_STATE[user_id] = "game_chosen"
    NUM_CLIPS = [1,2,3,4,5,6,7,8,9,10]
    query = update.callback_query
    game = query.data

    keyboard = [
        [InlineKeyboardButton(num, callback_data=f"{game}_{num}")] for num in NUM_CLIPS
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Prevent exception being thrown
    if query.message.text != "Choose the number of clips:" or query.message.reply_markup != reply_markup:
        await query.edit_message_text("Choose the number of clips:", reply_markup=reply_markup)
    else:
        pass

async def num_clips_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asks the user to choose the timewindow."""
    user_id = update.effective_user.id
    USER_STATE[user_id] = "num_clips_chosen"
    TIMEWINDOWS = ["all", "30d", "7d", "24hr"]
    query = update.callback_query
    game, num_clips = query.data.split("_")

    keyboard = [
        [InlineKeyboardButton(timewindow, callback_data=f"{game}_{num_clips}_{timewindow}")] for timewindow in TIMEWINDOWS
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Choose the timewindow:", reply_markup=reply_markup)

async def timewindow_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asks the user to choose whether to include subtitles or not."""
    user_id = update.effective_user.id
    query = update.callback_query
    data_parts = query.data.split("_")

    if len(data_parts) == 4:
        # Call subtitles_chosen function if callback data has four parts
        await subtitles_chosen(update, context)
    elif len(data_parts) == 3:
        USER_STATE[user_id] = "timewindow_chosen"
        game, num_clips, timewindow = data_parts

        keyboard = [
            [InlineKeyboardButton("Yes", callback_data=f"{game}_{num_clips}_{timewindow}_True")],
            [InlineKeyboardButton("No", callback_data=f"{game}_{num_clips}_{timewindow}_False")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Include subtitles?", reply_markup=reply_markup)
    else:
        # Handle any other cases where the callback data doesn't match the expected format
        await query.answer("Invalid callback data format")

async def subtitles_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Executes the main function with the chosen options."""
    user_id = update.effective_user.id
    USER_STATE[user_id] = "subtitles_chosen"
    query = update.callback_query
    game, num_clips, timewindow, subtitles = query.data.split("_")

    request_message = f"Processing your request for {game}, {num_clips} clip(s), {timewindow} timewindow, and subtitles={subtitles}"
    await query.edit_message_text(text=request_message, reply_markup=None)

    task = asyncio.create_task(run_main(game, int(num_clips), timewindow, subtitles == "True"))
    await task

async def send_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts the process of choosing options."""
    user_id = update.effective_user.id
    state = USER_STATE.get(user_id, "start")

    if state == "start":
        await start(update, context)
    elif state == "game_chosen":
        await game_chosen(update, context)
    elif state == "num_clips_chosen":
        await num_clips_chosen(update, context)
    elif state == "timewindow_chosen":
        await timewindow_chosen(update, context)
    elif state == "subtitles_chosen":
        await subtitles_chosen(update, context)
#endregion
#endregion

#region Mains
async def run_main(game: str, num_clips: int, timewindow: str, subtitles: bool) -> None:
    """
    Gets called by the last sub-function of premain (subtitles_chosen()).
    Executes main() and send() within the same event loop.
    """
    main(game, num_clips, timewindow, subtitles)
    video_dir = f"{var_folder}_{timewindow}"
    await send(os.path.join(base_folder, f"Videos\\{game}", video_dir))

def main(game: str, num_clips: int, timewindow: str, subtitles: bool) -> None:
    url = f"https://www.twitch.tv/directory/category/{game}/clips?range={timewindow}"
    video_dir = f"{var_folder}_{timewindow}"

    clean_up()

    clip_list = get_clip_data(num_clips, url)
    download(clip_list, timewindow, game)
    add_subtitles("en", timewindow, game)

    """if not subtitles:
        Send all videos
    else:
        Send all videos with buttons
        Add subtitles
        Send merged videos
    """

def premain():
    """
    Make the user choose all options via Telegram buttons. 
    """
    application = ApplicationBuilder().token(get_token()).build()

    application.add_handler(CommandHandler("send", send_command))
    application.add_handler(MessageHandler(filters.Regex("^send$"), send_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start))

    # Add callback query handlers with patterns
    application.add_handler(CallbackQueryHandler(game_chosen, pattern=r'^[^_]+$'))
    application.add_handler(CallbackQueryHandler(num_clips_chosen, pattern=r'^[^_]+_\d+$'))
    application.add_handler(CallbackQueryHandler(timewindow_chosen, pattern=r'^[^_]+_\d+_\w+(?!_)$'))
    application.add_handler(CallbackQueryHandler(subtitles_chosen, pattern=r'^[^_]+_\d+_\w+_[TrueFalse]+$'))

    application.run_polling()
#endregion

if __name__ == '__main__':
    premain()