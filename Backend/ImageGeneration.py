import asyncio
import os
import requests
from random import randint
from PIL import Image
from dotenv import dotenv_values
from time import sleep

# Load environment variables
env_vars = dotenv_values(".env")
HuggingFaceAPIKey = env_vars.get("HuggingFaceAPIKey")

if not HuggingFaceAPIKey:
    raise ValueError("Missing HuggingFaceAPIKey in .env file")

# API details for the Hugging Face Stable Diffusion model
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
HEADERS = {"Authorization": f"Bearer {HuggingFaceAPIKey}"}

# Function to open and display images based on a given prompt
def open_images(prompt):
    folder_path = r"Data"  # Folder where the images are stored
    prompt = prompt.replace(" ", "_")  # Replace spaces in prompt with underscores

    files = [os.path.join(folder_path, f"{prompt}{i}.jpg") for i in range(1, 5)]

    for image_path in files:
        if os.path.exists(image_path):  # Check if the file exists
            try:
                img = Image.open(image_path)
                print(f"Opening image: {image_path}")
                img.show()
                sleep(1)  # Pause before showing the next image
            except IOError:
                print(f"Unable to open {image_path}")
        else:
            print(f"Image not found: {image_path}")

# Async function to send a query to the Hugging Face API
async def query(payload):
    try:
        response = await asyncio.to_thread(requests.post, API_URL, headers=HEADERS, json=payload)
        
        if response.status_code != 200:
            return f"API Error {response.status_code}: {response.text}"

        return response.content
    except requests.exceptions.RequestException as e:
        return f"Request Error: {str(e)}"

# Async function to generate images based on the given prompt
async def generate_images(prompt: str):
    tasks = []
    prompt_clean = prompt.replace(" ", "_")

    # Ensure the Data folder exists
    os.makedirs("Data", exist_ok=True)

    for i in range(1, 5):
        payload = {
            "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}"
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    image_bytes_list = await asyncio.gather(*tasks)

    # Save generated images
    for i, image_bytes in enumerate(image_bytes_list):
        if isinstance(image_bytes, bytes):  # Ensure valid image data
            file_path = os.path.join("Data", f"{prompt_clean}{i+1}.jpg")
            with open(file_path, "wb") as f:
                f.write(image_bytes)
        else:
            print(f"Image {i+1} generation failed: {image_bytes}")

# Wrapper function to generate and open images
def GenerateImages(prompt: str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(generate_images(prompt))
    loop.close()

    open_images(prompt)

# Main loop to monitor for image generation requests
def monitor_file():
    file_path = r"Frontend\Files\ImageGeneration.data"

    while True:
        try:
            # Read the status and prompt from the data file
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    data = f.read().strip()

                if data:
                    parts = data.split(",")
                    if len(parts) == 2:
                        prompt, status = parts[0].strip(), parts[1].strip().lower()
                        
                        if status == "true":
                            print("Generating Images ...")
                            GenerateImages(prompt)

                            # Reset the status after generating images
                            with open(file_path, "w") as f:
                                f.write("False, False")

            sleep(1)  # Wait before checking again

        except Exception as e:
            print(f"Error: {str(e)}")
            sleep(1)  # Prevent rapid error loops

# Run the file monitor
if __name__ == "__main__":
    monitor_file()
