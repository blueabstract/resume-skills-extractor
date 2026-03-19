# Resume Skill Extractor + ATS Job Match Scorer

A fullstack NLP + ML web app built with Flask that extracts structured information from PDF resumes and scores them against job descriptions using TF-IDF vectorization and cosine similarity.

Built with Python, Flask, spaCy, scikit-learn, and pdfplumber. Deployed for free on Railway.

---

## Live Demo

> Replace this with your Railway URL after deploying
> e.g. `https://resume-skills-extractor-production.up.railway.app`

---

## Features

### Resume Extractor
- Upload a PDF resume via drag-and-drop or file picker
- Extracts **skills** from a curated list of 100+ tech keywords with confidence scoring
- Detects **job titles** using multi-pass regex + spaCy NER with deduplication
- Calculates **years of experience** from date ranges (handles "Present", month+year, etc.)
- Pulls **contact info** — email, phone, LinkedIn, GitHub, portfolio website
- Identifies **education** (degrees, institutions)
- Extracts **professional summary** if present

### ATS Job Match Scorer (ML)
- Paste any job description alongside your resume
- Scores resume-to-JD match from 0–100 using **TF-IDF + cosine similarity**
- Shows **matched skills** and **missing skills**
- **Category breakdown** — scores by skill domain (Languages, Frontend, Backend, Cloud, etc.)
- Highlights **bonus skills** — things you have that aren't in the JD but are still valuable
- Animated score ring UI with verdict (Excellent / Good / Partial / Low match)

---

## How the ML Works

The ATS scorer uses two signals blended together for a calibrated final score:

**1. TF-IDF Cosine Similarity (60% weight)**
Both the resume and job description are converted into TF-IDF feature vectors using scikit-learn's `TfidfVectorizer` with trigrams (`ngram_range=(1,3)`) and log normalization. Cosine similarity is then computed between the two vectors — measuring the angle between them in high-dimensional space. A score of 1.0 means identical, 0.0 means no overlap.

**2. Keyword Match Ratio (40% weight)**
Skills are extracted from both texts using regex pattern matching against a curated database of 100+ tech skills grouped by category. The ratio of matched keywords to total JD keywords gives a direct skill coverage score.

**Final score = (TF-IDF similarity × 0.6) + (keyword ratio × 0.4)**

This blend makes the score robust — TF-IDF captures semantic context and phrasing, while keyword matching captures exact skill names.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Flask |
| ML / Scoring | scikit-learn (TF-IDF, cosine similarity) |
| NLP | spaCy (`en_core_web_sm`), regex |
| PDF parsing | pdfplumber |
| Frontend | Vanilla HTML / CSS / JS |
| Deployment | Railway (free tier) |
| Process manager | Gunicorn |

---

## Project Structure

```
resume-extractor/
├── utils/
│   ├── __init__.py
│   ├── extractor.py        # NLP extraction logic
│   └── ats_scorer.py       # ML scoring — TF-IDF + cosine similarity
├── templates/
│   └── index.html          # Frontend UI (two tabs)
├── uploads/                # Temp folder (auto-cleared after each request)
├── app.py                  # Flask routes (/extract and /ats-score)
├── requirements.txt
├── Procfile                # Railway start command
├── runtime.txt             # Python version pin
└── .gitignore
```

---

## Running Locally

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

## API Endpoints

### `POST /extract`
Extracts structured data from a PDF resume.

**Request:** `multipart/form-data`
| Field | Type | Description |
|---|---|---|
| `resume` | file | PDF resume (max 5MB) |

**Response:**
```json
{
  "contact": { "name": "...", "email": "...", "phone": "...", "linkedin": "...", "github": "...", "website": "..." },
  "skills": ["Python", "Flask", "Docker", "..."],
  "job_titles": ["Senior Software Engineer", "..."],
  "experience": { "total_years": 5, "date_ranges": [...] },
  "education": ["B.Tech Computer Science, IIT Bombay, 2018"],
  "summary": "...",
  "word_count": 423
}
```

---

### `POST /ats-score`
Scores a resume against a job description using ML.

**Request:** `multipart/form-data`
| Field | Type | Description |
|---|---|---|
| `resume` | file | PDF resume (max 5MB) |
| `job_description` | string | Full job description text |

**Response:**
```json
{
  "score": 74,
  "verdict": "Good match",
  "verdict_color": "blue",
  "matched_skills": ["Python", "Docker", "AWS"],
  "missing_skills": ["Kubernetes", "Terraform"],
  "bonus_skills": ["Flask", "Redis"],
  "category_scores": {
    "Languages": { "score": 80, "matched": ["Python"], "missing": [] },
    "Cloud / DevOps": { "score": 50, "matched": ["Docker", "AWS"], "missing": ["Kubernetes"] }
  },
  "keyword_match_pct": 68,
  "tfidf_similarity": 32.4,
  "total_jd_keywords": 12,
  "total_resume_keywords": 18
}
```

---

## Deploying for Free on Railway

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
2. Select your `resume-skills-extractor` repo and click **Deploy Now**
3. Go to **Settings → Build** and set the Custom Build Command:
   ```
   pip install -r requirements.txt
   ```
4. Go to **Settings → Deploy** and set the Start Command:
   ```
   gunicorn app:app
   ```
5. Click the purple **Deploy** button at the top

### Step 4 — Get your live URL

1. Go to **Settings → Networking**
2. Click **Generate Domain**
3. Your app is live at the generated URL

> Railway gives you $5 free credit per month which resets monthly. A simple Flask app like this uses roughly $0.50–$1.00/month — well within the free tier. No card required.

---

## Extending the Project

- **Semantic skill matching** — replace keyword matching with `sentence-transformers` for fuzzy skill detection
- **Resume quality scorer** — train a regression model on resume features to output a quality score
- **Job role predictor** — classify what role a candidate is best suited for using a scikit-learn classifier
- **Export results as PDF** — generate a downloadable match report
- **Store results in a database** — add SQLite with Flask-SQLAlchemy for history tracking
- **Support DOCX** — use `python-docx` to accept Word document resumes
- **Resume summarizer** — use a Hugging Face model to auto-generate a professional summary

---

## License

MIT