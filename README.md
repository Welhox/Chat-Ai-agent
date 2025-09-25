# 🤖 Donna - AI Chat Agent

> **A sophisticated AI-powered chat agent for Casimir's portfolio, built with security, rate limiting, and production deployment in mind.**

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)

---

## 🌟 Overview

**Donna** is an intelligent AI chat agent designed to represent Casimir Lundberg on his portfolio website. Built with enterprise-grade security features, comprehensive rate limiting, and robust production deployment capabilities, Donna provides visitors with an interactive way to learn about Casimir's background, skills, and projects.

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

## 📁 Project Structure

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

### Cloud Run (Google Cloud)
```bash
# Build and deploy
gcloud run deploy donna-chat \
  --source . \
  --platform managed \
  --region europe-north1
```

### Railway/Render
```bash
# Set environment variables
OPENAI_API_KEY=your_openai_key
CLIENT_API_KEY=your_client_key
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
