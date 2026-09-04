import asyncio
import edge_tts
import os
from lesson_parser import clean_lesson

async def text_to_audio(text, output_file):
    
    voice = "en-US-GuyNeural"
    communicator = edge_tts.Communicate(text, voice)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    await communicator.save(output_file)
    print(f"[+] Audio successfully created: {output_file}")

if __name__ == "__main__":
    lessons = clean_lesson()
    first_lesson_text = lessons[0]["speech"]
    print("Generating voiceover for Concept 1...")
    asyncio.run(text_to_audio(first_lesson_text, "output/lesson_01.mp3"))
    