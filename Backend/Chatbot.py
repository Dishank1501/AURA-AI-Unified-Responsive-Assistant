from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

# Load environment variables from the .env file
env_vars = dotenv_values(".env")

# Retrieve API keys and names
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Check if API key is available
if not GroqAPIKey:
    raise ValueError("Error: Missing Groq API Key! Please check your .env file.")

# Initialize Groq API client
client = Groq(api_key=GroqAPIKey)

# Define system message
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

# Define system instructions
SystemChatBot = [{"role": "system", "content": System}]

# Initialize chat log file
chat_log_file = "Data/ChatLog.json"
try:
    with open(chat_log_file, "w") as f:
        dump([], f, indent=4)
except Exception as e:
    print(f"Error initializing chat log: {e}")

# Function to retrieve real-time information
def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    return f"""Please use this real-time information if needed:
    Day: {current_date_time.strftime("%A")}
    Date: {current_date_time.strftime("%d")}
    Month: {current_date_time.strftime("%B")}
    Year: {current_date_time.strftime("%Y")}
    Time: {current_date_time.strftime("%H")} hours {current_date_time.strftime("%M")} minutes {current_date_time.strftime("%S")} seconds.
    """

# Function to modify chatbot's response for better formatting
def AnswerModifier(Answer):
    return "\n".join(line.strip() for line in Answer.split("\n") if line.strip())

# Main chatbot function to handle user queries
def ChatBot(query):
    """Sends the user's query to the chatbot and returns the AI's response."""
    try:
        # Load existing chat log
        with open(chat_log_file, "r") as f:
            messages = load(f)

        # Append user query
        messages.append({"role": "user", "content": query})

        # Make a request to the Groq API for a response
        completion = client.chat.completions.create(
            model="llama3-70b-8192",  # Specify AI model
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,  # Limit response length
            temperature=0.7,  # Adjust creativity level
            top_p=1,  # Use nucleus sampling
            stream=True,  # Enable response streaming
            stop=None  # Allow model to determine stopping point
        )

        # Process streamed response correctly
        Answer = ""
        for chunk in completion:
            delta_content = chunk.choices[0].delta.content
            if delta_content:
                Answer += delta_content

        # Clean up unwanted tokens
        Answer = Answer.replace("</s>", "")

        # Append chatbot response to messages
        messages.append({"role": "assistant", "content": Answer})

        # Save updated chat log
        with open(chat_log_file, "w") as f:
            dump(messages, f, indent=4)

        # Return formatted response
        return AnswerModifier(Answer)

    except Exception as e:
        print(f"Error: {e}")

        # Reset chat log on error
        with open(chat_log_file, "w") as f:
            dump([], f, indent=4)

        return "An error occurred. Please try again."

# Main program entry point
if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ")  # Prompt user for input
        print(ChatBot(user_input))  # Print chatbot's response
