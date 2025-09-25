# main.py
import os
import time
import json
from typing import List, Literal, Optional, Dict, Any
# Optional dotenv loading (local dev only)
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI, OpenAIError

from constraints import (
    SYSTEM_RULES,
    trim_user_text,
    MAX_OUTPUT_TOKENS,
    REQUEST_TIMEOUT_SECONDS,
)
import tools as T

# ----- OpenAI client (key must come from env / Secret Manager in Cloud Run) -----
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    # Don't crash on import; return a clear 500 later if someone hits /chat.
    client = None  # type: ignore
else:
    client = OpenAI(api_key=OPENAI_API_KEY)

# ----- FastAPI + CORS -----
app = FastAPI(title="AI Agent Backend", version="0.1.0")

# Allow specific origins from env (comma-separated). If missing, default to localhost dev + production.
allowed = [o.strip() for o in (os.getenv("ALLOWED_ORIGINS") or "").split(",") if o.strip()]
default_origins = [
    "http://127.0.0.1:5173", 
    "http://localhost:5173",
    "https://casimirlundberg.fi",
    "https://www.casimirlundberg.fi"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed or default_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Role = Literal["system", "user", "assistant"]

class Msg(BaseModel):
    role: Role
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Msg]] = None

class ChatResponse(BaseModel):
    reply: str

@app.get("/health")
def health():
    return {"status": "ok"}

