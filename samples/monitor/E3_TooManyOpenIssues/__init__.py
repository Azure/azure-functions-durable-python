import requests
import json

def main(repoID: str) -> str:

    # We use the GitHub API to count the number of open issues in the repo provided
    # Note that the GitHub API only displays at most 30 issues per response, so
    # the maximum number this activity will return is 30. That's enough for demo'ing purposes.
    [user, repo] = repoID.split("/")
    url = f"https://api.github.com/repos/{user}/{repo}/issues?state=open"
    res = requests.get(url)
    if res.status_code != 200:
        error_message = f"Could not find repo {user} under {repo}! API endpoint hit was: {url}"
        raise Exception(error_message)
    issues = json.loads(res.text)
    too_many_issues: bool = len(issues) >= 3
    return too_many_issues