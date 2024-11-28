from moviepy.editor import AudioFileClip


def extract_audio(input_video_path, output_audio_path="output_audio.wav"):
    audio_clip = AudioFileClip(input_video_path)
    audio_clip.write_audiofile(output_audio_path)
    audio_clip.close()

    print(f"Audio saved as {output_audio_path}")
    return output_audio_path
