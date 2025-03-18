import os
import asyncio
import edge_tts
import pygame
import webbrowser
import subprocess
import requests
import keyboard
from AppOpener import close, open as appopen
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import pywhatkit

# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")
AssistantVoice = env_vars.get("AssistantVoice")

# Initialize the Groq AI client
client = Groq(api_key=GroqAPIKey)

# 🚀 Automation Class
class Automation:
    def __init__(self):
        print("Automation class initialized!")

    async def text_to_audio_file(self, text):
        """ Convert text to an audio file using edge_tts """
        file_path = "Data/speech.mp3"
        if os.path.exists(file_path):
            os.remove(file_path)
        communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%')
        await communicate.save(file_path)

    def TTS(self, text):
        """ Text-to-Speech playback """
        asyncio.run(self.text_to_audio_file(text))
        pygame.mixer.init()
        pygame.mixer.music.load("Data/speech.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.quit()

    def content_writer_ai(self, prompt):
        """ Generate AI content using Groq API """
        messages = [{"role": "user", "content": prompt}]
        completion = client.chat.completions.create(
            model="mixtral-8×7b-32768",
            messages=messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True
        )
        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content
        return answer.replace("</s>", "")

    def generate_content(self, topic):
        """ Generate AI-written content and save it as a text file """
        content = self.content_writer_ai(topic)
        file_path = f"Data/{topic.lower().replace(' ', '_')}.txt"
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        subprocess.Popen(["notepad.exe", file_path])

    def google_search(self, topic):
        """ Perform a Google search """
        pywhatkit.search(topic)

    def youtube_search(self, topic):
        """ Perform a YouTube search """
        url = f"https://www.youtube.com/results?search_query={topic}"
        webbrowser.open(url)

    def play_youtube(self, query):
        """ Play a YouTube video """
        pywhatkit.playonyt(query)

    def open_app(self, app):
        """ Open an application """
        try:
            appopen(app, match_closest=True)
        except:
            print(f"Could not open {app}")

    def close_app(self, app):
        """ Close an application """
        try:
            close(app)
        except:
            print(f"Could not close {app}")

    def system_command(self, command):
        """ Execute system commands like volume control """
        commands = {
            "mute": lambda: keyboard.press_and_release("volume mute"),
            "unmute": lambda: keyboard.press_and_release("volume mute"),
            "volume up": lambda: keyboard.press_and_release("volume up"),
            "volume down": lambda: keyboard.press_and_release("volume down")
        }
        if command in commands:
            commands[command]()

    def extract_links(self, html):
        """ Extract Google search result links """
        if html is None:
            return []
        soup = BeautifulSoup(html, 'html.parser')
        return [link.get('href') for link in soup.find_all('a', {'jsname': 'UWckNb'})]

    def search_google(self, query):
        """ Perform a web search """
        url = f"https://www.google.com/search?q={query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None

    async def translate_and_execute(self, commands):
        """ Process and execute user commands """
        tasks = []
        for command in commands:
            if command.startswith("open"):
                tasks.append(asyncio.to_thread(self.open_app, command.removeprefix("open ")))
            elif command.startswith("close"):
                tasks.append(asyncio.to_thread(self.close_app, command.removeprefix("close ")))
            elif command.startswith("play"):
                tasks.append(asyncio.to_thread(self.play_youtube, command.removeprefix("play ")))
            elif command.startswith("content"):
                tasks.append(asyncio.to_thread(self.generate_content, command.removeprefix("content ")))
            elif command.startswith("google search"):
                tasks.append(asyncio.to_thread(self.google_search, command.removeprefix("google search ")))
            elif command.startswith("youtube search"):
                tasks.append(asyncio.to_thread(self.youtube_search, command.removeprefix("youtube search ")))
            elif command.startswith("system"):
                tasks.append(asyncio.to_thread(self.system_command, command.removeprefix("system ")))
            else:
                print(f"No function found for: {command}")
        await asyncio.gather(*tasks)

    async def automation(self, commands):
        """ Run automation tasks """
        await self.translate_and_execute(commands)
        return True

# 🔥 Main Execution
if __name__ == "__main__":
    bot = Automation()  # Initialize the Automation class
    while True:
        command = input("Enter command: ")
        asyncio.run(bot.automation([command]))
