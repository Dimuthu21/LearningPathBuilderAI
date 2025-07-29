from github_tool import search_github_repos

topic = "computer vision"
repos = search_github_repos(topic)

print(f"\nTop 5 GitHub repos for: {topic}\n")
for name, url in repos:
    print(f"{name} → {url}")
