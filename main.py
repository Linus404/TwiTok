from scraper import get_clip_data
import youtube_dl as ydl
from datetime import datetime, timedelta
import os
from langdetect import detect

## Params
# URL
game = "league-of-legends"
timewindow = "24hr"
url = f"https://www.twitch.tv/directory/category/{game}/clips?range={timewindow}"
# Download
num_clips = 6
filter_lang = False # Also filters clips which have nicknames like "LUL 5K"

## Clear old Videos
def clean_up():
    today = datetime.now().date()
    termination = today - timedelta(days=3)
    path = os.path.join(os.path.dirname(__file__), "Videos", termination.strftime("%Y-%m-%d"))
    print(path)
    
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