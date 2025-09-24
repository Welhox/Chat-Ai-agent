# tools.py
import json, os, time
from typing import Dict, Any, List, Optional
import httpx

BIO_PATH = os.path.join("data", "bio.json")
GITHUB_API = "https://api.github.com"
GITHUB_GQL = "https://api.github.com/graphql"

def _gh_headers():
    headers = {"Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN") or ""
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def _gh_client():
    return httpx.Client(base_url=GITHUB_API, headers=_gh_headers(), timeout=30.0)

def _gql_client():
    headers = _gh_headers()
    headers["Content-Type"] = "application/json"
    return httpx.Client(base_url=GITHUB_GQL, headers=headers, timeout=30.0)
def _read_json(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _write_json(path: str, data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ---- BIO tools ----
def bio_get(keys: Optional[List[str]] = None) -> Dict[str, Any]:
    data = _read_json(BIO_PATH)
    if not keys:
        return data
    return {k: data.get(k) for k in keys}

def bio_set(update: Dict[str, Any]) -> Dict[str, Any]:
    data = _read_json(BIO_PATH)
    data.update(update or {})
    _write_json(BIO_PATH, data)
    return {"ok": True, "updated_keys": list(update.keys())}

# ---- GitHub helpers ----
def _gh_client():
    headers = {"Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN") or ""
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return httpx.Client(base_url=GITHUB_API, headers=headers, timeout=20.0)

def github_list_repos(user: Optional[str] = None) -> List[Dict[str, Any]]:
    user = user or os.getenv("GITHUB_USER", "")
    if not user:
        return []
    with _gh_client() as c:
        r = c.get(f"/users/{user}/repos", params={"per_page": 100, "sort": "updated"})
        r.raise_for_status()
        return [{"name": repo["name"], "private": repo["private"], "html_url": repo["html_url"], "description": repo.get("description")} for repo in r.json()]

def github_search_code(q: str, repo: Optional[str] = None) -> List[Dict[str, Any]]:
    # q example: "filename:README.md language:Markdown"
    # add repo qualifier if given
    query = q
    if repo:
        query += f" repo:{repo}"
    with _gh_client() as c:
        r = c.get("/search/code", params={"q": query, "per_page": 10})
        r.raise_for_status()
        items = r.json().get("items", [])
        return [{"name": it["name"], "path": it["path"], "repository": it["repository"]["full_name"], "html_url": it["html_url"]} for it in items]

# ----- Repo reading -----
def github_get_readme(owner_repo: str, ref: Optional[str] = None) -> Dict[str, Any]:
    # GET /repos/{owner}/{repo}/readme
    owner, repo = owner_repo.split("/", 1)
    with _gh_client() as c:
        r = c.get(f"/repos/{owner}/{repo}/readme", params={"ref": ref} if ref else None)
        r.raise_for_status()
        data = r.json()
        content = ""
        if data.get("encoding") == "base64":
            import base64
            content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        return {"repository": owner_repo, "path": data.get("path", "README.md"), "content": content, "sha": data.get("sha")}

def github_get_file(owner_repo: str, path: str, ref: Optional[str] = None) -> Dict[str, Any]:
    # owner_repo e.g. "Welhox/portfolio-page"
    with _gh_client() as c:
        r = c.get(f"/repos/{owner_repo}/contents/{path}", params={"ref": ref} if ref else None)
        r.raise_for_status()
        data = r.json()
        if data.get("encoding") == "base64":
            import base64
            content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        else:
            content = data.get("content", "")
        return {"path": path, "repository": owner_repo, "content": content, "sha": data.get("sha")}

# ----- Commits -----
def github_list_commits(owner_repo: str, author: Optional[str] = None, path: Optional[str] = None,
                        since: Optional[str] = None, until: Optional[str] = None,
                        per_page: int = 30) -> List[Dict[str, Any]]:
    # GET /repos/{owner}/{repo}/commits
    owner, repo = owner_repo.split("/", 1)
    params = {"per_page": per_page}
    if author: params["author"] = author
    if path:   params["path"] = path
    if since:  params["since"] = since
    if until:  params["until"] = until
    with _gh_client() as c:
        r = c.get(f"/repos/{owner}/{repo}/commits", params=params)
        r.raise_for_status()
        items = r.json()
        out = []
        for it in items:
            out.append({
                "sha": it["sha"],
                "author_login": (it.get("author") or {}).get("login"),
                "commit_author": it["commit"]["author"],
                "commit_message": it["commit"]["message"],
                "html_url": it["html_url"],
                "files": None,  # fetch via github_get_commit if needed
            })
        return out

def github_get_commit(owner_repo: str, sha: str) -> Dict[str, Any]:
    owner, repo = owner_repo.split("/", 1)
    with _gh_client() as c:
        r = c.get(f"/repos/{owner}/{repo}/commits/{sha}")
        r.raise_for_status()
        data = r.json()
        files = [
            {
                "filename": f["filename"],
                "status": f["status"],
                "additions": f["additions"],
                "deletions": f["deletions"],
                "changes": f["changes"],
                "patch": f.get("patch")
            } for f in data.get("files", [])
        ]
        return {
            "sha": data["sha"],
            "author_login": (data.get("author") or {}).get("login"),
            "commit_author": data["commit"]["author"],
            "commit_message": data["commit"]["message"],
            "files": files,
            "html_url": data["html_url"],
        }

# ----- PRs -----
def github_list_pull_requests(owner_repo: str, state: str = "all", author: Optional[str] = None, per_page: int = 30) -> List[Dict[str, Any]]:
    # GET /repos/{owner}/{repo}/pulls?state=all
    owner, repo = owner_repo.split("/", 1)
    params = {"state": state, "per_page": per_page}
    with _gh_client() as c:
        r = c.get(f"/repos/{owner}/{repo}/pulls", params=params)
        r.raise_for_status()
        prs = r.json()
        out = []
        for pr in prs:
            if author and (pr.get("user") or {}).get("login") != author:
                continue
            out.append({
                "number": pr["number"],
                "title": pr["title"],
                "state": pr["state"],
                "user": (pr.get("user") or {}).get("login"),
                "html_url": pr["html_url"],
            })
        return out

def github_get_pull_request(owner_repo: str, number: int) -> Dict[str, Any]:
    owner, repo = owner_repo.split("/", 1)
    with _gh_client() as c:
        r = c.get(f"/repos/{owner}/{repo}/pulls/{number}")
        r.raise_for_status()
        pr = r.json()
        return {
            "number": pr["number"],
            "title": pr["title"],
            "state": pr["state"],
            "user": (pr.get("user") or {}).get("login"),
            "body": pr.get("body"),
            "additions": pr.get("additions"),
            "deletions": pr.get("deletions"),
            "changed_files": pr.get("changed_files"),
            "html_url": pr["html_url"],
        }

# ----- (Optional) GraphQL blame (precise authorship on a file) -----
def github_blame_file(owner_repo: str, path: str, ref: Optional[str] = None) -> Dict[str, Any]:
    # Uses GraphQL blame API
    owner, repo = owner_repo.split("/", 1)
    query = """
    query Blame($owner:String!, $repo:String!, $path:String!, $ref:String) {
      repository(owner:$owner, name:$repo) {
        object(expression: $ref) {
          ... on Commit {
            blame(path: $path) {
              ranges {
                startingLine
                endingLine
                commit {
                  oid
                  messageHeadline
                  author {
                    user { login }
                    email
                    name
                    date
                  }
                  url
                }
              }
            }
          }
        }
      }
    }
    """
    variables = {"owner": owner, "repo": repo, "path": path, "ref": ref or "HEAD"}
    with _gql_client() as c:
        r = c.post("", json={"query": query, "variables": variables})
        r.raise_for_status()
        data = r.json()
        ranges = (data.get("data") or {}).get("repository", {}).get("object", {}).get("blame", {}).get("ranges", []) or []
        # flatten ranges into a friendlier structure
        return {
            "repository": owner_repo,
            "path": path,
            "ref": variables["ref"],
            "ranges": [
                {
                    "start": rg["startingLine"],
                    "end": rg["endingLine"],
                    "commit": {
                        "sha": rg["commit"]["oid"],
                        "message": rg["commit"]["messageHeadline"],
                        "author_login": (rg["commit"]["author"].get("user") or {}).get("login"),
                        "author_email": rg["commit"]["author"].get("email"),
                        "author_name": rg["commit"]["author"].get("name"),
                        "date": rg["commit"]["author"].get("date"),
                        "url": rg["commit"]["url"],
                    },
                }
                for rg in ranges
            ],
        }