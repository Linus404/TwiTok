from scraper import get_clip_data
import youtube_dl as ydl
from datetime import datetime, timedelta
import os

## Params
url = "https://www.twitch.tv/directory/category/league-of-legends/clips?range=24hr"
num_clips = 6

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


if __name__ == '__main__':

    clean_up()

    ## Get List of Clips from scraper.py with parameters
    clip_list = get_clip_data(num_clips, url)
    ## Create todays folder as save directory

    ## Download the Clips with ydl
    def my_hook(d):
        if d['status'] == 'finished':
            print('[YDL] Done downloading')

    ydl_opts = {
        'format': 'best',
        'progress_hooks': [my_hook],
        'outtmpl': f"/Videos/{datetime.now().date()}/%(title)s.%(ext)s"
    }

    with ydl.YoutubeDL(ydl_opts) as ydlo:
        ydlo.download(clip_list)