# SharpChat AI - AI-Powered Chatbot Platform for SMEs

<div align="center">

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Latest-FF6B6B.svg?style=flat)](https://github.com/langchain-ai/langgraph)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-336791.svg?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0+-47A248.svg?style=flat&logo=mongodb&logoColor=white)](https://www.mongodb.com)

**An intelligent multi-tier chatbot system that helps small and medium enterprises (SMEs) automate customer support through WhatsApp and web interfaces.**

[Features](#features) • [Architecture](#architecture) • [Installation](#installation) • [API Documentation](#api-documentation) • [Usage](#usage)

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Usage Examples](#usage-examples)
- [Project Structure](#project-structure)
- [Development](#development)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

**SharpChat AI** is an intelligent conversational AI platform designed specifically for small and medium enterprises (SMEs). It provides a sophisticated multi-tier routing system that intelligently handles customer queries through:

- **Tier 1**: FAQ-based responses using semantic search and vector embeddings
- **Tier 2**: Complex queries requiring human intervention with automated email escalation
- **Conversation Agent**: Natural language conversations powered by LLMs

The platform integrates seamlessly with **WhatsApp** via Twilio and provides a RESTful API for web and mobile applications.

---

## ✨ Features

### 🤖 Intelligent Multi-Tier Routing

```mermaid
graph TD
    A[User Query] --> B[Router/Supervisor]
    B --> C{Query Classification}
    C -->|Simple FAQ| D[Tier 1: Vector Search]
    C -->|Complex/Escalation| E[Tier 2: Email Service]
    C -->|General Chat| F[Conversation Agent]
    D --> G[Response to User]
    E --> H[Email to Business]
    E --> G
    F --> G
```

- **Tier 1 Agent**: Handles FAQs using semantic similarity search with vector embeddings
- **Tier 2 Agent**: Escalates complex queries to business owners via email
- **Conversation Agent**: Engages in natural conversations using LLM

### 📱 WhatsApp Integration

- Multi-step conversation flow with session management
- Fuzzy business name matching for easy discovery
- Support for business ID and name-based lookup
- Session persistence and state management
- Exit/restart commands for user control

### 🧠 Knowledge Base Management

- Upload and process business documents (PDF, DOCX, TXT)
- Automatic text extraction and chunking
- Vector embeddings using Sentence Transformers
- Semantic search with PineconeDB
- FAQ and product catalog management

### 💼 Business Management

- Business registration and authentication
- Profile management (FAQs, products, services)
- Automatic knowledge base embedding on updates
- Business search and discovery

### 🔒 Security & Authentication

- API key-based authentication
- Environment-based configuration
- Secure credential management

---

## 🏗️ Architecture

### System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        WA[WhatsApp Users]
        WEB[Web/Mobile Apps]
    end
    
    subgraph "API Layer"
        WEBHOOK[WhatsApp Webhook]
        CHATBOT[Chatbot API]
        BIZ[Business API]
        KB[Knowledge Base API]
    end
    
    subgraph "Agent Layer"
        ROUTER[Query Router]
        T1[Tier 1 Agent]
        T2[Tier 2 Agent]
        CONV[Conversation Agent]
    end
    
    subgraph "Service Layer"
        RETRIEVAL[Vector Retrieval]
        EMAIL[Email Service]
        LLM[LLM Service]
    end
    
    subgraph "Data Layer"
        MONGO[(MongoDB)]
        POSTGRES[(PostgreSQL)]
        PINECONE[(PineconeDB)]
    end
    
    WA --> WEBHOOK
    WEB --> CHATBOT
    WEB --> BIZ
    WEB --> KB
    
    WEBHOOK --> ROUTER
    CHATBOT --> ROUTER
    BIZ --> MONGO
    KB --> Pinecone
    
    ROUTER --> T1
    ROUTER --> T2
    ROUTER --> CONV
    
    T1 --> RETRIEVAL
    T2 --> EMAIL
    CONV --> LLM
    
    RETRIEVAL --> Pinecone
    EMAIL --> T2
    LLM --> CONV
    
    ROUTER --> POSTGRES
    MONGO -.Business Data.-> RETRIEVAL
```

### Agent Workflow

The system uses **LangGraph** to orchestrate a stateful agent workflow:

1. **Supervisor Node**: Routes queries based on intent classification
2. **Tier 1 Node**: Searches knowledge base for relevant answers
3. **Tier 2 Node**: Extracts user info and sends escalation emails
4. **Conversation Node**: Handles general conversations

**State Management**: PostgreSQL-backed checkpointing ensures conversation continuity across sessions.

---

## 🛠️ Tech Stack

### Backend Framework
- **FastAPI** - Modern, high-performance web framework
- **Uvicorn** - ASGI server for production deployment

### AI/ML Stack
- **LangChain** - LLM orchestration framework
- **LangGraph** - Stateful agent workflow management
- **Sentence Transformers** - Text embeddings (all-MiniLM-L6-v2)
- **PineconeDB** - Vector database for semantic search

### Databases
- **MongoDB** - Business data, sessions, and user information
- **PostgreSQL** - Conversation state and checkpointing
- **PineconeDB** - Vector embeddings for knowledge retrieval

### External Services
- **Twilio** - WhatsApp messaging integration
- **SMTP** - Email service for escalations
- **LLM API** - Language model inference (configurable)

### Development Tools
- **Docker** - Containerization
- **Pydantic** - Data validation
- **Python-dotenv** - Environment management

---

## 📦 Installation

### Prerequisites

- Python 3.11 or higher
- MongoDB 7.0+
- PostgreSQL 16+
- Docker (optional, for containerized deployment)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/RAIN-META-AI-HACK-SERVER.git
   cd RAIN-META-AI-HACK-SERVER
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize databases**
   
   Ensure MongoDB and PostgreSQL are running, then the application will auto-initialize on startup.

6. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```

   The API will be available at `http://localhost:8000`

---

## ⚙️ Configuration

Create a `.env` file in the project root with the following variables:

```env
# Database Configuration
MONGO_URL=mongodb://localhost:27017/
POSTGRES_DB_URL=postgresql://user:password@localhost:5432/sharpchat

# LLM Configuration
LLAMA_API_KEY=your-llm-api-key
LLAMA_MODEL=llama-2-70b-chat

# WhatsApp/Twilio Configuration
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Email Configuration
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USER=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# API Security
API_KEY=your-secure-api-key
```

### Configuration Parameters

| Parameter | Description | Required |
|-----------|-------------|----------|
| `MONGO_URL` | MongoDB connection string | ✅ |
| `POSTGRES_DB_URL` | PostgreSQL connection string | ✅ |
| `LLAMA_API_KEY` | API key for LLM service | ✅ |
| `LLAMA_MODEL` | LLM model identifier | ✅ |
| `TWILIO_ACCOUNT_SID` | Twilio account SID | ⚠️ (for WhatsApp) |
| `TWILIO_AUTH_TOKEN` | Twilio authentication token | ⚠️ (for WhatsApp) |
| `TWILIO_WHATSAPP_NUMBER` | Twilio WhatsApp number | ⚠️ (for WhatsApp) |
| `MAIL_HOST` | SMTP server host | ⚠️ (for Tier 2) |
| `MAIL_PORT` | SMTP server port | ⚠️ (for Tier 2) |
| `MAIL_USER` | Email account username | ⚠️ (for Tier 2) |
| `MAIL_PASSWORD` | Email account password/app password | ⚠️ (for Tier 2) |
| `API_KEY` | API authentication key | ✅ |

---

## 📚 API Documentation

### Interactive Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### API Endpoints Overview

#### Health & Status

```http
GET /
GET /health
```

#### Business Management

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/business/signup` | POST | Register new business | ❌ |
| `/business/login` | POST | Business login | ❌ |
| `/business/{business_id}` | GET | Get business details | ✅ |
| `/business/search/{name}` | GET | Search businesses | ✅ |
| `/business/{business_id}` | PUT | Update business info | ✅ |

#### Chatbot

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/chatbot/chat` | POST | Send message to chatbot | ✅ |

#### Knowledge Base

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/kb/upload` | POST | Upload documents | ✅ |
| `/kb/add-faq` | POST | Add FAQ manually | ✅ |
| `/kb/search` | POST | Search knowledge base | ✅ |
| `/kb/regenerate/{business_id}` | POST | Regenerate embeddings | ✅ |

#### WhatsApp Webhook

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/web-hook/` | POST | Twilio webhook endpoint | ❌ |
| `/web-hook/session/{whatsapp_number}` | GET | Get session details | ❌ |
| `/web-hook/reset-session` | POST | Reset user session | ❌ |

---

## 💡 Usage Examples

### 1. Register a Business

```bash
curl -X POST "http://localhost:8000/business/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "businessName": "Joe'\''s Coffee Shop",
    "email": "joe@coffeeshop.com",
    "password": "securepassword123",
    "businessDescription": "Premium artisan coffee and pastries",
    "faqs": [
      {
        "question": "What are your opening hours?",
        "answer": "We'\''re open Monday-Friday 7am-6pm, weekends 8am-5pm"
      }
    ],
    "items": [
      {
        "name": "Cappuccino",
        "price": 4.50,
        "description": "Classic Italian cappuccino with steamed milk"
      }
    ]
  }'
```

### 2. Chat with the Bot

```bash
curl -X POST "http://localhost:8000/chatbot/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "query": "What are your opening hours?",
    "business_id": "BUS-0001",
    "thread_id": "user_123_session",
    "user_email": "customer@example.com"
  }'
```

**Response:**
```json
{
  "answer": "We're open Monday-Friday 7am-6pm, and weekends 8am-5pm. Looking forward to seeing you!",
  "route": "tier1",
  "email_sent": false,
  "business_name": "Joe's Coffee Shop",
  "business_email": "joe@coffeeshop.com"
}
```

### 3. Upload Knowledge Base Documents

```bash
curl -X POST "http://localhost:8000/kb/upload" \
  -H "X-API-Key: your-api-key" \
  -F "business_id=BUS-0001" \
  -F "files=@menu.pdf" \
  -F "files=@policies.docx"
```

### 4. WhatsApp Conversation Flow

```
User: Hi
Bot: Welcome to SharpChat AI! 👋
     What's your name?

User: John
Bot: Nice to meet you, John! 😊
     Which business would you like to chat with?
     💡 You can enter:
     • Business ID (e.g., BUS-0001)
     • Business name (e.g., Joe's Coffee Shop)

User: Joe's Coffee
Bot: ✅ Great! You're now connected to *Joe's Coffee Shop*
     Premium artisan coffee and pastries
     How can I help you today?

User: What's your best coffee?
Bot: Our signature drink is the Cappuccino - a classic Italian 
     cappuccino with perfectly steamed milk for just $4.50!
```

---

## 📁 Project Structure

```
RAIN-META-AI-HACK-SERVER/
├── agent/                          # AI Agent logic
│   ├── graph_builder/              # LangGraph workflow
│   │   ├── agent_state.py          # State schema
│   │   └── compiled_agent.py       # Graph compilation with Postgres Memory
│   ├── sub_agent/                  # Agent nodes
│   │   ├── router.py               # Query routing
│   │   ├── tier1.py                # FAQ handler
│   │   ├── tier2.py                # Escalation handler
│   │   └── conversation_agent.py   # Chat handler
│   ├── agent_utils.py              # Utility functions
│   ├── email_service.py            # Email integration
│   ├── llm.py                      # LLM configuration
│   ├── main_agent.py               # Main entry point
│   └── retrieval.py                # Vector search
│
├── config/                         # Configuration
│   ├── conf.py                     # Settings management
│   └── database.py                 # MongoDB connection
│
├── models/                         # Pydantic models
│   ├── business.py                 # Business schemas
│   ├── chatbot.py                  # Chatbot schemas
│   ├── kbase.py                    # Knowledge base schemas
│   └── whatsapp.py                 # WhatsApp schemas
│
├── routes/                         # API routes
│   ├── business_routes.py          # Business endpoints
│   ├── chatbot_routes.py           # Chat endpoints
│   ├── kb_route.py                 # Knowledge base endpoints
│   ├── whatsapp_webhook_routes.py  # WhatsApp webhook
│   └── utils/
│       └── auth.py                 # Authentication
│
├── schema/                         # Data serialization
│   └── schemas.py                  # MongoDB serializers
│
├── vector_db/                      # Vector database
│   ├── embedding.py                # Embedding service
│   ├── kb_toolkit.py               # Knowledge base tools
│   ├── main.py                     # Vector DB initialization
│   └── vectors.py                  # Vector operations
│
├── utils/                          # Utilities
│
├── .env.example                    # Environment template
├── .gitignore                      # Git ignore rules
├── Dockerfile                      # Docker configuration
├── main.py                         # Application entry point
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

---

## 🔧 Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

### Database Migrations

The application uses automatic schema initialization. On first run:

1. MongoDB collections are created automatically
2. PostgreSQL tables are initialized via LangGraph checkpointer
3. Pinecone collections are created on first embedding

---

## 🚀 Deployment

### Docker Deployment

1. **Build the Docker image**
   ```bash
   docker build -t sharpchat-ai:1.0.0 .
   ```

2. **Run the container**
   ```bash
   docker run -d \
     --name sharpchat-api \
     -p 8000:8000 \
     --env-file .env \
     sharpchat-ai:1.0.0
   ```

3. **For macOS (ARM architecture)**
   ```bash
   docker build --platform linux/amd64 -t sharpchat-ai:1.0.0 .
   ```

### Production Considerations

- Use a process manager (e.g., Gunicorn with Uvicorn workers)
- Set up reverse proxy (Nginx/Caddy)
- Enable HTTPS/TLS
- Configure proper logging and monitoring
- Set up database backups
- Use environment-specific configurations
- Implement rate limiting
- Set up health checks and auto-restart

### Environment Variables for Production

```env
# Production settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Database URLs (use production credentials)
MONGO_URL=mongodb://prod-mongo:27017/
POSTGRES_DB_URL=postgresql://prod-user:prod-pass@prod-db:5432/sharpchat

# Security
API_KEY=<strong-random-key>
ALLOWED_ORIGINS=https://yourdomain.com
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Coding Standards

- Follow PEP 8 style guide
- Write descriptive commit messages
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Groq** - For handling the LLaMa model used
- **LangChain & LangGraph** - For the amazing agent orchestration framework
- **FastAPI** - For the high-performance web framework
- **Twilio** - For WhatsApp integration capabilities
- **Sentence Transformers** - For powerful text embeddings
- **Pinecone** - For efficient vector storage and retrieval

---

## 📞 Support

For questions, issues, or feature requests:

- **Issues**: [GitHub Issues](https://github.com/yourusername/RAIN-META-AI-HACK-SERVER/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/RAIN-META-AI-HACK-SERVER/discussions)

---

<div align="center">

**Built with ❤️ for SMEs**

⭐ Star this repo if you find it helpful!

</div>
