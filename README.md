# Donna - Feline AI Chat Agent 🐾

<img width="1024" height="768" alt="Donna-ai-assistant-4-3" src="https://github.com/user-attachments/assets/8f502c0c-6a69-4753-9d25-ef093b6e0819" />

> **An intelligent AI assistant that lives on my portfolio, answering questions about my background, skills, and projects in real-time.**

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)](https://cloud.google.com)
[![Live Status](https://img.shields.io/badge/Status-Live%20🟢-brightgreen?style=for-the-badge)](https://casimirlundberg.fi)

---

## 🌟 What is Donna?

Donna is my personal AI assistant, currently live on [casimirlundberg.fi](https://casimirlundberg.fi). She's not just a chatbot—she's an intelligent agent with real-time access to my GitHub repositories, portfolio content, and professional background. Visitors can ask her anything about my projects, dive into my code, or learn about my experience, and she provides informed, conversational responses 24/7.

Think of her as the interactive layer of my portfolio, making it easy for recruiters, collaborators, or anyone curious to explore my work without clicking through dozens of pages.

---

## 🎯 Why I Built This

Portfolio websites are often static and one-dimensional. I wanted something more engaging—a way for people to interact with my work naturally, ask questions, and get detailed answers about specific projects or skills. Building Donna let me combine several interests:

- **AI Integration**: Working with OpenAI's API and exploring conversational AI capabilities
- **Backend Architecture**: Designing a secure, production-ready FastAPI service
- **DevOps**: Deploying with Docker to Google Cloud Run with proper monitoring
- **Problem Solving**: Handling rate limiting, authentication, and real-time data access

---

## 🧠 What Donna Can Do

### Real-Time GitHub Integration
Donna has direct access to my GitHub repositories through the GitHub API. She can:
- Pull README files and explain project architectures
- Search through code to answer technical questions
- Analyze commit history and contribution patterns
- Discuss specific features or implementation details
- Show you exactly where and how I've worked on projects

**Example**: Ask her "How did Casimir implement JWT authentication in WebPONG?" and she'll fetch the relevant code and explain the approach.

### Portfolio Intelligence
She knows everything about my professional background:
- Technical skills and experience levels
- Education and certifications (Hive Helsinki, aviation background)
- Work history and transferable skills
- Current availability and career objectives

### Smart Conversations
Powered by OpenAI's GPT models with carefully crafted prompts, Donna:
- Maintains context throughout conversations
- Provides detailed, accurate responses about my work
- Stays on-topic (she won't help you debug your own code)
- References specific projects and links when relevant

---

## 🏗️ Technical Architecture

### Backend Stack
- **FastAPI**: High-performance async Python framework
- **OpenAI API**: GPT-4 for natural language processing
- **GitHub API**: Real-time repository data access
- **Beautiful Soup**: Web scraping for portfolio content
- **Pydantic**: Request validation and type safety

### Security & Performance
- **API Key Authentication**: Secured endpoints with client authentication
- **Rate Limiting**: Per-IP throttling (30 requests/minute) to prevent abuse
- **Input Validation**: Sanitized inputs and length limits
- **Usage Tracking**: Monitoring requests and token consumption
- **CORS Protection**: Configured for specific origins only

### Production Deployment
Hosted on **Google Cloud Run** with:
- Automatic scaling (scales to zero when idle)
- Global CDN distribution
- Managed HTTPS certificates
- Container-based deployment with Docker
- Environment-based configuration

---

## 🛠️ How It Works

When someone sends a message to Donna:

1. **Frontend** sends request with API key authentication
2. **Rate Limiter** checks IP-based quotas
3. **FastAPI** validates and sanitizes input
4. **Donna's tools** fetch relevant data (GitHub repos, bio info, etc.)
5. **OpenAI** generates a contextual response using the data
6. **Response** is returned with usage metrics

The system connects my portfolio frontend to FastAPI backend, which communicates with both OpenAI's GPT API and GitHub API, all while enforcing security through rate limiting and authentication.

---

## 🎨 Key Features

### 📋 Bio Management
Dynamic access to professional information stored in JSON format. Donna can retrieve and discuss education, work history, skills, and current objectives.

### 🐙 GitHub Tools
- **Repository Listing**: Browse all public repos
- **README Parsing**: Extract and explain project documentation
- **Code Search**: Find specific implementations or patterns
- **Commit Analysis**: Review contribution history and frequency
- **File Inspection**: Read and discuss specific code files
- **Contribution Analytics**: Comprehensive analysis of coding patterns

### 🌐 Web Content Extraction
Intelligent scraping of portfolio website content to answer questions about projects, skills, and experience without hardcoding everything.

### 📊 Monitoring & Analytics
Built-in tracking for:
- Request volume per IP
- Token usage and costs
- Response times
- Error rates and types

---

## 🎯 Use Cases & Learnings

### What I Learned
- **AI Prompt Engineering**: Crafting effective system prompts to constrain behavior
- **API Security**: Implementing authentication, rate limiting, and input validation
- **Async Python**: FastAPI's async capabilities for concurrent requests
- **Cloud Deployment**: Containerization and serverless deployment patterns
- **Tool Integration**: Building custom functions for AI to call dynamically

### Real-World Applications
Beyond my portfolio, this architecture could be adapted for:
- Customer support chatbots with CRM integration
- Technical documentation assistants
- Interactive product demos
- Internal knowledge base tools

---

## 📁 Project Structure

The project is organized into several key components:

**Core Application**
- `app/main.py` - FastAPI application and endpoints
- `constraints.py` - AI system prompts and behavior rules
- `tools.py` - GitHub API and utility functions

**Data & Configuration**
- `data/bio.json` - Biographical data store
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container configuration
- `docker-compose.yml` - Multi-service orchestration

---

## 🚀 Live Demo

**Try Donna yourself**: Visit [casimirlundberg.fi](https://casimirlundberg.fi) and click the chat icon in the bottom right corner.

Try asking:
- "What projects has Casimir built?"
- "Tell me about the WebPONG authentication system"
- "What's in Casimir's Minishell repository?"
- "What technologies does Casimir work with?"

---

## 👤 About Me

I'm **Casimir Lundberg**, a full-stack developer with a background in aviation, based in Finland. I work with C/C++, TypeScript, React, Python, and modern web technologies. Currently seeking developer opportunities where I can contribute to meaningful projects.

- 🌐 **Portfolio**: [casimirlundberg.fi](https://casimirlundberg.fi)
- 💼 **LinkedIn**: [linkedin.com/in/caslun](https://linkedin.com/in/caslun)
- 📧 **Email**: mail@casimirlundberg.fi
- 🐙 **GitHub**: [@Welhox](https://github.com/Welhox)

---

<div align="center">


*OpenAI GPT • FastAPI • Docker • Google Cloud Run*

[Try Donna Live](https://casimirlundberg.fi) 🐾

</div>
