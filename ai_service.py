import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Use correct model
model = genai.GenerativeModel("gemini-1.5-flash")


def ask_gemini(prompt: str) -> str:
    """
    Sends prompt to Gemini AI and returns response text.
    """

    try:
        response = model.generate_content(prompt)

        # Gemini returns structured response
        return response.text

    except Exception as e:
        return f"AI Error: {str(e)}"
