from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

# ✅ Load the .env file first
load_dotenv()

def search_youtube(topic):
    # ✅ Get the API key from environment
    api_key = os.getenv("YOUTUBE_API_KEY")

    # ✅ Raise error if key is missing (for safety)
    if not api_key:
        raise ValueError("YOUTUBE_API_KEY is missing. Please check your .env file.")

    # ✅ Build YouTube API client
    youtube = build("youtube", "v3", developerKey=api_key)

    # ✅ Create a search request
    request = youtube.search().list(
        part="snippet",
        q=topic,
        type="video",
        maxResults=5
    )

    # ✅ Execute the request and get response
    response = request.execute()

    # ✅ Extract and return top 5 video links
    results = []
    for item in response["items"]:
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        url = f"https://www.youtube.com/watch?v={video_id}"
        results.append((title, url))

    return results
