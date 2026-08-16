# ComplianceGuard

An AI-powered legal contract auditor. Upload a contract PDF, and Google's Gemini API extracts high-risk clauses, generates a plain-English summary, and assigns a risk score (0–100) — all shown on a simple dashboard.

**Live:** https://complianceguard-h9me.onrender.com

---

## How it works

1. User uploads a contract PDF via the upload form.
2. `pypdf` extracts raw text from every page.
3. The text is sent to `gemini-2.5-flash` with a system instruction telling it to act as a corporate legal auditor.
4. Gemini returns a summary and a `RISK_SCORE: <number>` line, which is parsed out with simple string matching.
5. Vendor name, AI summary, and risk score are saved to the `Contract` model.
6. The dashboard lists all audited contracts, newest first.

---

## Tech Stack

| Layer | Choice |
|---|---|
| Backend | Django 5.2.14 |
| API layer | Django REST Framework 3.17.1 (serializers defined, not yet wired to routes) |
| AI | Google Gemini (`google-genai` 2.7.0) — model `gemini-2.5-flash` |
| PDF parsing | pypdf 6.12.2 |
| Database | SQLite (see **Known Issues** below) |
| Deployment | Render, via Gunicorn |

---

## Project Structure

```
ComplianceGuard/
├── compliance_main/       # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── auditor/                # Core app
│   ├── models.py           # Contract, Clause, ComplianceReport
│   ├── views.py             # DashboardView, ContractUploadView
│   ├── serializers.py       # DRF serializers (Contract, Clause)
│   ├── ai_utility.py        # PDF extraction + Gemini call
│   └── admin.py
├── templates/
│   ├── base.html
│   ├── upload.html
│   └── dashboard.html
├── requirements.txt
├── Procfile
└── manage.py
```

---

## Data Models

- **Contract** — `vendor_name`, `risk_score`, `upload_at`, `ai_summary`
- **Clause** — linked to a Contract, `clause_type`, `extracted_text` (defined but not yet populated anywhere in the code)
- **ComplianceReport** — linked to a Contract, `report_name`, `final_decision` (approved/rejected) (defined but not yet used by any view)

---

## Routes

| URL | View | Purpose |
|---|---|---|
| `/` | redirects to `/upload/` | Landing |
| `/upload/` | `ContractUploadView` | Upload a PDF, trigger AI analysis |
| `/dashboard/` | `DashboardView` | List all audited contracts |
| `/admin/` | Django admin | — |

---

## Setup (local)

```bash
git clone https://github.com/KhushyanKalla/ComplianceGuard.git
cd ComplianceGuard

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_key_here
```

Then:

```bash
python manage.py migrate
python manage.py runserver
```

Visit `http://127.0.0.1:8000/upload/`.

---

## Known Issues — read this honestly

I'm flagging these because you said this thing has "an unresolved issue" and these are the things that would actually cause one in production:

1. **SQLite on Render will lose your data.** `settings.py` has `ENGINE: django.db.backends.sqlite3`, but Render's filesystem is ephemeral — every redeploy or dyno restart wipes `db.sqlite3`. You already have `psycopg2-binary` in `requirements.txt`, which means you *intended* to use Postgres but never switched `DATABASES` over. This is almost certainly why contracts "disappear" after a while. Fix: spin up a Render Postgres instance, set `DATABASE_URL` as an env var, and point `DATABASES['default']` at it (use `dj-database-url` to parse it cleanly).

2. **Hardcoded `SECRET_KEY` committed to the repo.** It's sitting in plaintext in `settings.py`. This is the same class of mistake as the API key leak you already had to clean up with GitHub Push Protection. Move it to `.env` like you did with `GEMINI_API_KEY`.

3. **No `.env.example`.** Anyone cloning this repo has to guess that `GEMINI_API_KEY` is required. Add a `.env.example` with the key name (no value) so setup isn't guesswork.

4. **Risk score parsing is fragile.** In `views.py`, you parse `RISK_SCORE:` out of Gemini's free-text response using `line.split(":")[1]`. If Gemini ever changes its output format even slightly (extra colon, different phrasing), this silently falls back to `risk_score = 50` with no logging. You won't know it broke until someone notices every contract scoring exactly 50.

5. **Broad exception handling hides real errors.** The `except Exception as e` in `ContractUploadView.post` catches everything — bad PDF, Gemini API down, network timeout, bad API key — and shows the same generic "Google AI Server is currently busy" message for all of them. `e` isn't logged anywhere. Add `logging` at minimum so you can see what actually failed.

6. **DRF is installed but unused.** `serializers.py` exists but there's no `urls.py` entry routing to any API views — so DRF isn't doing anything right now. Either wire it up (if you want a JSON API) or drop it from `requirements.txt` to keep the stack honest.

None of these are "your code is bad" — the logic flow (extract → analyze → parse → save) is clean and correct. These are the specific gaps between "works on my machine" and "production-safe," which is exactly the kind of thing interviewers will poke at if you mention this project.

---

## Roadmap (suggested, not yet built)

- [ ] Switch to Postgres on Render
- [ ] Populate `Clause` model from Gemini's response (structured clause-by-clause breakdown instead of one summary blob)
- [ ] Wire up the DRF serializers to real API endpoints
- [ ] Add proper logging around the Gemini call
- [ ] Contract detail view (currently only dashboard list + upload exist)
