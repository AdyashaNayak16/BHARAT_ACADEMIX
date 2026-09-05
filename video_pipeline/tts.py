import asyncio
import edge_tts
import os
import re

VOICE_MAP = {
    "English": "en-IN-NeerjaNeural",
    "English (US)": "en-US-GuyNeural",
    "Hindi": "hi-IN-MadhurNeural",
    "Hinglish": "hi-IN-MadhurNeural",
    "Bengali": "bn-IN-BashkarNeural",
    "Tamil": "ta-IN-ValluvarNeural",
    "Telugu": "te-IN-MohanNeural",
    "Marathi": "mr-IN-ManoharNeural",
    "Gujarati": "gu-IN-NiranjanNeural",
    "Kannada": "kn-IN-GaganNeural"
}

def clean_for_speech(text: str) -> str:
    """Clean markdown and code blocks for clean TTS pronunciation."""
    # Remove code blocks
    text = re.sub(r"```[\s\S]*?```", " As shown on the slide. ", text)
    # Remove inline backticks
    text = re.sub(r"`([^`]+)`", r"\1", text)
    # Remove markdown headers and formatting
    text = re.sub(r"[#*_~>]+", " ", text)
    # Clean whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text

async def text_to_audio(text: str, output_file: str, language: str = "English", voice_override: str = None):
    voice = voice_override or VOICE_MAP.get(language, "en-IN-NeerjaNeural")
    clean_text = clean_for_speech(text)
    if not clean_text:
        clean_text = "Let's move on to the next concept."
    communicator = edge_tts.Communicate(clean_text, voice)
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    await communicator.save(output_file)
    print(f"[+] Audio successfully created: {output_file} (Voice: {voice})")
    return output_file

def generate_speech_sync(text: str, output_file: str, language: str = "English", voice_override: str = None):
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(text_to_audio(text, output_file, language, voice_override))
        else:
            return asyncio.run(text_to_audio(text, output_file, language, voice_override))
    except Exception as e:
        print(f"[-] TTS Error: {e}")
        # Try fallback using a dedicated thread loop
        try:
            import threading
            result_holder = []
            def runner():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                res = new_loop.run_until_complete(text_to_audio(text, output_file, language, voice_override))
                result_holder.append(res)
                new_loop.close()
            t = threading.Thread(target=runner)
            t.start()
            t.join(timeout=10)
            return result_holder[0] if result_holder else None
        except Exception as e2:
            print(f"[-] TTS Thread Fallback Error: {e2}")
            return None

if __name__ == "__main__":
    from lesson_parser import clean_lesson
    lessons = clean_lesson()
    first_lesson_text = lessons[0]["speech"]
    print("Generating voiceover for Concept 1...")
    asyncio.run(text_to_audio(first_lesson_text, "output/lesson_01.mp3", language="English"))