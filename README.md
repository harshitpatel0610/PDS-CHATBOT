# 🤖 PDS AI Chatbot

> An intent-driven Retrieval-Augmented Generation (RAG) chatbot for answering Public Distribution System (PDS) queries using curated government knowledge.

The **PDS AI Chatbot** is designed to help users obtain information about ration cards, eligibility, required documents, application procedures, and other Public Distribution System services.

The system combines **intent classification, entity extraction, workflow-based clarification, semantic retrieval, ChromaDB, and Gemini** to generate context-aware responses.

## 📌 Project Overview

PDS rules and procedures can vary by state, district, ration-card type, and service. This project uses an **Intent-Based RAG Architecture** so that the chatbot can identify the user's intent, extract relevant entities, retrieve appropriate knowledge, and provide that context to the LLM.

## 🏗️ System Architecture

```text
USER QUERY
    │
    ▼
Application / API
    │
    ▼
ROUTER
Intent Classification
    │
    ▼
ENTITY EXTRACTOR
State / District / Card Type
    │
    ▼
WORKFLOW
Missing information?
    │
    ├── YES ──► Clarification
    │
    └── NO
          │
          ▼
       RETRIEVER
       ChromaDB
          │
          ▼
   Retrieved Context
          │
          ▼
        GEMINI
          │
          ▼
    FINAL RESPONSE
```

## 🧠 Core Components

### 1. Intent Classification

The router determines what the user wants.

Example:

```text
"What documents are required for a ration card?"
                    ↓
          documents_required
```

The routing layer uses rule-based and embedding-based classification.

### 2. Entity Extraction

The chatbot extracts entities such as:

- State
- District
- Ration Card Type

Example:

```text
"What documents are required for an APL ration card in Gujarat?"

Intent: documents_required
State: Gujarat
Card Type: APL
```

### 3. Workflow / Slot Filling

When required information is missing, the workflow layer can ask clarification questions before retrieval.

### 4. RAG Retrieval

The retriever searches the knowledge base using semantic similarity and metadata such as:

```text
Intent
State
Card Type
Query semantics
```

The project uses BGE-M3 embeddings and ChromaDB.

### 5. LLM Response Generation

Retrieved knowledge is supplied as context to Gemini:

```text
User Query
     +
Retrieved Knowledge
     ↓
   Gemini
     ↓
Response
```

## 🔍 Why RAG?

PDS information can be state-specific and can change over time. RAG allows the application to retrieve relevant curated knowledge at inference time instead of relying exclusively on the LLM's pretrained knowledge.

```text
User
 ↓
Intent
 ↓
Entities
 ↓
Workflow
 ↓
Knowledge Retrieval
 ↓
Relevant PDS Context
 ↓
Gemini
 ↓
Answer
```

## ⚙️ Technology Stack

| Component | Technology |
|---|---|
| Language | Python |
| API | FastAPI |
| UI | Streamlit |
| LLM | Google Gemini |
| Embeddings | BAAI BGE-M3 |
| Vector Database | ChromaDB |
| Retrieval | Semantic + Metadata Filtering |
| Intent Classification | Rules + Embeddings |
| Testing | Python test suites |

## 🗂️ Project Structure

```text
PDS-AI-Chatbot/
│
├── assets/
├── chatbot/
│   ├── api/
│   ├── conversation/
│   ├── database/
│   ├── dialogue/
│   ├── entities/
│   ├── knowledge/
│   ├── llms/
│   ├── orchestrator/
│   ├── repositories/
│   ├── response_engine/
│   ├── router/
│   ├── services/
│   └── workflow/
│
├── rag/
│   ├── embeddings.py
│   ├── ingest.py
│   └── retriever.py
│
├── tests/
│   └── ...
│
├── ui/
├── utils/
├── app.py
├── main.py
├── intent_test_dataset.csv
├── requirements.txt
└── .gitignore
```

> `rag/vector_store/` is generated locally by ChromaDB and is excluded from version control.

## 🧩 Example Intents

Examples include:

```text
ration_card_apply
documents_required
ration_card_online_offline
ration_card_number_inquiry
ration_card_eligibility
ration_card_update
ration_card_types
```

The architectural responsibilities are separated as follows:

```text
Router       → What does the user want?
Entities     → Which entities are involved?
Workflow     → Is required information missing?
Retriever    → Where is the relevant knowledge?
LLM          → How should the response be formulated?
```

