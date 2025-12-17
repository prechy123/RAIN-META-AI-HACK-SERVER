# SharpChat AI - AI-Powered Business Chatbot Platform

## 📋 Overview

**SharpChat AI** is an intelligent multi-tenant chatbot platform designed for local SMEs (Small and Medium Enterprises) in Nigeria. It provides AI-powered customer support with automated FAQ handling, intelligent query routing, and seamless escalation to human support when needed.

The platform integrates with **WhatsApp via Twilio**, uses **LangGraph** for agentic AI workflows, **Pinecone** for vector-based knowledge retrieval, and **PostgreSQL** for conversation memory persistence.

---

## 🏗️ Architecture

### Technology Stack

- **Framework**: FastAPI (Python 3.11)
- **AI/LLM**: LangChain + LangGraph + Groq (Llama models)
- **Vector Database**: Pinecone (for business knowledge base)
- **Databases**:
  - MongoDB (business data, sessions)
  - PostgreSQL (conversation memory/checkpointing)
- **Messaging**: Twilio WhatsApp Integration
- **Embeddings**: HuggingFace Sentence Transformers
- **Deployment**: Docker (multi-platform support)

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Interactions                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   WhatsApp   │  │   Web API    │  │  Mobile App  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Backend (main.py)                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Route Handlers                           │  │
│  │  • Business Routes    • Chatbot Routes               │  │
│  │  • KB Routes          • WhatsApp Webhook Routes      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              LangGraph Agent System (Multi-Tier)            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Router/Supervisor (Query Classification)         │  │
│  │     ├─→ Tier 1: FAQ Handler (Pinecone + LLM)        │  │
│  │     ├─→ Tier 2: Human Support (Email Collection)    │  │
│  │     └─→ Conversation Agent (General Chat)           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┼───────────┐
                ▼           ▼           ▼
    ┌─────────────┐  ┌──────────┐  ┌─────────────┐
    │   MongoDB   │  │ Pinecone │  │ PostgreSQL  │
    │  (Business  │  │ (Vector  │  │ (Memory/    │
    │   & Session)│  │   KB)    │  │ Checkpoint) │
    └─────────────┘  └──────────┘  └─────────────┘
