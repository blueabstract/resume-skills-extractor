# Resume Skill Extractor

A fullstack NLP web app built with Flask that extracts structured information from PDF resumes — including skills, job titles, years of experience, education, and contact info.

Built with Python, Flask, spaCy, and pdfplumber. Deployable for free on Render or Railway.

---

## Features

- Upload a PDF resume via drag-and-drop or file picker
- Extracts **skills** from a curated list of 80+ tech keywords
- Detects **job titles** using regex pattern matching
- Calculates **years of experience** from date ranges
- Pulls **contact info** (email, phone, LinkedIn, GitHub) and infers name via spaCy NER
- Identifies **education** (degrees, institutions)
- Clean, responsive UI — no page reloads, all AJAX

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Flask |
| NLP | spaCy (`en_core_web_sm`), regex |
| PDF parsing | pdfplumber |
| Frontend | Vanilla HTML/CSS/JS |
| Deployment | Render / Railway (free tier) |
| Process manager | Gunicorn |

---

## Project structure

```
resume-extractor/
├── app.py                  # Flask routes
├── utils/
│   ├── __init__.py
│   └── extractor.py        # NLP extraction logic
├── templates/
│   └── index.html          # Frontend UI
├── requirements.txt
├── render.yaml             # Render deployment config
├── Procfile                # For Railway / Heroku
├── runtime.txt
└── .gitignore
```

---

## Running locally

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/resume-extractor.git
cd resume-extractor
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Download the spaCy language model

```bash
python -m spacy download en_core_web_sm
```

### 5. Run the app

```bash
python app.py
```

Open your browser at `http://localhost:5000`

---

## Deploying for free on Render

### Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/resume-extractor.git
git push -u origin main
```

### Step 2 — Create a Render account

Go to [render.com](https://render.com) and sign up for free (use your GitHub account).

### Step 3 — Create a new Web Service

1. Click **New → Web Service**
2. Connect your GitHub account and select the `resume-extractor` repo
3. Render will auto-detect the `render.yaml` config file
4. If it doesn't, set these manually:
   - **Build command:** `pip install -r requirements.txt && python -m spacy download en_core_web_sm`
   - **Start command:** `gunicorn app:app`
   - **Environment:** Python 3
5. Choose the **Free** plan
6. Click **Create Web Service**

Render will build and deploy your app. It takes 2–4 minutes on first deploy.

> **Note:** Free tier on Render spins down after 15 minutes of inactivity. The first request after sleep takes ~30 seconds to wake up. This is normal.

---

## Alternative: Deploy on Railway

1. Go to [railway.app](https://railway.app) and sign in with GitHub
2. Click **New Project → Deploy from GitHub Repo**
3. Select your repo
4. Railway auto-detects the `Procfile` — no config needed
5. Add an environment variable if needed: `PORT=5000`
6. Click **Deploy**

Railway gives you $5 free credit per month — enough for light usage.

---

## How extraction works

### Skills
Scanned against a hardcoded list of 80+ skills across programming languages, frameworks, cloud tools, databases, and more. Uses regex word-boundary matching to avoid false positives.

### Job titles
Regex pattern looks for common title structures like `Senior Software Engineer`, `Data Scientist`, `Backend Developer`, etc. Handles optional seniority prefixes.

### Years of experience
Parses date ranges like `Jan 2020 – Dec 2023` or `2019 – Present` using regex, then sums the total. Falls back to explicit mentions like `5 years of experience`.

### Contact info
Email, phone, LinkedIn, and GitHub are extracted via regex. Candidate name is identified using spaCy's Named Entity Recognition (`PERSON` label) on the first 500 characters.

### Education
Matches degree keywords (B.S., M.Tech, Ph.D., MBA, etc.) and captures a snippet of surrounding context.

---

## Extending the project

Some ideas for going further:

- **Add more skills** — edit `SKILLS_DB` in `utils/extractor.py`
- **Export results as JSON/PDF** — add a download button on the frontend
- **ATS score** — compare skills against a job description
- **Store results in a database** — add SQLite or PostgreSQL with Flask-SQLAlchemy
- **Support DOCX** — use `python-docx` for Word document resumes
- **Better NER** — fine-tune a spaCy model on resume data for higher accuracy

---

## License

MIT