## 🧠 Retrieval Pipeline

```text
User Query
    │
    ▼
Intent
    │
    ▼
Entity Metadata
    │
    ▼
Metadata Filtering
    │
    ▼
Semantic Retrieval
    │
    ▼
Relevant Documents
    │
    ▼
Context Construction
    │
    ▼
Gemini
    │
    ▼
Final Answer
```

## 🗃️ Knowledge Base

The knowledge base can contain information related to:

- Ration card application
- Required documents
- Eligibility
- Ration card categories
- Online/offline application
- State-specific procedures
- Other PDS services

Knowledge can be associated with metadata such as:

```json
{
  "state": "Gujarat",
  "card_type": "APL",
  "intent": "documents_required"
}
```

## 🔐 Security

Sensitive configuration is stored in environment variables.

Example:

```env
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
LLM_PROVIDER=gemini
```

The `.env` file is excluded from Git. API keys should never be committed to the repository.

## 🧪 Testing

The project contains a dedicated `tests/` directory covering areas such as:

- Intent classification
- Router behavior
- Entity extraction
- Workflow behavior
- Retrieval
- Knowledge handling
- Dialogue behavior
- Matcher behavior
- RAG functionality

Example:

```text
tests/
├── rag/
├── test_router.py
├── test_entities.py
├── test_workflow.py
├── test_retrivel.py
└── ...
```

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/harshitpatel0610/AI-CHATBOT.git
cd AI-CHATBOT
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 🔑 Environment Configuration

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
LLM_PROVIDER=gemini
```

Do not commit `.env` to GitHub.

## ▶️ Running the Application

### Streamlit UI

```bash
streamlit run app.py
```

The UI is normally available at:

```text
http://localhost:8501
```

### FastAPI Backend

If the FastAPI application exposes `app` from `main.py`:

```bash
uvicorn main:app --reload
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## 📚 RAG Ingestion

The general RAG ingestion pipeline is:

```text
Knowledge Files
      ↓
Document Loading
      ↓
Processing / Chunking
      ↓
BGE-M3 Embeddings
      ↓
ChromaDB
```

The generated vector store is kept locally and excluded from version control.

## 🔎 Example Queries

```text
How can I apply for a ration card in Gujarat?
```

```text
What documents are required for a ration card in Gujarat?
```

```text
What types of ration cards are available?
```

```text
Can I apply for a ration card online?
```

```text
What documents are required for an APL ration card in Gujarat?
```

## 🛡️ State-Specific Retrieval

The retrieval layer uses metadata such as:

```text
state
intent
card_type
```

along with semantic retrieval to reduce the risk of returning irrelevant state-specific information.

Generic knowledge can also be used where appropriate.

## 🔄 Data Acquisition Architecture

The knowledge-acquisition workflow can be separated from chatbot runtime:

```text
Official Government Sources
          │
          ▼
    Data Acquisition
          │
          ▼
    Content Extraction
          │
          ▼
    Structured Knowledge
          │
          ▼
      Human Review
          │
          ▼
    Approved Knowledge
          │
          ▼
        RAG
```

This allows collected government information to be reviewed before being added to the production knowledge base.

## 📈 Design Principles

### Separation of Responsibilities

```text
Router       → Intent
Entities     → Context
Workflow     → Missing information
Retriever    → Knowledge
LLM          → Response generation
```

### Grounded Generation

The LLM receives relevant retrieved context rather than relying exclusively on pretrained knowledge.

### Testability

The architecture separates routing, entity extraction, workflow, retrieval, and response generation so they can be tested independently.

### Extensibility

The architecture can be extended with additional:

- Intents
- States
- PDS services
- Knowledge sources
- Retrieval strategies
- LLM providers

## 🎯 Future Improvements

- Expand state-specific PDS knowledge
- Add more official government data sources
- Improve document provenance
- Build automated knowledge acquisition
- Improve retrieval evaluation
- Expand end-to-end testing
- Add multilingual PDS support
- Improve conversational memory
- Production deployment
- Monitoring and observability
- Retrieval quality evaluation

## 👨‍💻 Project

**PDS AI Chatbot**

An AI-powered information assistant for Public Distribution System services.

Repository:

https://github.com/harshitpatel0610/AI-CHATBOT

## 📜 License

This project is intended for educational and development purposes.
