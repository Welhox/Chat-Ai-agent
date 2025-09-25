# 🤖 Donna - AI Chat Agent

> **A sophisticated AI-powered chat agent for Casimir's portfolio, built with security, rate limiting, and production deployment in mind.**

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)](https://cloud.google.com)
[![Live Status](https://img.shields.io/badge/Status-Live%20🟢-brightgreen?style=for-the-badge)](https://casimirlundberg.fi)

---

## 🌟 Overview

**Donna** is an intelligent AI chat agent designed to represent Casimir Lundberg on his portfolio website. Built with enterprise-grade security features, comprehensive rate limiting, and robust production deployment capabilities, Donna provides visitors with an interactive way to learn about Casimir's background, skills, and projects.

> 🌐 **Currently Live**: Donna is actively hosted on Google Cloud Run and serves visitors on Casimir's portfolio at [casimirlundberg.fi](https://casimirlundberg.fi)

### 🎯 Key Features

- **🧠 Intelligent Responses**: Powered by OpenAI's GPT models with carefully crafted system prompts
- **🛡️ Security First**: API key authentication, rate limiting, and input validation
- **📊 Usage Analytics**: Built-in monitoring and request tracking
- **🚀 Production Ready**: Docker containerization with cloud deployment support
- **⚡ High Performance**: FastAPI backend with async support
- **🔒 Content Filtering**: Smart constraints to ensure appropriate responses

---

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Portfolio     │    │   FastAPI       │    │   OpenAI        │
│   Frontend      │───▶│   Backend       │───▶│   GPT API       │
│                 │    │   (Donna)       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Rate Limiter  │
                       │   & Security    │
                       │   Layer         │
                       └─────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **OpenAI API Key**
- **Docker** (for containerized deployment)

### 🔧 Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/Welhox/Chat-Ai-agent.git
   cd Chat-Ai-agent
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Install dependencies**
   ```bash
   make install
   ```

4. **Run development server**
   ```bash
   make dev
   ```

5. **Test the API**
   ```bash
   curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-api-key" \
     -d '{"message": "Tell me about Casimir"}'
   ```

### 🐳 Docker Deployment

```bash
# Development
make docker-dev

# Production
make docker-prod
```

---

## 🛠️ API Reference

### `POST /chat`

**Send a message to Donna and receive an AI-generated response.**

#### Headers
- `X-API-Key`: Client authentication key
- `Content-Type`: application/json

#### Request Body
```json
{
  "message": "What programming languages does Casimir know?",
  "conversation_context": [] // Optional: Previous conversation history
}
```

#### Response
```json
{
  "response": "Casimir is proficient in several programming languages including C/C++, Python, TypeScript/JavaScript, and has experience with React, FastAPI, and Docker...",
  "timestamp": "2025-09-25T16:45:30.123456",
  "tokens_used": 150,
  "model": "gpt-4"
}
```

### `GET /health`

**Health check endpoint for monitoring and load balancers.**

#### Response
```json
{
  "status": "healthy",
  "timestamp": "2025-09-25T16:45:30.123456",
  "version": "1.0.0"
}
```

### `GET /stats` (Protected)

**Get usage statistics and monitoring data.**

---

## 🔒 Security Features

### 🛡️ Rate Limiting
- **Per IP**: 30 requests per minute
- **Global**: Configurable limits to prevent abuse
- **Sliding window**: Advanced rate limiting algorithm

### 🔐 Authentication
- **API Key**: Client authentication via `X-API-Key` header
- **Request Validation**: Input sanitization and length limits
- **CORS Protection**: Configured for specific origins

### 📊 Monitoring
- **Usage Tracking**: Requests per IP, hourly stats
- **Token Monitoring**: OpenAI token usage tracking
- **Security Alerts**: Automated detection of suspicious activity

---

## 🎨 Customization

### System Prompt
The AI personality is defined in `constraints.py`:
```python
SYSTEM_RULES = """
You are Donna, Casimir's AI assistant on his portfolio website.
You know everything about his background, skills, and projects...
"""
```

### Bio Data
Personal information is stored in `data/bio.json`:
```json
{
  "name": "Casimir Lundberg",
  "location": "Espoo, Finland",
  "tagline": "Aviation pro → Software developer",
  "focus": ["C/C++", "React/TS", "Fastify", "Python", "Docker"]
}
```

---

## �️ AI Tools & Capabilities

Donna is equipped with a comprehensive suite of tools that enable intelligent responses about Casimir's professional background and projects. These tools are implemented in `tools.py` and provide the AI with access to real-time information.

### 📋 Bio Management Tools

#### `bio_get(keys: Optional[List[str]] = None)`
Retrieves biographical information from the JSON database.
```python
# Get all bio data
bio_data = bio_get()

# Get specific keys only
contact_info = bio_get(["name", "email", "location"])
```

#### `bio_set(update: Dict[str, Any])`
Updates biographical information dynamically.
```python
# Update profile information
bio_set({"current_role": "Software Developer - Seeking New Opportunities"})
```

### 🐙 GitHub Integration Tools

#### Repository Analysis
- **`github_list_repos(user)`**: Lists all public repositories for a given user
- **`github_get_readme(owner_repo)`**: Fetches and parses README files
- **`github_get_file(owner_repo, path)`**: Retrieves specific file contents

#### Code & Commit Analysis
- **`github_search_code(query, repo)`**: Searches for code snippets across repositories
- **`github_list_commits(owner_repo, author)`**: Analyzes commit history and contributions
- **`github_get_commit(owner_repo, sha)`**: Detailed commit information with file changes
- **`github_blame_file(owner_repo, path)`**: Precise authorship tracking using GraphQL

#### Pull Request Analysis
- **`github_list_pull_requests(owner_repo, state, author)`**: Lists PRs with filtering
- **`github_get_pull_request(owner_repo, number)`**: Detailed PR analysis

#### Advanced Analytics
- **`analyze_my_contributions(owner_repo)`**: Comprehensive contribution analysis including:
  - Commit frequency and patterns
  - File modification history
  - Collaboration metrics
  - Technology stack usage

### 🌐 Web Content Tools

#### `fetch_website_content(url: Optional[str] = None)`
Intelligently scrapes and analyzes web content from Casimir's portfolio:
- Extracts structured content from sections (about, projects, skills)
- Parses meta descriptions and page titles
- Identifies relevant links and references
- Handles dynamic content and navigation

#### `get_professional_profile()`
Aggregates comprehensive professional information:
- Technical skills and expertise areas
- Education and certification details
- Professional experience and achievements
- Current availability status and career objectives

### 🔧 Tool Integration

All tools are seamlessly integrated with the AI system to provide:
- **Real-time Information**: Dynamic access to current profile data
- **Contextual Responses**: Tools inform conversational context
- **Data Validation**: Automated verification of information accuracy
- **Performance Optimization**: Efficient caching and rate limiting

---

## �📁 Project Structure

```
Chat-Ai-agent/
├── app/
│   └── main.py              # FastAPI application
├── data/
│   └── bio.json            # Casimir's biographical data
├── constraints.py          # AI behavior rules and limits
├── tools.py               # Utility functions and tools
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
├── docker-compose.yml    # Multi-service setup
├── Makefile             # Development commands
└── .env.example         # Environment template
```

---

## 🚀 Deployment

### ☁️ Google Cloud Run (Production)

**Donna is currently hosted on Google Cloud Run**, providing scalable, serverless deployment with automatic HTTPS and global CDN distribution.

#### Production Deployment
```bash
# Configure project and region
gcloud config set project YOUR_PROJECT_ID
gcloud config set run/region europe-north1

# Deploy with environment variables
gcloud run deploy donna-chat \
  --source . \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars="OPENAI_API_KEY=${OPENAI_API_KEY},CLIENT_API_KEY=${CLIENT_API_KEY}" \
  --memory=1Gi \
  --cpu=1 \
  --timeout=300 \
  --max-instances=10
```

#### Cloud Run Features
- **🌍 Global Distribution**: Automatic multi-region deployment
- **📈 Auto-scaling**: Scales to zero when not in use, scales up under load
- **🔒 Secure by Default**: Managed HTTPS certificates and VPC integration
- **💰 Cost Effective**: Pay-per-request pricing model
- **⚡ Cold Start Optimization**: FastAPI + uvicorn for minimal cold start times

#### Environment Configuration
```yaml
# Cloud Run Environment Variables
OPENAI_API_KEY: "sk-..."          # OpenAI API access
CLIENT_API_KEY: "secure-key-123"  # Client authentication
GITHUB_TOKEN: "ghp_..."           # GitHub API access (optional)
GITHUB_USER: "Welhox"             # GitHub username
```

### 🚢 Alternative Deployment Options

#### Railway/Render
```bash
# Set environment variables in dashboard
OPENAI_API_KEY=your_openai_key
CLIENT_API_KEY=your_client_key
PORT=8000
```

### Traditional VPS
```bash
# Using Docker Compose
docker-compose -f docker-compose.yml up -d
```

---

## 🧪 Development

### Commands
```bash
make install     # Install dependencies
make dev         # Run development server
make test        # Run tests (if implemented)
make lint        # Code linting
make format      # Code formatting
make docker-dev  # Development Docker build
make docker-prod # Production Docker build
```

### Environment Variables
```bash
OPENAI_API_KEY=sk-...          # OpenAI API key
CLIENT_API_KEY=your-key        # Client authentication
ENVIRONMENT=development        # development/production
PORT=8000                      # Server port
```

---

## 🎯 Use Cases

- **Portfolio Integration**: Interactive chat on personal websites
- **Technical Interviews**: AI assistant for candidate evaluation
- **Customer Support**: Automated responses for common questions
- **Educational Tool**: Learning about AI integration in web apps

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 About Casimir

**Casimir Lundberg** is a software developer transitioning from aviation to tech, currently studying at **Hive Helsinki**. With a strong foundation in **C/C++**, **React/TypeScript**, and **Python**, he builds robust applications with a focus on clean code and user experience.

- 🌐 **Portfolio**: [casimirlundberg.fi](https://casimirlundberg.fi)
- 💼 **LinkedIn**: [Casimir Lundberg](https://linkedin.com/in/casimir-lundberg)
- 📧 **Email**: mail@casimirlundberg.fi
- 🐙 **GitHub**: [@Welhox](https://github.com/Welhox)

---

<div align="center">

**Built with ❤️ by Casimir Lundberg**

*Powered by OpenAI GPT • Secured with FastAPI • Deployed with Docker*

</div>
