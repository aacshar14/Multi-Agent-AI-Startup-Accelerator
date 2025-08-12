# Create a new file: tools/image_tool.py
import os
import requests
from crewai.tools import BaseTool

class ImageGenerationTool(BaseTool):
    name: str = "DALL-E 3 Image Generator"
    description: str = "Generates an image from a detailed text prompt using the DALL-E 3 model. Returns the URL of the generated image."

    def _run(self, prompt: str) -> str:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return "Error: OPENAI_API_KEY environment variable not set."

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "dall-e-3",
            "prompt": f"A clean, modern, minimalist logo for a tech startup. The logo should be on a plain white background. The prompt is: '{prompt}'",
            "n": 1,
            "size": "1024x1024"
        }

        try:
            response = requests.post("https://api.openai.com/v1/images/generations", headers=headers, json=data)
            response.raise_for_status()
            image_url = response.json()['data'][0]['url']
            return f"Image generated successfully. Here is the URL: {image_url}"
        except Exception as e:
            return f"Error generating image: {e}"