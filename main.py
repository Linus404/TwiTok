from datetime import datetime, timedelta
import youtube_dl as ydl
from telegram import Bot
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
        print(f"\n\n[MAIN] Der Ordner {path} (3d ago) wurde gelöscht.")
    else:
        print(f"\n\n[MAIN] Der Ordner {path} (3d ago) ist nicht vorhanden und wurde gegebenfalls schon gelöscht.")
#endregion

#region Download
def my_hook(d):
    if d['status'] == 'finished':
        print('[YDL] Done downloading')

def title_filter(info_dict):
    title = info_dict.get('title', '')
    if all(ord(char) < 128 for char in title):
        info_dict['title'] = title.rstrip()
        return None
    else:
        video_title = unicodedata.normalize('NFKD', title).encode('ASCII', 'ignore').decode('ASCII')
        info_dict['title'] = video_title.rstrip()
        return None

def download(clip_list: list):
    with ydl.YoutubeDL({
        'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        'quiet': True,
        'no_warnings': True,
        'progress_hooks': [my_hook],
        'outtmpl': f"/Videos/{datetime.now().date()}_{timewindow}/%(title)s.%(ext)s",
        'match_filter': title_filter
    }) as ydlo:
        ydlo.download(clip_list)
#endregion

#region Telegram
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

def add_subtitles(language) -> None:
    video_dir = os.path.join("Videos", f"{var_folder}_{timewindow}")
    for video_file in os.listdir(video_dir):
        if video_file.endswith(".mp4") and "_merged" not in video_file:
            video_name = os.path.splitext(video_file)[0]
            if not os.path.exists(os.path.join(video_dir, f"{video_name}_merged.mp4")):
                try:
                    add_subs(f"{var_folder}_{timewindow}", video_name, language)
                    rmv_wtrmrk(video_dir, video_name)
                except Exception as e:
                    logger.warning(f"Error adding Subtitles: {e}")
                else:
                    print(f"Finished adding Subtitles to {video_name}.")
                    print("-------------------------------------------\n")

    os.chdir(os.path.join(base_folder, video_dir))
    del_list = glob.glob("*_subed.mp4")
    for file in del_list:
        os.remove(file)


def main(game: str, num_clips: int, timewindow: str, subtitles: bool):
    url = f"https://www.twitch.tv/directory/category/{game}/clips?range={timewindow}"
    video_dir = f"{var_folder}_{timewindow}"

    clean_up()

    clip_list = get_clip_data(num_clips, url)
    download(clip_list)
    add_subtitles("en")
    #asyncio.run(send(os.path.join(base_folder, "Videos", video_dir)))

    """if not subtitles:
        Send all videos
    else:
        Send all videos with buttons
        Add subtitles
        Send merged videos
    """
if __name__ == '__main__':
    game = "league-of-legends"
    num_clips = 1
    timewindow = "30d"
    subtitles = True

    main(game, num_clips, timewindow, subtitles)