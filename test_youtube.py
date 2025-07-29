from youtube_tool import search_youtube

# Test topic
topic = "Learn Python for Data Science"

# Get video results
results = search_youtube(topic)

# Print the top 5 videos
print("\nTop 5 YouTube tutorials:\n")
for title, url in results:
    print(f"{title}\n→ {url}\n")
