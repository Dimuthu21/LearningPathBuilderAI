from gemini_agent import generate_learning_path

# Ask Gemini to generate a roadmap for this topic
topic = "Learn Python for Data Science"
result = generate_learning_path(topic)

# Show the roadmap
print(result)
