# AI Expense Tracker

An AI-powered expense tracker built with Django REST Framework and Django templates.

## Features

- **Receipt Scanning** — Upload receipt images; AI extracts amount, date, merchant, and category
- **Manual Entry** — Add expenses via a clean form
- **Dashboard** — Overview of today, week, and month spending with Chart.js breakdown
- **Expense List** — Filterable, sortable list with table (desktop) and card (mobile) layouts
- **LLM Fallback Chain** — Uses Google Gemini 2.0 Flash, falls back to Groq Llama 4 Scout Vision

## Tech Stack

- **Backend**: Django 4.2+, Django REST Framework
- **Frontend**: Django Templates, Tailwind CSS (CDN), Chart.js (CDN)
- **Database**: PostgreSQL (Supabase) via dj-database-url
- **AI**: Google Gemini 2.0 Flash → Groq Llama 4 Scout Vision fallback

## Setup

1. **Clone the repo**

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add:
   - `DJANGO_SECRET_KEY` — any random string
   - `DATABASE_URL` — your Supabase PostgreSQL connection string
   - `GEMINI_API_KEY` — from https://aistudio.google.com (free)
   - `GROQ_API_KEY` — from https://console.groq.com (free)
   - `DEBUG=True` for development

5. **Run migrations**
   ```bash
   python manage.py makemigrations expenses
   python manage.py migrate
   ```

6. **Run the server**
   ```bash
   python manage.py runserver
   ```

7. **Login** at http://127.0.0.1:8000
   - Email: `admin@kharchatrack.com`
   - Password: `kharcha123`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/expenses/` | List expenses (filter: `?year=&month=&category=`) |
| POST | `/api/expenses/` | Create expense |
| GET | `/api/expenses/{id}/` | Get expense detail |
| PUT | `/api/expenses/{id}/` | Update expense |
| DELETE | `/api/expenses/{id}/` | Delete expense |
| GET | `/api/expenses/stats/` | Dashboard stats |
| POST | `/api/expenses/upload_receipt/` | Upload receipt image for extraction |

## Getting Free API Keys

- **Gemini**: Visit https://aistudio.google.com → Get API key (1500 requests/day free)
- **Groq**: Visit https://console.groq.com → Sign up → Create API key (free tier)
