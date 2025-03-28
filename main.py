import requests
from collections import defaultdict

repo_path = "owner/name"
token = "your-github-token"  # For private repositorys

user_commit_count = defaultdict(int)


def fetch_all_pages(url, source):
    page = 1
    while True:
        paged_url = f"{url}&page={page}"
        response = requests.get(paged_url, headers={"Authorization": f"token {token}"})

        if response.status_code != 200:
            print(f"Error fetching commits: {response.status_code}, {response.text}")
            break

        commits = response.json()
        if not commits:
            break

        if source != "pull request":
            print(f"Gathering {len(commits)} commits from {source} (Page {page})")

        with open("commit_messages.txt", "a", encoding="utf8") as file:
            for commit in commits:
                author = commit["commit"]["author"].get("name", "Unknown")
                user_commit_count[author] += 1
                file.write(commit["commit"]["message"] + "\n")

        page += 1


repo_info = requests.get(f"https://api.github.com/repos/{repo_path}", headers={"Authorization": f"token {token}"})
if repo_info.status_code == 200:
    default_branch = repo_info.json()["default_branch"]
    fetch_all_pages(f"https://api.github.com/repos/{repo_path}/commits?sha={default_branch}&per_page=100",
                    default_branch)
else:
    print(f"Error fetching repository info: {repo_info.status_code}, {repo_info.text}")

pulls_response = requests.get(f"https://api.github.com/repos/{repo_path}/pulls?state=closed&per_page=100",
                              headers={'Authorization': f'token {token}'})
if pulls_response.status_code == 200:
    pull_requests = pulls_response.json()
    pr_count = len(pull_requests)
    print(f"Gathering commits from {pr_count} pull requests")
    for pr in pull_requests:
        fetch_all_pages(pr["commits_url"] + "?per_page=100", "pull request")
else:
    print(f"Error fetching pull requests: {pulls_response.status_code}, {pulls_response.text}")

print()
for user, count in user_commit_count.items():
    print(f"{user}, Commits: {count}")
