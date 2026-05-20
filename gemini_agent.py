import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Generate roadmap
def generate_learning_path(topic):

    prompt = f"""
    You are a professional mentor. Please create a personalized weekly learning roadmap for the topic: "{topic}".

    Include:
    - Weekly breakdown
    - Subtopics to learn each week
    - Suggested resources
    - Clear and simple structure

    Format it in clean markdown.
    """

    model = genai.GenerativeModel("models/gemini-1.5-flash")

    response = model.generate_content(prompt)

    return response.text