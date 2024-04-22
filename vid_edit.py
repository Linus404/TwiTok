from subsai import *
from moviepy.editor import TextClip, CompositeVideoClip, VideoFileClip

def generate_subtitles(vid_file, language):
    subs_ai = SubsAI()
    tools = Tools()

    model = subs_ai.create_model('openai/whisper', {'model_type': 'base'})
    subs = subs_ai.transcribe(vid_file, model)
    #tsubs = tools.translate(subs, language, 'english')

    return subs


from moviepy.editor import TextClip, CompositeVideoClip, VideoFileClip
import pysrt

def add_subtitles(vid_file, subtitles):
    video = VideoFileClip(vid_file)

    subtitle_clips = []

    for sub in subtitles:
        start = sub.start / 1000  # Convert start time from milliseconds to seconds
        end = sub.end / 1000  # Convert end time from milliseconds to seconds
        text = sub.text
        subtitle_clip = TextClip(txt=text, fontsize=60, font='Cooper-Black', color='purple')
        subtitle_clip = subtitle_clip.set_position(('center', 0.8), relative=True)

        subtitle_clip = subtitle_clip.set_start(start).set_end(end)
        subtitle_clips.append(subtitle_clip)

    final_clips = [video] + subtitle_clips
    final_clip = CompositeVideoClip(final_clips)

    return final_clip