import os
import subsai
import torchaudio
import subprocess
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
from moviepy.editor import TextClip, CompositeVideoClip, VideoFileClip

def generate_subtitles(vid_file, language):
    subs_ai = subsai.SubsAI()
    tools = subsai.Tools()

    model_id = "facebook/seamless-m4t-v2-large"
    processor = AutoProcessor.from_pretrained(model_id)
    model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id)

    # Extract audio from video file and temporarily save it
    command = f"ffmpeg -i {vid_file} -vn -ar 16000 -ac 1 -c:a pcm_s16le temp_audio.wav"
    subprocess.call(command, shell=True)

    audio = torchaudio.load("temp_audio.wav")

    audio_inputs = processor(audios=audio, return_tensors="pt")

    output = model.generate(**audio_inputs, tgt_lang="en")[0].cpu().numpy().squeeze(0)
    transcription = processor.batch_decode(output, skip_special_tokens=True)[0]

    # Uncomment this line if you want to translate the transcription to another language
    # tsubs = tools.translate(transcription, language, 'english')

    # Remove the audio file
    os.remove("temp_audio.wav")

    return transcription


def add_subtitles(vid_file, subtitles):
    video = VideoFileClip(vid_file)

    subtitle_clips = []

    for sub in subtitles:
        start = sub.start / 1000  # Convert start time from milliseconds to seconds
        end = sub.end / 1000  # Convert end time from milliseconds to seconds
        text = sub.text
        subtitle_clip = TextClip(txt=text, fontsize=60, font='Cooper-Black', color='white')
        subtitle_clip = subtitle_clip.set_position(('center', 0.8), relative=True)

        subtitle_clip = subtitle_clip.set_start(start).set_end(end)
        subtitle_clips.append(subtitle_clip)

    final_clips = [video] + subtitle_clips
    final_clip = CompositeVideoClip(final_clips)

    return final_clip


video_path = "E:/Code/Projects/TwitchClip/Videos/2024-04-22_all/HAHAHAHHAHAHAHAH.mp4"
language = "en"  # Set the desired language code for translation

subtitles = generate_subtitles(video_path, language)
final_clip = add_subtitles(video_path, subtitles)
final_clip.write_videofile("output_video_with_subtitles.mp4")