import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1️⃣ Load the Gemini API key from the .env file
load_dotenv()
genai.configure(api_key=os.getenv("AIzaSyCbO2pRB7PKVwq2Y89jp-J6utnaGCeLjpc"))

# 2️⃣ Define the function that talks to Gemini and gets a roadmap
def generate_learning_path(topic):
    prompt = f"""
    You are a professional mentor. Please create a personalized weekly learning roadmap for the topic: "{topic}".

    Include:
    - Weekly breakdown (e.g., Week 1, Week 2...)
    - Subtopics to learn each week
    - Suggested resources (books, videos, online courses)
    - Clear and simple structure

    Format it in clean markdown so I can display it nicely in a webpage.
    """

    # 3️⃣ Create the Gemini model (Gemini Pro)
    model = genai.GenerativeModel("models/gemini-1.5-flash")

    # 4️⃣ Send the prompt and get the response
    response = model.generate_content(prompt)

    # 5️⃣ Return the text content from the response
    return response.text