# ----- Tool schema for OpenAI -----
TOOLS_SPEC = [
    {
        "type": "function",
        "function": {
            "name": "bio_get",
            "description": "Read persistent BIO/memory for Casimir. Optionally filter by keys.",
            "parameters": {
                "type": "object",
                "properties": {"keys": {"type": "array", "items": {"type": "string"}}},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "bio_set",
            "description": "Update BIO/memory with key/value pairs. Use sparingly for long-lived facts.",
            "parameters": {
                "type": "object",
                "properties": {"update": {"type": "object", "additionalProperties": True}},
                "required": ["update"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "github_list_repos",
            "description": "ALWAYS use first when asked about repositories, projects, or code. Lists all GitHub repos to discover project names when users ask vague questions like 'tell me about his projects' or mention partial names.",
            "parameters": {
                "type": "object",
                "properties": {"user": {"type": "string", "description": "GitHub username, defaults to env"}},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "github_search_code",
            "description": "Search code in GitHub by query; optionally restrict to a repo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "q": {"type": "string"},
                    "repo": {"type": "string", "description": "owner/name"},
                },
                "required": ["q"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "github_get_file",
            "description": "Get the content of a file from a GitHub repo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "owner_repo": {"type": "string", "description": "owner/name"},
                    "path": {"type": "string"},
                    "ref": {"type": "string", "description": "branch, tag, or commit SHA (optional)"},
                },
                "required": ["owner_repo", "path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "github_get_readme",
            "description": "Fetch README.md content (or repo default readme) for a repository.",
            "parameters": {
                "type": "object",
                "properties": {"owner_repo": {"type": "string"}, "ref": {"type": "string"}},
                "required": ["owner_repo"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "github_list_commits",
            "description": "List commits for a repository, filterable by author, path, and dates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "owner_repo": {"type": "string"},
                    "author": {"type": "string"},
                    "path": {"type": "string"},
                    "since": {"type": "string", "description": "ISO8601"},
                    "until": {"type": "string", "description": "ISO8601"},
                    "per_page": {"type": "integer"},
                },
                "required": ["owner_repo"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "github_get_commit",
            "description": "Get detailed info for a single commit, including changed files and patches.",
            "parameters": {
                "type": "object",
                "properties": {"owner_repo": {"type": "string"}, "sha": {"type": "string"}},
                "required": ["owner_repo", "sha"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "github_list_pull_requests",
            "description": "List pull requests in a repo (optionally filter by author).",
            "parameters": {
                "type": "object",
                "properties": {
                    "owner_repo": {"type": "string"},
                    "state": {"type": "string", "enum": ["open", "closed", "all"]},
                    "author": {"type": "string"},
                    "per_page": {"type": "integer"},
                },
                "required": ["owner_repo"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "github_get_pull_request",
            "description": "Get a PR’s details (body, lines changed, etc.).",
            "parameters": {
                "type": "object",
                "properties": {"owner_repo": {"type": "string"}, "number": {"type": "integer"}},
                "required": ["owner_repo", "number"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "github_blame_file",
            "description": "Get blame ranges for a file to attribute lines to authors (uses GraphQL).",
            "parameters": {
                "type": "object",
                "properties": {"owner_repo": {"type": "string"}, "path": {"type": "string"}, "ref": {"type": "string"}},
                "required": ["owner_repo", "path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_my_contributions",
            "description": "Comprehensive analysis of Casimir's contributions to a repository (commits, PRs, README mentions)",
            "parameters": {
                "type": "object",
                "properties": {"owner_repo": {"type": "string", "description": "Repository in format 'owner/name'"}},
                "required": ["owner_repo"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_website_content",
            "description": "Fetch current content from Casimir's portfolio website (casimirlundberg.fi)",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Website URL (defaults to bio.json site link)"}
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_professional_profile",
            "description": "ALWAYS USE for questions about Casimir's family, personal life, wife, children, hobbies, or any personal information. Also provides comprehensive professional information including experience, skills, education, and achievements.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
]

# ----- Tool dispatcher -----
def json_dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False)

def execute_tool(name: str, args: Dict[str, Any]) -> str:
    try:
        if name == "bio_get":
            return json_dumps(T.bio_get(args.get("keys")))
        if name == "bio_set":
            return json_dumps(T.bio_set(args.get("update") or {}))
        if name == "github_list_repos":
            return json_dumps(T.github_list_repos(args.get("user")))
        if name == "github_search_code":
            return json_dumps(T.github_search_code(args["q"], args.get("repo")))
        if name == "github_get_file":
            return json_dumps(T.github_get_file(args["owner_repo"], args["path"], args.get("ref")))
        if name == "github_get_readme":
            return json_dumps(T.github_get_readme(args["owner_repo"], args.get("ref")))
        if name == "github_list_commits":
            return json_dumps(
                T.github_list_commits(
                    args["owner_repo"],
                    args.get("author"),
                    args.get("path"),
                    args.get("since"),
                    args.get("until"),
                    args.get("per_page") or 30,
                )
            )
        if name == "github_get_commit":
            return json_dumps(T.github_get_commit(args["owner_repo"], args["sha"]))
        if name == "github_list_pull_requests":
            return json_dumps(
                T.github_list_pull_requests(
                    args["owner_repo"],
                    args.get("state", "all"),
                    args.get("author"),
                    args.get("per_page") or 30,
                )
            )
        if name == "github_get_pull_request":
            return json_dumps(T.github_get_pull_request(args["owner_repo"], args["number"]))
        if name == "github_blame_file":
            return json_dumps(T.github_blame_file(args["owner_repo"], args["path"], args.get("ref")))
        if name == "analyze_my_contributions":
            return json_dumps(T.analyze_my_contributions(args["owner_repo"]))
        if name == "fetch_website_content":
            return json_dumps(T.fetch_website_content(args.get("url")))
        if name == "get_professional_profile":
            return json_dumps(T.get_professional_profile())
        return json_dumps({"error": f"unknown tool {name}"})
    except Exception as e:
        return json_dumps({"error": str(e)})

# ----- Chat route with tool-calling loop -----
@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if client is None:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")

    t0 = time.time()
    user_text = trim_user_text(req.message)

    # Start with system + provided history
    messages: List[Dict[str, Any]] = [{"role": "system", "content": SYSTEM_RULES}]
    for m in (req.history or []):
        messages.append({"role": m.role, "content": m.content})
    messages.append({"role": "user", "content": user_text})

    # Tool-call loop (max 4 hops)
    for _ in range(4):
        if time.time() - t0 > REQUEST_TIMEOUT_SECONDS:
            raise HTTPException(status_code=408, detail="Request timeout (tool loop)")

        try:
            resp = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,          # type: ignore
                tools=TOOLS_SPEC,
                tool_choice="auto",
                temperature=0.3,
                max_tokens=MAX_OUTPUT_TOKENS,
            )
        except OpenAIError as e:
            raise HTTPException(status_code=502, detail=f"OpenAI error: {e.__class__.__name__}")

        choice = resp.choices[0]
        msg = choice.message

        # Tool calls?
        if getattr(msg, "tool_calls", None):
            for tc in msg.tool_calls:
                name = tc.function.name
                args_json = tc.function.arguments or "{}"
                args = json.loads(args_json)
                tool_result_str = execute_tool(name, args)

                # Append assistant's tool call + the tool's result
                messages.append({"role": "assistant", "content": None, "tool_calls": [tc]})
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "name": name,
                        "content": tool_result_str,
                    }
                )
            continue  # let the model integrate tool outputs

        # No tool call → final answer
        final = msg.content or ""
        return ChatResponse(reply=final.strip())

    # If we exit loop without a final answer:
    raise HTTPException(status_code=500, detail="Tool loop did not converge")
