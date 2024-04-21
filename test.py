import youtube_dl
from langdetect import detect

# Define the filter function
def title_filter(info_dict):
    # Check if the video title is in English or German
    title = info_dict.get('title', '')
    language = detect(title)
    if language == 'en' or language == 'de':
        return None
    else:
        video_title = info_dict.get('title', info_dict.get('id', 'video'))
        return '%s is probably not in your target language, skipping ..' % video_title

# Set up youtube_dl options
ydl_opts = {
    'format': 'best',
    'match_filter': title_filter
}

# Initialize YoutubeDL with options
ydl = youtube_dl.YoutubeDL(ydl_opts)

# URL of a Twitch clip
clip_url = 'https://www.twitch.tv/recrent/clip/RelatedGoodBarracudaBudStar-vWSXBoL7CcITXsLr'

# Download video
ydl.download([clip_url])