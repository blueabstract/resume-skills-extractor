# Resume Skill Extractor

A fullstack NLP web app built with Flask that extracts structured information from PDF resumes — including skills, job titles, years of experience, education, and contact info.

Built with Python, Flask, spaCy, and pdfplumber. Deployed for free on Railway.

---

## Live Demo

> Replace this with your Railway URL after deploying
> e.g. `https://resume-skills-extractor-production.up.railway.app`

---

## Features

- Upload a PDF resume via drag-and-drop or file picker
- Extracts **skills** from a curated list of 100+ tech keywords with confidence scoring
- Detects **job titles** using multi-pass regex + spaCy NER with deduplication
- Calculates **years of experience** from date ranges (handles "Present", month+year, etc.)
- Pulls **contact info** — email, phone, LinkedIn, GitHub, portfolio website
- Identifies **education** (degrees, institutions)
- Extracts **professional summary** if present
- Clean, responsive UI — no page reloads, all AJAX

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Flask |
| NLP | spaCy (`en_core_web_sm`), regex |
| PDF parsing | pdfplumber |
| Frontend | Vanilla HTML/CSS/JS |
| Deployment | Railway (free tier) |
| Process manager | Gunicorn |

---

## Project structure

```
resume-extractor/
├── utils/
│   ├── __init__.py
│   └── extractor.py        # NLP extraction logic
├── templates/
│   └── index.html          # Frontend UI
├── uploads/                # Temp folder (auto-cleared after each request)
├── app.py                  # Flask routes
├── requirements.txt
├── Procfile                # Railway / gunicorn start command
├── runtime.txt             # Python version pin
└── .gitignore
```

---

## Running locally

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/resume-skills-extractor.git
cd resume-skills-extractor
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python app.py
```

Open your browser at `http://localhost:5000`

---

## Deploying for free on Railway

### Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/resume-skills-extractor.git
git push -u origin main
```

### Step 2 — Create a Railway account

Go to [railway.app](https://railway.app) and sign up for free using your GitHub account. No card required.

### Step 3 — Deploy

1. Click **New Project → GitHub Repository**
2. Select your `resume-skills-extractor` repo
3. Click **Deploy Now**
4. Go to **Settings → Build** and set the custom build command:
   ```
   pip install -r requirements.txt
   ```
5. Go to **Settings → Deploy** and set the start command:
   ```
   gunicorn app:app
   ```
6. Click the **Deploy** button at the top

### Step 4 — Get your live URL

1. Go to **Settings → Networking**
2. Click **Generate Domain**
3. Your app is live at the generated URL

> Railway gives you $5 free credit per month which resets monthly. A simple Flask app like this uses roughly $0.50–$1.00/month, so you're well within the free tier.

---

## How extraction works

### Skills
Scanned against a list of 100+ skills across programming languages, frameworks, cloud tools, databases, and more. Uses a confidence scoring system — skills found inside a dedicated "Skills" section score higher than those found in the body text.

### Job titles
Three-pass extraction: regex pattern matching for title structures like `Senior Software Engineer`, a hardcoded list of 30+ known standalone titles, and a line-by-line scan of the experience section. Substring deduplication removes shorter titles if a longer match already exists.

### Years of experience
Parses date ranges like `Jan 2020 – Dec 2023` or `2019 – Present` using regex. Filters out bad years, deduplicates repeated ranges, and sorts by most recent. Falls back to explicit mentions like `5 years of experience`.

### Contact info
Email, phone (international-aware), LinkedIn, GitHub, and portfolio website are extracted via regex. Name is identified using spaCy's Named Entity Recognition (`PERSON` label) on the first 600 characters, with a fallback to the first short capitalized line.

### Education
Matches degree keywords (B.S., M.Tech, Ph.D., MBA, etc.) and captures surrounding context. Deduplicates by degree type.

### Professional summary
Looks for a summary/objective/profile section header and extracts the text beneath it (up to 400 characters).

---

## Extending the project

- **Add more skills** — edit `SKILLS_DB` in `utils/extractor.py`
- **Export results as JSON** — add a download button on the frontend
- **ATS score** — compare extracted skills against a job description
- **Store results in a database** — add SQLite with Flask-SQLAlchemy
- **Support DOCX** — use `python-docx` for Word document resumes
- **Better NER** — fine-tune a spaCy model on resume data for higher accuracy

---

## License

MIT