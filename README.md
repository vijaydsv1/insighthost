# InsightHost – Voice-Enabled AI Experience Center Assistant

## Overview

**InsightHost** is an AI-powered voice assistant designed for the **Accion Xperience Center**.
It allows visitors to interact with company information using **natural language or voice**, providing instant answers about:

* Company overview
* Services
* Projects
* Industry expertise
* Key personnel

The system uses **Retrieval-Augmented Generation (RAG)** to ensure responses are grounded in approved knowledge sources.

---

## Features

* Voice interaction (Speech-to-Text and Text-to-Speech)
* AI assistant powered by LLMs
* Retrieval-Augmented Generation (RAG)
* Pinecone vector database
* Guardrails for secure and controlled responses
* Metadata-based citations for answers
* React frontend interface
* FastAPI backend
* OpenAI + Groq fallback for LLM reliability

---

## System Architecture

User Voice / Text
↓
Speech-to-Text
↓
Input Validation & Guardrails
↓
Intent Classification
↓
RAG Retrieval (Pinecone Vector Database)
↓
LLM Response Generation (OpenAI / Groq)
↓
Output Filtering
↓
Text + Voice Response

---

## Tech Stack

### Backend

* FastAPI
* Python
* LangChain

### AI / ML

* OpenAI GPT-4o-mini
* Groq Llama Models
* HuggingFace Embeddings (MiniLM)

### Data & Retrieval

* Pinecone Vector Database
* JSON / CSV Knowledge Base

### Voice Processing

* SpeechRecognition
* ElevenLabs Text-to-Speech

### Frontend

* React (Voice Assistant UI)

---

## Project Structure

```
insighthost/
│
├── api/                # FastAPI routes
├── app/                # Application entry point
├── guardrails/         # Input validation & safety filters
├── pipeline/           # Assistant orchestration pipeline
├── rag/                # Retrieval-Augmented Generation logic
├── speech/             # STT and TTS modules
├── knowledge_base/     # Company data and scraped content
├── ui/                 # Frontend interface
│
├── create_pinecone_index.py
├── voice_assistant.py
├── voice_client.py
└── README.md
```

---

## Setup Instructions

### 1. Clone the Repository

```
git clone https://github.com/your-username/insighthost.git
cd insighthost
```

---

### 2. Create Virtual Environment

```
python -m venv venv
source venv/bin/activate
```

---

### 3. Install Dependencies

```
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Create a `.env` file in the project root.

```
OPENAI_API_KEY=your_openai_key
GROQ_API_KEY=your_groq_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX=insighthost
ELEVENLABS_API_KEY=your_elevenlabs_key
```

---

### 5. Create Pinecone Vector Index

```
python create_pinecone_index.py
```

---

### 6. Upload Knowledge Base to Vector DB

```
python -m rag.vector_store
```

---

### 7. Start the Backend Server

```
uvicorn app.main:app --reload
```

---

### 8. Access the Assistant UI

Open in browser:

```
http://localhost:8000/ui
```

---

## Example Queries

* "What services does Accion Labs provide?"
* "Tell me about Accion Labs AI capabilities."
* "Which industries does Accion Labs work with?"

---

## Guardrails & Safety

The system implements multiple safeguards:

* Input validation
* Restricted topic filtering
* Intent classification
* Response moderation
* Knowledge-base-only responses

This ensures **secure and factual responses**.

---

## Future Improvements

* Knowledge graph integration
* Multi-language support
* Visitor analytics dashboard
* Context-aware conversations
* Real-time enterprise data integration

---


## License

This project is developed for the **Accion Innovation Hackathon** and is intended for demonstration and research purposes.
