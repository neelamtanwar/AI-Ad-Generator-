# agent/video_gen.py
#
# HOW IT WORKS (100% free):
# Real video generation APIs cost money, so we build a "video" from:
#   1. The flyer image (static background)
#   2. gTTS voiceover audio (Google Text-to-Speech, completely free)
#   3. MoviePy to combine them into an .mp4 file
#
# The result is a professional-looking "talking ad" —
# your flyer image on screen with a voiceover playing over it.
# This is actually how many social media video ads are structured.
#
# KEY CONCEPT — MoviePy:
# MoviePy treats video as a timeline of clips.
# ImageClip creates a video clip from a still image.
# AudioFileClip loads an audio file.
# .set_audio() attaches audio to a video clip.
# .write_videofile() renders everything to an mp4.

import os
import tempfile
import numpy as np
from gtts import gTTS
from PIL import Image
import moviepy.editor as mp

def validate_script(script: str) -> None:
    """Validate that script is non-empty."""
    if not isinstance(script, str) or not script.strip():
        raise ValueError("Script must be a non-empty string")


def validate_flyer_image(flyer_img) -> None:
    """Validate that flyer_img is a PIL Image."""
    if not isinstance(flyer_img, Image.Image):
        raise TypeError(f"flyer_img must be a PIL Image, got {type(flyer_img)}")


def generate_voiceover(script: str) -> str:
    """
    Converts text to speech using gTTS (Google Text-to-Speech).
    Free, no API key needed — uses Google's public TTS endpoint.
    Returns the path to a temporary .mp3 file.
    
    gTTS sends your text to Google's servers and streams back audio.
    lang="en" = English, slow=False = normal speaking speed.
    Raises ValueError if script is invalid or gTTS fails.
    """
    validate_script(script)
    
    try:
        tts = gTTS(text=script, lang="en", slow=False)
    except Exception as e:
        raise ValueError(f"gTTS failed to generate voiceover: {e}")
    
    # Save to a temporary file (OS handles cleanup)
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    try:
        tts.save(tmp.name)
    except Exception as e:
        tmp.close()
        os.unlink(tmp.name)
        raise ValueError(f"Failed to save voiceover: {e}")
    tmp.close()
    return tmp.name


def create_video_ad(flyer_img: Image.Image, script: str) -> str:
    """
    Creates an mp4 video ad from a PIL image and a script string.
    
    Process:
    1. Generate voiceover audio from the script
    2. Convert the PIL image to a numpy array (MoviePy needs this format)
    3. Create a video clip from the image, lasting as long as the audio
    4. Attach the audio to the video clip
    5. Render to mp4 and return the file path
    
    Returns: path to the output .mp4 file
    Raises TypeError if flyer_img is not a PIL Image, ValueError for other errors.
    """
    # Validate inputs
    validate_flyer_image(flyer_img)
    validate_script(script)
    
    audio_path = None
    audio_clip = None
    video_clip = None
    
    try:
        # Step 1 — Generate audio
        audio_path = generate_voiceover(script)

        # Step 2 — Convert PIL image to numpy array
        # MoviePy's ImageClip expects a numpy array of shape (H, W, 3) with uint8 values
        img_array = np.array(flyer_img.convert("RGB"))

        # Step 3 — Load audio to find its duration
        audio_clip = mp.AudioFileClip(audio_path)
        duration = audio_clip.duration  # in seconds (usually 25-35s for a 75-word script)
        
        # Validate duration is reasonable
        if duration <= 0:
            raise ValueError(f"Audio duration must be > 0, got {duration}s")
        if duration > 300:  # max 5 minutes
            raise ValueError(f"Audio duration too long: {duration}s (max 300s)")

        # Step 4 — Create a video clip from the still image
        # duration= makes the image last exactly as long as the audio
        video_clip = mp.ImageClip(img_array, duration=duration)
        video_clip = video_clip.set_fps(24)  # 24 frames per second is cinema standard

        # Step 5 — Attach audio to video
        final_clip = video_clip.set_audio(audio_clip)

        # Step 6 — Render to mp4 (use NamedTemporaryFile for safety)
        output_tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        output_path = output_tmp.name
        output_tmp.close()
        
        temp_audio_tmp = tempfile.NamedTemporaryFile(suffix=".m4a", delete=False)
        temp_audio_path = temp_audio_tmp.name
        temp_audio_tmp.close()
        
        try:
            final_clip.write_videofile(
                output_path,
                codec="libx264",           # H.264 video codec — universal compatibility
                audio_codec="aac",        # AAC audio — works everywhere
                logger=None,              # suppress verbose MoviePy output
                temp_audiofile=temp_audio_path,
            )
        finally:
            # Cleanup temp audio file
            if os.path.exists(temp_audio_path):
                os.unlink(temp_audio_path)
        
        # Verify output file was created
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            raise ValueError(f"Video file not created or is empty: {output_path}")
        
        return output_path
        
    finally:
        # Cleanup resources
        if video_clip is not None:
            video_clip.close()
        if audio_clip is not None:
            audio_clip.close()
        if audio_path is not None and os.path.exists(audio_path):
            os.unlink(audio_path)