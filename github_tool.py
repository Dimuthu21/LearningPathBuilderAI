import requests

def search_github_repos(topic):
    # 1. Build the GitHub search URL
    url = f"https://api.github.com/search/repositories?q={topic}&sort=stars&order=desc&per_page=5"

    # 2. Set headers (optional)
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }

    # 3. Send GET request to GitHub
    response = requests.get(url, headers=headers)

    # 4. Parse JSON response
    data = response.json()

    # 5. Extract top 5 repo names + links
    results = []
    for repo in data.get("items", []):
        full_name = repo["full_name"]  # e.g., "pallets/flask"
        html_url = repo["html_url"]
        results.append((full_name, html_url))

    return results