```

---

## 🎯 Core Features

### 1. **Multi-Tenant Business Management**

- Business registration and authentication
- Business profile management (info, FAQs, products/services)
- Automatic business ID generation (BUS-0001, BUS-0002, etc.)
- Search businesses by name or ID

### 2. **Intelligent 3-Tier Query Routing**

#### **Tier 1: FAQ Handler** (Knowledge Base Queries)

- Answers questions about business hours, location, prices, menu, services
- Uses **RAG (Retrieval Augmented Generation)**:
  - Queries Pinecone vector database
  - Retrieves relevant business information
  - Generates contextual answers using LLM
- Supports Nigerian Naira (₦) pricing display

#### **Tier 2: Human Support** (Complex Requests)

- Handles reservations, orders, complaints, custom requests
- **LLM-powered contact collection**:
  - Natural conversation flow
  - Extracts email/phone from messages
  - Determines preferred contact method
  - Sends email notification to business owner
- Auto-extracts contact info using regex patterns

#### **Tier 3: Conversation Agent** (General Chat)

- Handles greetings, small talk, unclear queries
- Friendly and professional personality
- Offers to help with specific questions

### 3. **WhatsApp Integration** (Twilio)

Multi-step conversation flow with state management:

**Step 1: Greeting & Name Collection**

```
Welcome to SharpChat AI! 👋
What's your name?
```

**Step 2: Business Selection**

```
Nice to meet you, [Name]! 😊
Which business would you like to chat with?
```

**Step 3: Fuzzy Business Matching**

- Exact match by Business ID (`BUS-0001`)
- Fuzzy search by name (60% similarity threshold)
- Uses `SequenceMatcher` for intelligent matching

**Step 4: Connected to AI Chatbot**

```
✅ Great! You're now connected to *[Business Name]*
How can I help you today?
```

**Exit Commands**: `exit`, `quit`, `restart`, `change business`, etc.

### 4. **Conversation Memory** (PostgreSQL)

- Persistent conversation history per thread
- Uses LangGraph checkpointing
- Thread-based isolation (each user has unique thread_id)
- Survives server restarts

### 5. **Vector Knowledge Base Management**

- Embed all businesses to Pinecone
- Embed single business (for updates)
- Change detection (only sync modified businesses)
- Delete business from knowledge base
- Get knowledge base statistics

### 6. **Email Notifications**

- Sends support requests to business owners
- Includes conversation summary
- Customer contact details
- LLM-generated issue extraction

---

## 📁 Project Structure

```
rain-meta-hack-server/
├── main.py                      # FastAPI application entry point
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker containerization
├── WHATSAPP_WEBHOOK_README.md   # WhatsApp webhook documentation
│
├── agent/                       # AI Agent System
│   ├── main_agent.py            # Main agent entry point
│   ├── llm.py                   # LLM configuration (Groq)
│   ├── retrieval.py             # Pinecone query functions
│   ├── email_service.py         # Email sending logic
│   ├── agent_utils.py           # Utility functions
│   │
│   ├── graph_builder/           # LangGraph State Machine
│   │   ├── agent_state.py       # State schema definition
│   │   └── compiled_agent.py    # Graph compilation + checkpointing
│   │
│   └── sub_agent/               # Agent Handlers
│       ├── router.py            # Query classification/routing
│       ├── tier1.py             # FAQ handler (RAG)
│       ├── tier2.py             # Human support handler
│       └── conversation_agent.py # General chat handler
│
├── routes/                      # API Route Handlers
│   ├── business_routes.py       # Business CRUD operations
│   ├── chatbot_routes.py        # Chatbot API endpoint
│   ├── kb_route.py              # Knowledge base management
│   ├── whatsapp_webhook_routes.py # WhatsApp webhook
│   └── utils/
│       └── auth.py              # Authentication middleware
│
├── models/                      # Pydantic Models
│   ├── business.py              # Business data models
│   ├── chatbot.py               # Chat request/response models
│   ├── kbase.py                 # Knowledge base models
│   └── whatsapp.py              # WhatsApp models
│
├── vector_db/                   # Vector Database
│   ├── embedding.py             # Embedding functions
│   ├── vectors.py               # Pinecone client
│   └── kb_toolkit.py            # KB sync utilities
│
├── config/                      # Configuration
│   ├── conf.py                  # Settings (environment variables)
│   └── database.py              # MongoDB connection
│
├── schema/                      # MongoDB Schemas
│   └── schemas.py               # Serialization helpers
│
└── utils/                       # Utilities
    └── sms.py                   # SMS utilities (future use)
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **MongoDB** (for business data and sessions)
- **PostgreSQL** (for conversation memory)
- **Pinecone Account** (for vector database)
- **Groq API Key** (for LLM)
- **Twilio Account** (for WhatsApp - optional)

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd rain-meta-hack-server
```

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file in the project root:

```env
# MongoDB
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/sharpchat?retryWrites=true&w=majority

# PostgreSQL (for conversation memory)
POSTGRES_DB_URL=postgresql://user:password@localhost:5432/sharpchat_memory

# Pinecone Vector Database
PINECONE_API_KEY=your_pinecone_api_key
KB_INDEX=sharpchat-kb
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1

# Groq LLM
GROQ_API_KEY=your_groq_api_key
LLAMA_MODEL=llama-3.3-70b-versatile
TEMPERATURE=0.7
MAX_TOKENS=1024

# HuggingFace Embeddings
HUGGINGFACE_EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Email Configuration (for Tier 2 support)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_PORT_SSL=465
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=support@yourbusiness.com

# API Authentication
ENDPOINT_AUTH_KEY=your-secret-api-key

