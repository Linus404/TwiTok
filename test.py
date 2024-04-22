from subsai import *
import moviepy.editor as mp
import pysrt
from datetime import timedelta

def generate_subtitles(vid_file, name, lang):
    ## Init
    subs_ai = SubsAI()
    tools = Tools()

    model = subs_ai.create_model('openai/whisper', {'model_type': 'base'})
    subs = subs_ai.transcribe(vid_file, model)
    tsubs = tools.translate(
        subs,
        f'{lang}',
        'english'
    )
    tsubs.save(f'{name}.srt')

    return None

def add_subtitles(vid_file, name):
    video = mp.VideoFileClip(vid_file)

    subtitles = pysrt.open(f"{name}.srt")
    subtitle_clips = []

    for sub in subtitles:
        start = sub.start.to_time()
        end = sub.end.to_time()
        text = sub.text
        subtitle_clip = mp.TextClip(txt=text, fontsize=24, font='Arial', color='white')
        subtitle_clip = subtitle_clip.set_position(('center', 0.8), relative=True)
        
        # Convert start and end times to seconds
        start_seconds = (start.hour * 3600 + start.minute * 60 + start.second) + start.microsecond / 1000000
        end_seconds = (end.hour * 3600 + end.minute * 60 + end.second) + end.microsecond / 1000000
        
        subtitle_clip = subtitle_clip.set_start(start_seconds).set_end(end_seconds)
        subtitle_clips.append(subtitle_clip)

    final_clips = [video] + subtitle_clips
    final_clip = mp.CompositeVideoClip(final_clips)
    final_clip.write_videofile(f"{name}_with_subtitles.mp4", fps=video.fps)
    print("++++DEBUG Saved new Video")

path = './Videos/2024-04-22_7d/Hänno ruft an ausm Krankenbett.mp4'
name = 'Hänno ruft an ausm Krankenbett'
generate_subtitles(path, name, 'german')
add_subtitles(path, name)