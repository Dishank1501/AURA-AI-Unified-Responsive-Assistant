import datetime  # For real-time date and time information.
from dotenv import dotenv_values  # To read environment variables from a .env file.
from googlesearch import search
from groq import Groq  # For Groq API integration.
from json import load, dump  # For handling JSON files.
import requests  # For error handling in network requests

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize the Groq client
client = Groq(api_key=GroqAPIKey)

# Define chatbot system instructions
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***"""

# Load or create chat log
try:
    with open("Data/ChatLog.json", "r") as f:
        messages = load(f)
except (FileNotFoundError, ValueError):
    messages = []
    with open("Data/ChatLog.json", "w") as f:
        dump([], f)

# Function to perform a Google search
def GoogleSearch(query):
    try:
        print(f"Performing search for: {query}")
        results = list(search(query, num_results=5))  # Only URLs returned
        
        if not results:
            return "No relevant search results found."

        Answer = f"The search results for '{query}' are:\n[start]\n"
        for url in results:
            Answer += f"URL: {url}\n\n"
        Answer += "[end]"

        return Answer
    except requests.exceptions.HTTPError as e:
        return f"HTTP Error: {e.response.status_code} - {e.response.reason}"
    except requests.exceptions.RequestException as e:
        return f"Network Error: {str(e)}"
    except Exception as e:
        return f"Unexpected Error: {str(e)}"

# Function to clean up the answer
def AnswerModifier(Answer):
    return '\n'.join([line for line in Answer.split('\n') if line.strip()])

# System message and chatbot initialization
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

# Function to get real-time information
def Information():
    current_date_time = datetime.datetime.now()
    return f"Use this real-time information if needed:\nDay: {current_date_time.strftime('%A')}\nDate: {current_date_time.strftime('%d')}\nMonth: {current_date_time.strftime('%B')}\nYear: {current_date_time.strftime('%Y')}\nTime: {current_date_time.strftime('%H:%M:%S')}."

# Function to handle real-time search and response generation
def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    # Load chat log
    try:
        with open("Data/ChatLog.json", "r") as f:
            messages = load(f)
    except (FileNotFoundError, ValueError):
        messages = []

    messages.append({"role": "user", "content": prompt})

    # Perform Google search and add results to chatbot messages
    search_results = GoogleSearch(prompt)
    SystemChatBot.append({"role": "system", "content": search_results})

    # Generate response using Groq API
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=True,
            stop=None
        )

        # Extract response content
        Answer = ""
        for chunk in completion:
            if hasattr(chunk.choices[0].delta, "content"):
                Answer += chunk.choices[0].delta.content or ""

        Answer = Answer.strip().replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})

        # Save updated chat log
        with open("Data/ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        # Remove the latest system message
        SystemChatBot.pop()

        return AnswerModifier(Answer)
    except Exception as e:
        return f"AI Response Error: {str(e)}"

# Main entry point for user interaction
if __name__ == "__main__":
    while True:
        try:
            prompt = input("Enter your query: ")
            if prompt.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            print(RealtimeSearchEngine(prompt))
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
