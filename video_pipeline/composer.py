import os
import glob
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips

def generate_multi_slide_video(slides_dir: str, audio_path: str, output_path: str):
    # 1. Load full audio
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration

    # 2. Gather all slides in order
    slide_files = sorted(glob.glob(os.path.join(slides_dir, "slide_*.png")))
    num_slides = len(slide_files)

    if num_slides == 0:
        raise FileNotFoundError(f"No slide images found in {slides_dir}")

    # 3. Calculate display time per slide
    duration_per_slide = total_duration / num_slides
    print(f"[*] Total duration: {total_duration:.2f}s | Slides: {num_slides} | {duration_per_slide:.2f}s per slide")

    # 4. Create image clips with assigned durations
    clips = []
    for slide in slide_files:
        clip = ImageClip(slide).with_duration(duration_per_slide)
        clips.append(clip)

    # 5. Concatenate all slides into one sequence
    video_sequence = concatenate_videoclips(clips, method="compose")
    video_sequence = video_sequence.with_audio(audio)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 6. Render final composite video
    video_sequence.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        audio=True,
        temp_audiofile="output/temp_seq_audio.m4a",
        remove_temp=True
    )

    audio.close()
    video_sequence.close()
    print(f"[+] Multi-slide video ready: {output_path}")

if __name__ == "__main__":
    generate_multi_slide_video(
        slides_dir="output",
        audio_path="output/lesson_01.mp3",
        output_path="output/final_lesson_01.mp4"
    )