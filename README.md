# Voice2Query

Streamlit dashboard for asking a PostgreSQL database questions in natural language.
The app supports text input, browser microphone recording, and optional audio-file
transcription once you add your Speechmatics API key.

## Setup

1. Install Python 3.10+.
2. Create and activate a virtual environment.
3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and update the values:

```powershell
Copy-Item .env.example .env
```

5. Create a PostgreSQL database named `voice2query`, then seed sample tables:

```powershell
python -m app.database.database_setup
```

6. Start the dashboard:

```powershell
streamlit run dashboard.py
```

## Configuration

`DATABASE_URL` controls the PostgreSQL connection.

For text-to-SQL, the default provider is local Ollama:

```env
TEXT_TO_SQL_PROVIDER=ollama
OLLAMA_MODEL=llama3:latest
```

You can switch to OpenAI by setting:

```env
TEXT_TO_SQL_PROVIDER=openai
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-4.1-mini
```

When you receive the Speechmatics key, add:

```env
SPEECHMATICS_API_KEY=your_api_key
SPEECHMATICS_LANGUAGE=en
```
