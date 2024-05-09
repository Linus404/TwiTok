from langdetect import detect
import youtube_dl as ydl
import os
import glob
import asyncio
from datetime import datetime, timedelta

from twitch_scraper import get_clip_data
from subs_scraper import add_subs, rmv_wtrmrk
from send_vids import sv_main



## Clear old Videos
def clean_up():
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
        print(f"[MAIN] Der Ordner {path} (3d ago) wurde gelöscht.")
    else:
        print(f"[MAIN] Der Ordner {path} (3d ago) ist nicht vorhanden und wurde gegebenfalls schon gelöscht.")

## Print when Video is finished downloading
def my_hook(d):
    if d['status'] == 'finished':
        print('[YDL] Done downloading')

## Check if the video title is in English or German
def title_filter(info_dict):
    title = info_dict.get('title', '')
    language = detect(title)
    if language == 'en' or language == 'de':
        return None
    else:
        video_title = info_dict.get('title', info_dict.get('id', 'video'))
        return '%s is probably not in your target language, skipping ..' % video_title

if __name__ == '__main__':

    ## Params
    # URL
    game = "league-of-legends"
    num_clips = 2
    timewindow = "all"
    subtitles = True
    filter_lang = False # Also filters out clips which have nicknames like "LUL 5K"

    url = f"https://www.twitch.tv/directory/category/{game}/clips?range={timewindow}"

    ## Delete the Videos and Folder from 3 days ago 
    clean_up()

    ## Get List of Clips from scraper.py with parameters
    clip_list = get_clip_data(num_clips, url)

    ## Download the Clips with ydl
    if filter_lang:
        ydl_opts = {
            'format': 'best',
            'progress_hooks': [my_hook],
            'outtmpl': f"/Videos/{datetime.now().date()}_{timewindow}/%(title)s.%(ext)s",
            'match_filter': title_filter
        }
    else: 
        ydl_opts = {
            'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
            'progress_hooks': [my_hook],
            'outtmpl': f"/Videos/{datetime.now().date()}_{timewindow}/%(title)s.%(ext)s",
        }

    with ydl.YoutubeDL(ydl_opts) as ydlo:
        ydlo.download(clip_list)

    if subtitles:
        sub_folder = datetime.now().date()
        ## Generate subtitles and merge with video
        video_dir = os.path.join("Videos", f"{datetime.now().date()}_{timewindow}")
        for video_file in os.listdir(video_dir):
            if video_file.endswith(".mp4") and "_subed" not in video_file and "_merged" not in video_file:
                video_name = os.path.splitext(video_file)[0]
                # _subed can be removed if everything works properly there should exist files with _subed
                if not os.path.exists(os.path.join(video_dir, f"{video_name}_subed.mp4")) and not os.path.exists(os.path.join(video_dir, f"{video_name}_merged.mp4")):
                    language = detect(video_name)
                    language = 'en'
                    add_subs(f"{sub_folder}_{timewindow}", video_name, language)
                    rmv_wtrmrk(video_dir, video_name)
                    print(f"Finished adding Subtitles to {video_name}.")
                    print("\n-------------------------------------------\n")

        # Delete redundant files
        os.chdir(os.path.join(".\\Videos", f"{str(sub_folder)}_{str(timewindow)}"))
        del_list = glob.glob("*_subed.mp4")
        for file in del_list:
            os.remove(file)

    asyncio.run(sv_main())