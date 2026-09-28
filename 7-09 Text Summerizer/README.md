# Text Summarizer

A Django web app and REST API for summarizing text. It uses the Qwen 3 model through a local Ollama server when available, and falls back to a built-in extractive summarizer if Ollama cannot be reached.

## Requirements

- Python 3.10 or newer
- Ollama (optional; required only for Qwen-powered summaries)

## Setup on Windows

Open PowerShell in the project folder and run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open <http://127.0.0.1:8000/> to use the web app.

### Enable Qwen with Ollama

Install [Ollama](https://ollama.com/), then download the configured model and start its server in a separate PowerShell window:

```powershell
ollama pull qwen3:8b
ollama serve
```

The app defaults to `OLLAMA_URL=http://127.0.0.1:11434` and `QWEN_MODEL=qwen3:8b`. To override either value, set it in the PowerShell session before starting Django:

```powershell
$env:OLLAMA_URL = "http://127.0.0.1:11434"
$env:QWEN_MODEL = "qwen3:8b"
python manage.py runserver
```

If Ollama is unavailable, summaries are generated locally with a simple extractive algorithm. The local fallback does not use an AI model.

## API

`POST /api/summarize/` accepts JSON with `text` and an optional `style`:

```json
{
  "text": "Text to summarize. Include at least 80 characters...",
  "style": "balanced"
}
```

Valid styles are `concise`, `balanced` (the default), and `detailed`. Text must contain 80 to 20,000 characters.

Example using PowerShell:

```powershell
$body = @{ text = "A sufficiently long text goes here..."; style = "concise" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/summarize/" -Method Post -ContentType "application/json" -Body $body
```

The response contains the generated `summary`, the `model` label, and the selected `style`. Invalid input returns validation details.

## Tests

Run the Django test suite with:

```powershell
python manage.py test
```

## Project Structure

- `config/` - Django project settings and URL configuration
- `summarizer/` - API, input validation, and summarization logic
- `templates/` and `static/` - Web interface
- `db.sqlite3` - Local SQLite database