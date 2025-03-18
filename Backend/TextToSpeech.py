import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values

# Load environment variables from a .env file
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice", "en-IN-PrabhatNeural")  # Indian male voice

# Define the path for saving speech audio
file_path = "Data/speech.mp3"

# Asynchronous function to convert text to an audio file
async def TextToAudioFile(text):
    if os.path.exists(file_path):  # Remove existing file to prevent issues
        os.remove(file_path)

    try:
        communicate = edge_tts.Communicate(text, AssistantVoice, pitch='-3Hz', rate='+10%')
        await communicate.save(file_path)  # Save the generated speech as an MP3 file
    except Exception as e:
        print(f"Error generating speech file: {e}")

# Function to manage Text-to-Speech (TTS) playback
def TTS(text, func=lambda r=None: True):
    try:
        asyncio.run(TextToAudioFile(text))  # Convert text to an audio file asynchronously

        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        # Loop until the audio finishes playing
        while pygame.mixer.music.get_busy():
            if func() is False:  # Check if external function returns False
                break
            pygame.time.Clock().tick(10)  # Limit loop to 10 ticks per second

        return True  # Return True if the audio played successfully

    except Exception as e:
        print(f"Error in TTS: {e}")

    finally:
        try:
            func(False)  # Signal the end of TTS
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception as e:
            print(f"Error in cleanup: {e}")

# Function to manage Text-to-Speech with handling for long text
def TextToSpeech(text, func=lambda r=None: True):
    sentences = text.split(".")  # Split the text into sentences
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out.",
        "Please check the chat screen for the remaining text.",
        "The remaining information is available in the chat.",
        "You can find the rest of the text in the chat window.",
        "Check the chat screen for the full response.",
        "The next part of the response is in the chat.",
        "More details are in the chat window.",
        "Check the chat for additional information."
    ]

    if len(sentences) > 4 and len(text) > 250:
        shortened_text = " ".join(sentences[:2]) + ". " + random.choice(responses)
        TTS(shortened_text, func)
    else:
        TTS(text, func)

# Main execution loop
if __name__ == "__main__":
    while True:
        user_input = input("Enter the text: ")
        TextToSpeech(user_input)
