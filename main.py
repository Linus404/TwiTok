from datetime import datetime, timedelta
from scraper import get_clip_data
from langdetect import detect
import youtube_dl as ydl
from vid_edit import *
import os

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
        print(f"[MAIN] Der Ordner vom {path} (3d ago) wurde gelöscht.")
    else:
        print(f"[MAIN] Der Ordner vom {path} (3d ago) ist nicht vorhanden und wurde gegebenfalls schon gelöscht.")

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
    timewindow = "7d"
    url = f"https://www.twitch.tv/directory/category/{game}/clips?range={timewindow}"
    # Download
    num_clips = 6
    filter_lang = False # Also filters out clips which have nicknames like "LUL 5K"
    translate_subs = False

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
            'format': 'best',
            'progress_hooks': [my_hook],
            'outtmpl': f"/Videos/{datetime.now().date()}_{timewindow}/%(title)s.%(ext)s",
        }

    with ydl.YoutubeDL(ydl_opts) as ydlo:
        ydlo.download(clip_list)

    if translate_subs:
        ## Generate subtitles and merge with video
        video_dir = os.path.join("Videos", f"{datetime.now().date()}_{timewindow}")
        for video_file in os.listdir(video_dir):
            if video_file.endswith(".mp4"):
                video_path = os.path.join(video_dir, video_file)
                video_name = os.path.splitext(video_file)[0]
                language = detect(video_name)
                subtitles = generate_subtitles(video_path, language)
                final_clip = add_subtitles(video_path, subtitles)
                output_path = os.path.join(video_dir, f"{video_name}_with_subtitles.mp4")
                final_clip.write_videofile(output_path, fps=final_clip.fps)
                os.remove(video_path)  # Remove the original video without subtitles