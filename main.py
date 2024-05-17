from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, filters, MessageHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from datetime import datetime, timedelta
import youtube_dl as ydl
#import unicodedata
import logging
import asyncio
import shutil
import glob
import os
import sys
import re

from subs_scraper import add_subs, rmv_wtrmrk
from get_token import get_telegram_token
from twitch_scraper import get_clip_data
from twitch_handler import get_clip_info

base_folder = os.path.dirname(os.path.abspath("main.py"))
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
    Delete folders inside game folders that are more than 3 days old.
    """
    videos_dir = os.path.join(os.path.dirname(__file__), "Videos")
    today = datetime.now().date()
    termination = today - timedelta(days=3)
    
    for game_folder in os.listdir(videos_dir): # Iterate over all game folders
        game_path = os.path.join(videos_dir, game_folder)
        if os.path.isdir(game_path): # Only continue if element is folder
            for date_folder in os.listdir(game_path): # Iterate over every date_timewindow folder
                date_path = os.path.join(game_path, date_folder)
                if os.path.isdir(date_path): # Only continue if element is folder
                    try:
                        folder_date_str = date_folder.split('_')[0]
                        folder_date = datetime.strptime(folder_date_str, "%Y-%m-%d").date()
                        if folder_date < termination:
                            shutil.rmtree(date_path)
                            logger.info(f"Obsolete folder {date_path} has been deleted.")
                    except ValueError:
                        logger.warning(f"\n\nInvalid date format for folder {date_path}. Will be skipped.")

    logger.info(f"\n\nVideo folder cleanup completed.")

def reset_script_state():
    """
    Function to reset the script state after a successful run.
    """
    # Clear the USER_STATE dictionary
    USER_STATE.clear()

    # Reset any other state variables or flags
    # ...

    logger.info("Script state has been reset.")

def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Function to handle unhandled exceptions.
    """
    logger.error(f"Unhandled exception: {exc_value}", exc_info=(exc_type, exc_value, exc_traceback))
    reset_script_state()

"""def title_filter(info_dict) -> None:
    title = info_dict.get('title', '')
    if all(ord(char) < 128 for char in title):
        info_dict['title'] = title.rstrip()
        return None
    else:
        video_title = unicodedata.normalize('NFKD', title).encode('ASCII', 'ignore').decode('ASCII')
        info_dict['title'] = video_title.rstrip()
        return None"""

def clean_title(info_dict):
    """
    Removes all non-alphanumeric characters from the title.
    """
    title = info_dict.get('title', '')
    info_dict['title'] = re.sub(r'[.]+', '', title)
    return None
#endregion

#region Download
def my_hook(d):
    if d['status'] == 'finished':
        logger.info('[YDL] Done downloading')

def download(clip_list: list, timewindow: str, game: str, subtitles: bool) -> None:
    with ydl.YoutubeDL({
        'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        'quiet': True,
        'no_warnings': True,
        'progress_hooks': [my_hook],
        'outtmpl': f"/Videos/{game}/{datetime.now().date()}_{timewindow}/%(title)s.%(ext)s",
        'match_filter': clean_title #title_filter
    }) as ydlo:
        clip_info = get_clip_info(clip_list)
        # Iterate over every clip and add subtitles if enabled
        for clip in clip_info:
            try:
                ydlo.download([clip['url']])
                if subtitles:
                    video_name = clean_title(clip['title'])
                    language = clip['language']
                    add_subtitles(language, timewindow, game, video_name)
            except Exception as e:
                logger.warning(f"Error downloading or adding subtitles for {clip['title']}: {e}")
#endregion