# Twilio WhatsApp (optional)
# TWILIO_ACCOUNT_SID=your_account_sid
# TWILIO_AUTH_TOKEN=your_auth_token
# TWILIO_PHONE_NUMBER=whatsapp:+14155238886
```

5. **Run the server**

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

6. **Access the API**

- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

---

## 🐳 Docker Deployment

### Build Docker Image

**For Linux/AMD64:**

```bash
docker build -t rain-meta-hack-server:1.0.0 .
```

**For macOS (Apple Silicon):**

```bash
docker build --platform linux/amd64 -t rain-meta-hack-server:1.0.0 .
```

### Run Docker Container

```bash
docker run -d \
  --name sharpchat-api \
  -p 8000:8000 \
  --env-file .env \
  rain-meta-hack-server:1.0.0
```

### Push to Docker Hub

```bash
docker tag rain-meta-hack-server:1.0.0 yourusername/rain-meta-hack-server:1.0.0
docker push yourusername/rain-meta-hack-server:1.0.0
```

---

## 📚 API Documentation

### Authentication

Most endpoints require authentication via the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-secret-api-key" http://localhost:8000/business/BUS-0001
```

**Exceptions**: WhatsApp webhook endpoints (for Twilio access)

---

### Business Management

#### **1. Register Business**

```http
POST /business/signup
Content-Type: application/json

{
  "email": "owner@business.com",
  "password": "securepassword",
  "businessName": "Joe's Coffee Shop",
  "businessDescription": "Best coffee in Lagos",
  "businessAddress": "123 Main St, Lagos",
  "businessPhone": "+234123456789",
  "businessEmailAddress": "info@joescoffee.com",
  "businessCategory": "Restaurant",
  "businessOpenHours": "8 AM - 6 PM",
  "businessOpenDays": "Monday - Saturday",
  "businessWebsite": "https://joescoffee.com",
  "extra_information": "Free WiFi available",
  "faqs": [
    {
      "question": "Do you deliver?",
      "answer": "Yes, we deliver within 5km radius"
    }
  ],
  "items": [
    {
      "name": "Cappuccino",
      "price": 500,
      "description": "Classic Italian coffee"
    }
  ]
}
```

#### **2. Business Login**

```http
POST /business/login?email=owner@business.com&password=securepassword
```

#### **3. Get Business by ID**

```http
GET /business/BUS-0001
X-API-Key: your-secret-api-key
```

#### **4. Search Business by Name**

```http
GET /business/search/coffee
X-API-Key: your-secret-api-key
```

#### **5. Update Business**

```http
PUT /business/BUS-0001
X-API-Key: your-secret-api-key
Content-Type: application/json

{
  "businessOpenHours": "7 AM - 7 PM",
  "items": [...]
}
```

---

### Chatbot API

#### **Chat Endpoint**

```http
POST /chatbot/chat
X-API-Key: your-secret-api-key
Content-Type: application/json

{
  "message": "What are your opening hours?",
  "business_id": "BUS-0001",
  "thread_id": "user123_session456",
  "user_email": "customer@example.com",
  "user_phone": "+234987654321"
}
```

**Response:**

```json
{
  "answer": "We're open Monday to Saturday, 8 AM - 6 PM.",
  "route": "tier1",
  "email_sent": false,
  "business_name": "Joe's Coffee Shop",
  "business_email": "owner@business.com",
  "user_email": "customer@example.com",
  "user_phone": "+234987654321"
}
```

---

### Knowledge Base Management

#### **1. Embed All Businesses**

```http
POST /kb/embed
X-API-Key: your-secret-api-key
Content-Type: application/json

{
  "limit": null,
  "category": null
}
```

#### **2. Embed Single Business**

```http
POST /kb/embed/business
X-API-Key: your-secret-api-key
Content-Type: application/json

{
  "business_id": "BUS-0001"
}
```

#### **3. Get KB Statistics**

