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

# ----- Composite tool for analyzing user contributions -----
def analyze_my_contributions(owner_repo: str) -> Dict[str, Any]:
    """Comprehensive analysis of Casimir's contributions to a repository"""
    # Get GitHub username from bio
    bio_data = bio_get()
    username = bio_data.get("username", "Welhox")
    
    results = {
        "repository": owner_repo,
        "analyzed_for": username,
        "commits": [],
        "pull_requests": [],
        "readme_mentions": [],
        "summary": {}
    }
    
    try:
        # 1. Get commits by this user
        commits = github_list_commits(owner_repo, author=username, per_page=50)
        results["commits"] = commits
        
        # 2. Get pull requests by this user  
        prs = github_list_pull_requests(owner_repo, author=username, per_page=30)
        results["pull_requests"] = prs
        
        # 3. Check README for mentions of contributions
        try:
            readme_data = github_get_readme(owner_repo)
            readme_content = readme_data.get("content", "").lower()
            
            # Look for various forms of the name/username
            search_terms = [
                username.lower(),
                bio_data.get("name", "").lower(),
                "casimir",
                "casi"
            ]
            
            mentions = []
            for term in search_terms:
                if term and term in readme_content:
                    # Find lines containing mentions
                    lines = readme_data.get("content", "").split('\n')
                    for i, line in enumerate(lines):
                        if term.lower() in line.lower():
                            mentions.append({
                                "term": term,
                                "line_number": i + 1,
                                "content": line.strip()
                            })
            
            results["readme_mentions"] = mentions
        except Exception as e:
            results["readme_mentions"] = [{"error": f"Could not analyze README: {str(e)}"}]
        
        # 4. Generate summary
        total_commits = len(commits)
        total_prs = len(prs)
        readme_found = len(results["readme_mentions"]) > 0
        
        results["summary"] = {
            "total_commits": total_commits,
            "total_pull_requests": total_prs,
            "mentioned_in_readme": readme_found,
            "contribution_level": "high" if total_commits > 10 or total_prs > 3 else "medium" if total_commits > 0 or total_prs > 0 else "none"
        }
        
    except Exception as e:
        results["error"] = f"Analysis failed: {str(e)}"
    
    return results

# ----- Website Content Fetching -----
def fetch_website_content(url: Optional[str] = None) -> Dict[str, Any]:
    """Fetch and analyze content from Casimir's website"""
    if not url:
        bio_data = bio_get()
        url = bio_data.get("links", {}).get("site", "https://casimirlundberg.fi")
    
    try:
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
            
            # Parse HTML content
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
            
            # Extract key sections
            result = {
                "url": url,
                "title": soup.title.string if soup.title else "",
                "sections": {},
                "meta_description": "",
                "links": []
            }
            
            # Get meta description
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc:
                result["meta_description"] = meta_desc.get("content", "")
            
            # Extract main content sections
            # Look for common section patterns
            sections = soup.find_all(['section', 'div'], class_=lambda x: x and any(
                keyword in x.lower() for keyword in ['about', 'bio', 'projects', 'skills', 'experience', 'contact']
            ))
            
            for section in sections:
                # Get section identifier
                section_id = section.get('id', '')
                section_class = ' '.join(section.get('class', []))
                section_name = section_id or section_class or 'content'
                
                # Extract text content
                text = section.get_text(separator=' ', strip=True)
                if text and len(text) > 20:  # Only include substantial content
                    result["sections"][section_name] = text[:1000]  # Limit length
            
            # Extract project links and external references
            links = soup.find_all('a', href=True)
            for link in links[:10]:  # Limit to first 10 links
                href = link['href']
                text = link.get_text(strip=True)
                if text and len(text) > 3:
                    result["links"].append({
                        "text": text[:100],
                        "url": href
                    })
            
            # If no sections found, get general page content
            if not result["sections"]:
                body_text = soup.get_text(separator=' ', strip=True)
                result["sections"]["main_content"] = body_text[:2000]
            
            return result
            
    except Exception as e:
        return {
            "url": url,
            "error": f"Failed to fetch website content: {str(e)}",
            "suggestion": "Website might be temporarily unavailable or require different access method"
        }

def get_professional_profile() -> Dict[str, Any]:
    """Get comprehensive professional and personal information from bio data"""
    bio_data = bio_get()
    
    # Extract professional information from enhanced bio
    professional_info = {
        "basic_info": {
            "name": bio_data.get("name", ""),
            "location": bio_data.get("location", ""),
            "tagline": bio_data.get("tagline", ""),
            "email": bio_data.get("email", ""),
            "profile_summary": bio_data.get("profile_summary", "")
        },
        "links": bio_data.get("links", {}),
        "technical_focus": bio_data.get("focus", []),
        "projects": bio_data.get("projects", [])
    }
    
    # Add detailed professional information if available
    professional_data = bio_data.get("professional", {})
    if professional_data:
        professional_info.update({
            "current_role": professional_data.get("current_role", ""),
            "background": professional_data.get("background", ""),
            "education": professional_data.get("education", []),
            "experience": professional_data.get("experience", []),
            "technical_skills": professional_data.get("technical_skills", {}),
            "soft_skills": professional_data.get("soft_skills", []),
            "languages": professional_data.get("languages", []),
            "projects": professional_data.get("projects", [])
        })
    
    # Add personal information if available
    personal_data = bio_data.get("personal", {})
    if personal_data:
        professional_info["personal"] = personal_data
    
    return professional_info