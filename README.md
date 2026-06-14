# 🎙️ Voice2Query AI

AI-Powered Speech-to-SQL and Text-to-SQL Database Assistant for University Database Exploration.

Voice2Query AI enables users to interact with relational databases using natural language voice commands or text queries. The system automatically converts user input into executable SQL queries, retrieves data from a PostgreSQL database, and visualizes results through an interactive Streamlit dashboard.

---

## 🚀 Features

* 🎤 Voice-to-Text Query Processing
* ⌨️ Natural Language Text Queries
* 🤖 AI-Powered SQL Generation using Ollama (Llama 3)
* 🗄️ PostgreSQL Database Integration
* 📊 Interactive Dashboard and Visual Analytics
* 🔍 Automatic Query Execution
* 📈 Charts and Data Insights
* 🔐 Environment-Based Configuration

---

## 🏗️ System Architecture

```text
Voice Input / Text Input
            │
            ▼
 Speech-to-Text Processing
            │
            ▼
 Natural Language Query
            │
            ▼
 Ollama (Llama 3)
 Text-to-SQL Generation
            │
            ▼
 SQL Validation
            │
            ▼
 PostgreSQL Database
            │
            ▼
 Streamlit Dashboard
            │
            ▼
 Results & Visualizations
```

---

## 🛠️ Technology Stack

| Component            | Technology             |
| -------------------- | ---------------------- |
| Programming Language | Python                 |
| Database             | PostgreSQL             |
| Frontend Dashboard   | Streamlit              |
| LLM Engine           | Ollama (Llama 3)       |
| Data Processing      | Pandas                 |
| Visualizations       | Plotly                 |
| ORM / Database Layer | SQLAlchemy             |
| Speech Processing    | Speechmatics (Planned) |

---

## 📂 Project Structure

```text
Voice2Query-AI/
│
├── app/
│   ├── dashboard/
│   ├── database/
│   ├── nlp/
│   ├── speech/
│   ├── utils/
│   └── config.py
│
├── requirements.txt
├── dashboard.py
├── .env.example
├── README.md
└── .gitignore
```

---

## ⚙️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/Madhumithra1321/Voice2Query-AI.git
cd Voice2Query-AI
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate:

Windows:

```bash
venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🗄️ Database Setup

Create a PostgreSQL database named:

```text
voice2query
```

Initialize sample tables:

```bash
python -m app.database.database_setup
```

---

## 🔧 Configuration

Create a local environment file:

```bash
Copy-Item .env.example .env
```

Update the values inside `.env`.

### PostgreSQL

```env
DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/voice2query
```

### Ollama (Default)

```env
TEXT_TO_SQL_PROVIDER=ollama
OLLAMA_MODEL=llama3:latest
OLLAMA_URL=http://localhost:11434/api/generate
---

## ▶️ Running the Application

Start the dashboard:

```bash
streamlit run dashboard.py
```

Open:

```text
http://localhost:8501
```

---

## 📊 Example Queries

* Show top 10 students by marks
* List all professors
* Display students from Naples
* Find highest scoring students
* Show courses with more than 5 credits

## 👥 Done by

* Madhumithra Balasubramanian
* Aya Hechaichi 
* Alina Siddiqui

University of Naples Federico II