```http
GET /kb/stats
X-API-Key: your-secret-api-key
```

#### **4. Delete Business from KB**

```http
DELETE /kb/business/BUS-0001
X-API-Key: your-secret-api-key
```

#### **5. Delete Entire Index**

```http
DELETE /kb/index
X-API-Key: your-secret-api-key
```

---

### WhatsApp Webhook

#### **Main Webhook** (Twilio calls this)

```http
POST /web-hook/webhook
Content-Type: application/x-www-form-urlencoded

Body=Hello&From=whatsapp:+1234567890
```

#### **Get Session** (for debugging)

```http
GET /web-hook/session/whatsapp:+1234567890
```

#### **Reset Session**

```http
POST /web-hook/reset-session?whatsapp_number=whatsapp:+1234567890
```

---

## 🔧 How It Works

### 1. **User Sends Message**

- Via WhatsApp or API endpoint

### 2. **Session Management**

- WhatsApp: Multi-step state machine (name → business selection → chat)
- API: Direct access with `thread_id` for memory

### 3. **Query Routing** (LangGraph Supervisor)

The router LLM classifies the query:

- **"What are your hours?"** → Tier 1 (FAQ)
- **"I want to make a reservation"** → Tier 2 (Human Support)
- **"Hello!"** → Conversation Agent

### 4. **Handler Execution**

#### **Tier 1 Flow:**

1. Query Pinecone for relevant business info
2. Retrieve top 3 matching documents
3. Generate answer using LLM + context
4. Return answer to user

#### **Tier 2 Flow:**

1. Use LLM to have natural conversation
2. Collect contact preference (email/phone/both)
3. Extract contact info from messages
4. Send email to business owner
5. Confirm to user

#### **Conversation Flow:**

1. Generate friendly response using LLM
2. Maintain conversation context
3. Offer to help with specific questions

### 5. **Memory Persistence**

- All messages saved to PostgreSQL via LangGraph checkpointing
- Accessible in future conversations using same `thread_id`

---

## 🧪 Testing

### Test Business Creation

```bash
curl -X POST http://localhost:8000/business/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@test.com",
    "password": "test123",
    "businessName": "Test Business",
    "businessDescription": "A test business",
    "businessAddress": "Test Address",
    "businessPhone": "+1234567890",
    "businessCategory": "Test"
  }'
```

### Test Chatbot

```bash
curl -X POST http://localhost:8000/chatbot/chat \
  -H "X-API-Key: your-secret-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are your opening hours?",
    "business_id": "BUS-0001",
    "thread_id": "test_thread_123"
  }'
```

### Test Knowledge Base

```bash
# Embed all businesses
curl -X POST http://localhost:8000/kb/embed \
  -H "X-API-Key: your-secret-api-key" \
  -H "Content-Type: application/json" \
  -d '{"limit": null, "category": null}'

# Check stats
curl http://localhost:8000/kb/stats \
  -H "X-API-Key: your-secret-api-key"
```

---

## 🔐 Security

### API Key Authentication

- All protected endpoints require `X-API-Key` header
- WhatsApp webhook is intentionally unauthenticated (Twilio access)

### Password Storage

- Currently uses plain text (⚠️ **should be hashed with bcrypt**)
- `bcrypt` library is installed but not implemented

### Environment Variables

- Never commit `.env` file to version control
- Use secure secret management in production

---

## 📊 Database Collections

### MongoDB Collections

#### **1. business_collection**

Stores business profiles:

```javascript
{
  "_id": ObjectId,
  "business_id": "BUS-0001",
  "email": "owner@business.com",
  "password": "hashed_password",
  "businessName": "Joe's Coffee",
  "businessDescription": "...",
  "businessCategory": "Restaurant",
  "businessAddress": "...",
  "businessPhone": "...",
  "businessEmailAddress": "...",
  "faqs": [...],
  "items": [...]
}
```

#### **2. session_collection**

Stores WhatsApp conversation sessions:

```javascript
{
  "whatsapp_number": "whatsapp:+1234567890",
  "state": "CHATTING",
  "name": "John Doe",
  "business_id": "BUS-0001",
  "thread_id": "whatsapp_+1234567890_abc123",
  "created_at": ISODate,
  "updated_at": ISODate
}
```

### PostgreSQL Tables

#### **checkpoints**

LangGraph conversation memory:

- Stores message history per thread
- Enables conversation context
- Created automatically by LangGraph

---

## 🛠️ Configuration

### LLM Settings

```python
# config/conf.py
GROQ_API_KEY=your_key
LLAMA_MODEL=llama-3.3-70b-versatile
TEMPERATURE=0.7  # Lower = more deterministic
MAX_TOKENS=1024  # Max response length
```

### Vector Database Settings

```python
PINECONE_API_KEY=your_key
KB_INDEX=sharpchat-kb
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
HUGGINGFACE_EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Embedding Dimensions

- Default: 384 (all-MiniLM-L6-v2)
- Ensure Pinecone index dimension matches

---

## 🎨 Customization

### Add New Agent Handler

1. Create handler in `agent/sub_agent/`
2. Update router in `agent/sub_agent/router.py`
3. Add node to graph in `agent/graph_builder/compiled_agent.py`

### Change LLM Provider

Update `agent/llm.py`:

```python
from langchain_openai import ChatOpenAI

def get_llm():
    return ChatOpenAI(
        model="gpt-4",
        temperature=0.7
    )
```

### Customize Business Matching Threshold

In `routes/whatsapp_webhook_routes.py`:

```python
def find_business_by_name(search_term: str, threshold: float = 0.6):
    # Adjust threshold (0.0 - 1.0)
    # Higher = stricter matching
```

---

## 📈 Monitoring & Logging

### Log Levels

```python
# main.py
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(name)s - %(message)s'
)
```

### Key Loggers

- `main_agent` - Main agent invocations
- `router` - Query routing decisions
- `tier1`, `tier2`, `conversation_agent` - Handler execution
- `kb_toolkit` - Knowledge base operations
- `whatsapp_webhook` - WhatsApp interactions

---

## 🐛 Troubleshooting

### Issue: "No conversation memory"

**Solution**: Ensure `POSTGRES_DB_URL` is set and PostgreSQL is running

### Issue: "Business not found in Pinecone"

**Solution**: Run embedding endpoint:

```bash
curl -X POST http://localhost:8000/kb/embed \
  -H "X-API-Key: your-key"
```

### Issue: "Email not sending"

**Solution**:

- Check email credentials in `.env`
- Enable "Less secure app access" or use App Password (Gmail)
- Verify `EMAIL_HOST` and `EMAIL_PORT`

### Issue: "WhatsApp messages not arriving"

**Solution**:

- Verify Twilio webhook URL is correct
- Check Twilio account is active
- Ensure webhook endpoint is publicly accessible

---

## 🚧 Future Enhancements

- [ ] Implement password hashing (bcrypt)
- [ ] Add user authentication and sessions
- [ ] Multi-language support
- [ ] Voice message support (WhatsApp)
- [ ] Analytics dashboard
- [ ] Sentiment analysis
- [ ] Image/document support
- [ ] Payment integration
- [ ] Appointment booking system
- [ ] CRM integration

---

## 📄 License

[Add your license here]

---

## 👥 Contributors

[Add contributors here]

---

## 📞 Support

For issues and questions:

- GitHub Issues: [repository-url]/issues
- Email: support@sharpchat.ai
- Documentation: See `WHATSAPP_WEBHOOK_README.md` for WhatsApp setup

---

## 🙏 Acknowledgments

- **LangChain** & **LangGraph** for agentic AI framework
- **Groq** for fast LLM inference
- **Pinecone** for vector database
- **Twilio** for WhatsApp integration
- **FastAPI** for the web framework

---

**Built with ❤️ for Nigerian SMEs**
