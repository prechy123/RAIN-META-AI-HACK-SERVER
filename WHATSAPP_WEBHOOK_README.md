# WhatsApp Webhook Configuration

## Overview

The WhatsApp webhook has been configured with a multi-step conversation flow that:

1. Greets users and collects their name
2. Asks for business search (by ID or name)
3. Uses fuzzy matching to find businesses in MongoDB
4. Connects users to the chatbot with a generated thread_id

## Conversation Flow

### Step 1: Initial Greeting

When a user first messages the WhatsApp number, they receive:

```
Welcome to SharpChat AI! 👋

What's your name?

💡 Type 'exit' anytime to start over.
```

### Step 2: Name Collection

After user provides their name, the system stores it and asks:

```
Nice to meet you, [Name]! 😊

Which business would you like to chat with?

💡 You can enter:
• Business ID (e.g., BUS-0001)
• Business name (e.g., Joe's Coffee Shop)
```

### Step 3: Business Search

The system supports two search methods:

#### A. Business ID Search (Exact Match)

- Format: `BUS-XXXX` (e.g., BUS-0001)
- Instantly finds the business by ID

#### B. Business Name Search (Fuzzy Matching)

- Uses sophisticated similarity matching (60% threshold)
- Finds closest matching business name
- If no match found, prompts user to try again:

```
❌ Sorry, I couldn't find a business matching '[search]'.

Please try again with:
• A different business name
• A business ID (format: BUS-XXXX)
```

### Step 4: Connected to Chatbot

Once business is found:

```
✅ Great! You're now connected to *[Business Name]*

[Business Description]

How can I help you today?

_Type 'change business' to switch or 'exit' to end._
```

A unique `thread_id` is generated and all subsequent messages are routed to the `/chatbot` endpoint.

### Step 5: Ending a Session

Users can end their session at any time by sending any of these commands:
- `exit`
- `quit`
- `end`
- `stop`
- `restart`
- `reset`
- `new`
- `change business`
- `switch business`

When a session is ended, the user receives:

```
👋 Session ended!

Thanks for chatting, [Name]! Your conversation has been reset.

To start a new conversation, just send me any message.

💡 Tip: You can type 'exit', 'quit', 'restart', or 'change business' anytime to start over.
```

The session is completely deleted from the database, and sending any new message will start a fresh conversation from Step 1.

## API Endpoints

### 1. Main Webhook

**POST** `/webhook/webhook`

- Receives Twilio WhatsApp messages
- Manages conversation state
- Returns Twilio TwiML responses

### 2. Session Management

**GET** `/webhook/session/{whatsapp_number}`

- View session details for debugging
- Returns current state, business_id, thread_id, etc.

**POST** `/webhook/reset-session?whatsapp_number={number}`

- Reset a user's session
- Useful for testing or handling stuck sessions

## Session States

The system uses a state machine with four states:

1. `INITIAL` - First contact, ready to ask for name
2. `AWAITING_NAME` - Waiting for user to provide their name
3. `AWAITING_BUSINESS` - Waiting for business search input
4. `CHATTING` - Connected to business, chatting with AI agent

## Technical Features

### Fuzzy Business Matching

- Uses `SequenceMatcher` for similarity comparison
- 60% similarity threshold (configurable)
- Case-insensitive matching
- Returns closest match from all businesses in MongoDB

### Session Persistence

- Sessions stored in `session_collection` (MongoDB)
- Tracks: phone number, state, name, business_id, thread_id
- Automatic timestamp updates
- Survives server restarts

### Error Handling

- Graceful error messages for users
- Comprehensive logging for debugging
- Session reset on critical errors
- Empty message handling

## Setup Instructions

1. **Install Dependencies**

```bash
pip install -r requirements.txt
```

2. **Configure Twilio**

- Set up Twilio WhatsApp sandbox or production number
- Point webhook URL to: `https://your-domain.com/webhook/webhook`

3. **Environment Variables**
   Ensure your `.env` file has:

```
MONGO_URL=your_mongodb_connection_string
```

4. **Run the Server**

```bash
uvicorn main:app --reload
```

## Testing

### Test Conversation Flow

1. Send a message to your WhatsApp number
2. Provide your name when asked
3. Enter a business ID (e.g., "BUS-0001") or name
4. Start chatting with the AI agent

### Debug a Session

```bash
curl http://localhost:8000/webhook/session/whatsapp:+1234567890
```

### Reset a Session

```bash
curl -X POST "http://localhost:8000/webhook/reset-session?whatsapp_number=whatsapp:+1234567890"
```

## Database Collections Used

- `business_collection` - Business data lookup
- `session_collection` - WhatsApp session management

## Notes

- The webhook endpoint does NOT require authentication (for Twilio access)
- All other routes maintain their existing authentication
- Sessions are persistent and survive server restarts
- The fuzzy matching algorithm can be tuned by adjusting the threshold (currently 0.6)