def add_subtitles(language: str, timewindow: str, game: str, video_name: str) -> None:
    video_dir = os.path.join(f"Videos\\{game}", f"{var_folder}_{timewindow}")
    video_file = f"{video_name}.mp4"
    if os.path.exists(os.path.join(video_dir, video_file)):
        if not os.path.exists(os.path.join(video_dir, f"{video_name}_merged.mp4")):
            try:
                add_subs(f"{var_folder}_{timewindow}", video_name, language, game)
                rmv_wtrmrk(video_dir, video_name)
            except Exception as e:
                logger.warning(f"Error adding Subtitles: {e}")
            else:
                logger.info(f"Finished adding Subtitles to {video_name}.")

    os.chdir(os.path.join(base_folder, video_dir))
    del_list = glob.glob("*_subed.mp4")
    for file in del_list:
        os.remove(file)

#region Telegram
async def send_videos(video_path: str, subtitles: bool) -> None:
    """
    Sends all videos ending with "_merged.mp4" in the specified path to the chat.
    """
    bot = Bot(get_telegram_token())
    if subtitles:
        try:
            for filename in os.listdir(video_path):
                if filename.endswith("_merged.mp4"):
                    video_file = os.path.join(video_path, filename)
                    await bot.send_video(chat_id=853162659, video=video_file, caption=filename)
        except Exception as e:
            logger.warning(f"An error occurred while sending the videos: {e}")
    else:
        try:
            for filename in os.listdir(video_path):
                if not filename.endswith("_merged.mp4"):
                    video_file = os.path.join(video_path, filename)
                    await bot.send_video(chat_id=853162659, video=video_file, caption=filename)
        except Exception as e:
            logger.warning(f"An error occurred while sending the videos: {e}")

async def start_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    await query.edit_message_text(reply_markup=None, text=request_message)

    task = asyncio.create_task(run_main(game, int(num_clips), timewindow, subtitles == "True"))
    await task

async def send_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts the process of choosing options."""
    user_id = update.effective_user.id
    state = USER_STATE.get(user_id, "start")

    try:
        if state == "start":
            await start_bot(update, context)
        elif state == "game_chosen":
            await game_chosen(update, context)
        elif state == "num_clips_chosen":
            await num_clips_chosen(update, context)
        elif state == "timewindow_chosen":
            await timewindow_chosen(update, context)
        elif state == "subtitles_chosen":
            await subtitles_chosen(update, context)
    except AttributeError:
        # Reset the script state and simulate the /send command again
        reset_script_state()
        await send_command(update, context)
#endregion

#region Mains
async def run_main(game: str, num_clips: int, timewindow: str, subtitles: bool) -> None:
    """
    Gets called by the last sub-function of premain (subtitles_chosen()).
    Executes main() and send() within the same event loop.
    """
    main(game, num_clips, timewindow, subtitles)
    video_dir = f"{var_folder}_{timewindow}"
    await send_videos(os.path.join(base_folder, f"Videos\\{game}", video_dir), subtitles)

    reset_script_state()

def main(game: str, num_clips: int, timewindow: str, subtitles: bool) -> None:
    url = f"https://www.twitch.tv/directory/category/{game}/clips?range={timewindow}"



    clip_list = get_clip_data(num_clips, url)
    download(clip_list, timewindow, game, subtitles)

def premain():
    """
    Make the user choose all options via Telegram buttons. 
    """
    clean_up()
    
    application = ApplicationBuilder().token(get_telegram_token()).build()

    application.add_handler(CommandHandler("send", send_command))
    application.add_handler(MessageHandler(filters.Regex("^send$"), send_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start_bot))

    # Add callback query handlers with patterns
    application.add_handler(CallbackQueryHandler(game_chosen, pattern=r'^[^_]+$'))
    application.add_handler(CallbackQueryHandler(num_clips_chosen, pattern=r'^[^_]+_\d+$'))
    application.add_handler(CallbackQueryHandler(timewindow_chosen, pattern=r'^[^_]+_\d+_\w+(?!_)$'))
    application.add_handler(CallbackQueryHandler(subtitles_chosen, pattern=r'^[^_]+_\d+_\w+_[TrueFalse]+$'))

    application.run_polling()
#endregion

if __name__ == '__main__':
    sys.excepthook = handle_exception
    premain()