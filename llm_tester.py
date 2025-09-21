import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up API key
# Configure Gemini API
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

response = model.generate_content(
    """You're a motorsport expert with deep appreciation for driving skill, longevity, and adaptability.
Answer this like a real fan who knows why Fernando Alonso is the greatest of all time in Formula 1.
User: Who's the GOAT of F1?
Assistant:"""
)
# Print the result
print(response.text)