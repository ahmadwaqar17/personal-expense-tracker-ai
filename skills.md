Build a Django web application called "KharchaTrack" — an AI-powered expense tracker for a single user.

---

## LLM STRATEGY FOR RECEIPT IMAGE EXTRACTION

Use the following free LLMs that natively support image/vision input. 
Implement a fallback chain — try primary first, if it fails or quota is hit, try secondary.

PRIMARY — Google Gemini 2.0 Flash
- Provider: Google AI Studio (aistudio.google.com) — completely free, no credit card
- Model string: gemini-2.0-flash
- SDK: google-generativeai (official Python SDK)
- Vision support: yes, accepts image bytes inline (JPEG, PNG, WEBP, PDF)
- Free limits: 1500 requests/day, 15 requests/minute — more than enough for personal use
- API key env var: GEMINI_API_KEY

SECONDARY FALLBACK — Groq (Llama 4 Scout Vision)
- Provider: Groq Cloud (console.groq.com) — free tier, no credit card
- Model string: meta-llama/llama-4-scout-17b-16e-instruct
- SDK: groq (official Python SDK) or direct REST call
- Vision support: yes, accepts base64-encoded image in messages content array
- Free limits: generous daily token quota on free tier
- API key env var: GROQ_API_KEY

The extraction module should:
- Accept image bytes + mime type as input
- Try Gemini first
- On any exception or empty response, silently fall back to Groq
- If both fail, return None so the UI can prompt the user to fill in details manually
- Parse the JSON response from whichever LLM succeeded
- Never crash the app — all LLM calls wrapped in try/except

The extraction prompt sent to BOTH models should ask for:
amount (float, in PKR), date (YYYY-MM-DD), time (HH:MM 24hr), 
merchant name, category (Food/Transport/Shopping/Utility/Health/Other), 
and a one-line description — returned as strict JSON only, no explanation or markdown.

---

## STACK & CONSTRAINTS
- Backend: Django 4.2+, plain views and JsonResponse — no DRF
- Frontend: Django templates, Tailwind CSS via CDN, Chart.js via CDN
- Responsive: mobile-first, works on phone and desktop
- Storage: NO database at all. One flat JSON file at data/expenses.json for all records
- Sessions: use Django's file-based session backend so no DB migration is needed
- Auth: single hardcoded user — email admin@kharchatrack.com, password kharcha123
  Validated manually in view, session flag set on success — no Django User model or auth DB tables
- Currency: PKR everywhere, formatted as PKR 1,500.00
- No local models, no Ollama, no self-hosted inference

---

## DATA STRUCTURE
Each expense stored in the JSON array has: a UUID id, date, time, amount, currency (always PKR), 
merchant name, category, description, source (either "receipt" or "manual"), and created_at timestamp.
The JSON file is auto-created with an empty array if it does not exist on first run.

---

## PAGES & FEATURES

Login page — email + password, session-based, redirect to dashboard on success.

Dashboard — shows total spent today, this week, and this month in PKR. 
Shows last 5 transactions as cards. Shows a category-wise spending breakdown 
using Chart.js doughnut or bar chart. Two prominent action buttons: Upload Receipt and Add Manually.

Upload Receipt page — drag-and-drop or click-to-browse image upload area.
After selecting image, show a preview. On submit, send to LLM extraction chain.
Display the extracted fields in an editable confirmation form so user can correct 
any mistakes before saving. Show a loading spinner while extraction is running.
If extraction fails, show a message and let user fill the form manually.

Manual Entry page — form with date picker (default today), time picker (default now), 
PKR amount field, merchant name, category dropdown, and description. Clean and simple.

Expense List page — shows all expenses newest first. On mobile: cards layout. 
On desktop: table layout. Each entry shows date, merchant, category badge (color-coded), 
PKR amount, source badge (receipt or manual), and a delete button.
Filter controls for month and category at the top.

Delete endpoint — removes the record by UUID from JSON, redirects back with a flash message.

---

## UI APPROACH
Color scheme: deep navy (#1e3a5f) as primary, emerald green (#10b981) as accent, 
white cards on light gray background.
Category badges: Food=orange, Transport=blue, Shopping=purple, Utility=yellow, Health=red, Other=gray.
Navbar with app name, links, and logout. Flash messages for all actions.
All PKR amounts formatted with comma separators.

---

## SETUP & RUNNING APPROACH
- requirements.txt includes: Django, google-generativeai, groq, python-dotenv, Pillow
- .env file holds GEMINI_API_KEY and GROQ_API_KEY and DJANGO_SECRET_KEY
- settings.py loads .env via python-dotenv at top
- SESSION_ENGINE set to django.contrib.sessions.backends.file
- Only migration needed is for sessions — or use cookie-based sessions to avoid even that
- data/ directory auto-created by the app on startup if missing
- Uploaded images are read into memory, sent to LLM, then discarded — no permanent media storage needed
- README explains how to get free Gemini key from aistudio.google.com 
  and free Groq key from console.groq.com, and exact steps to run locally

---

## KEY IMPLEMENTATION NOTES FOR THE AI
- The LLM extraction module is the most critical piece — build it first and make it bulletproof
- The fallback chain (Gemini → Groq) must be transparent to the rest of the app
- JSON storage helpers must handle concurrent writes safely (read → modify → write pattern)
- Never import or use django.contrib.auth User model
- The session check decorator must be applied to every protected view
- All monetary display must go through a single formatting helper so PKR formatting is consistent
- Generate all files completely without truncation