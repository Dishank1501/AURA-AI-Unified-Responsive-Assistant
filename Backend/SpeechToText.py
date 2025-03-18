from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait  # Added for better timing
from selenium.webdriver.support import expected_conditions as EC  # Added for waiting
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt
import time  

# Load environment variables
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en-US")  # Default to English if not set

# Define HTML Code for Speech Recognition
HtmlCode = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Voice Recognition</title>
</head>
<body>
    <button id="start">Start</button>
    <button id="end">Stop</button>
    <p id="output"></p>
    <script>
        if (!window.SpeechRecognition && !window.webkitSpeechRecognition) {{
            document.getElementById("output").innerText = "Speech recognition not supported!";
        }} else {{
            var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = "{InputLanguage}";
            recognition.continuous = false;  // Stops after speaking
            recognition.interimResults = false;  // Prevents partial words
            
            recognition.onresult = function(event) {{
                document.getElementById("output").innerText = event.results[0][0].transcript;
                console.log("Recognized:", event.results[0][0].transcript);
            }};

            recognition.onerror = function(event) {{
                console.error("Recognition Error:", event.error);
                document.getElementById("output").innerText = "Error!";
            }};

            document.getElementById("start").onclick = function() {{ 
                console.log("🎤 Starting Speech Recognition...");
                recognition.start();
            }};
            document.getElementById("end").onclick = function() {{ 
                console.log("🛑 Stopping Speech Recognition...");
                recognition.stop();
            }};
        }}
    </script>
</body>
</html>"""

# Save HTML file
html_file_path = os.path.join(os.getcwd(), "Data", "Voice.html")
os.makedirs(os.path.dirname(html_file_path), exist_ok=True)

with open(html_file_path, "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# WebDriver Configuration
chrome_options = Options()
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--allow-running-insecure-content")
chrome_options.add_argument("--disable-web-security")
chrome_options.add_argument("--unsafely-treat-insecure-origin-as-secure=file://")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Load Voice Recognition HTML
Link = f"file:///{html_file_path}"

# Function to modify the query (add punctuation)
def QueryModifier(Query):
    if not Query:
        return ""
    Query = Query.strip().lower()
    if Query[-1] not in ['.', '?', '!']:
        Query += "?"
    return Query.capitalize()

# Function to translate text
def UniversalTranslator(Text):
    try:
        return mt.translate(Text, "en", "auto").capitalize()
    except:
        return Text.capitalize()

# Function to perform speech recognition
def SpeechRecognition():
    driver.get(Link)  
    time.sleep(1)  # Allow time for page load

    try:
        # Click 'Start' button
        start_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "start"))
        )
        start_button.click()
        
        print("🎤 Listening...")

        # Wait for speech to be recognized
        Text = ""
        timeout = 10  # 10 seconds max wait time
        elapsed_time = 0

        while elapsed_time < timeout:
            try:
                Text = driver.find_element(By.ID, "output").text
                if Text and Text.lower() != "error!":
                    print(f"🗣 Recognized Speech: {Text}")
                    break
            except Exception:
                pass
            time.sleep(1)
            elapsed_time += 1

        # Stop recognition
        driver.find_element(By.ID, "end").click()

        # If nothing was recognized
        if not Text:
            print("⚠ No speech detected within timeout.")
            return ""

        # Process text
        if "en" in InputLanguage.lower():
            return QueryModifier(Text)
        else:
            return QueryModifier(UniversalTranslator(Text))

    except Exception as e:
        print("❌ Speech recognition error:", str(e))
        return ""

# Run and test
if __name__ == "__main__":
    while True:
        result = SpeechRecognition()
        if result:
            print(f"✅ Final Query: {result}")
