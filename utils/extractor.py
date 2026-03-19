import re
import pdfplumber
import spacy

nlp = spacy.load("en_core_web_sm")

# ── Skills DB (grouped for section-aware matching) ─────────────────────────────
SKILLS_DB = [
    # Programming languages
    "python", "javascript", "typescript", "java", "c++", "c#", "c", "go",
    "rust", "kotlin", "swift", "ruby", "php", "scala", "r", "matlab", "bash",
    "shell", "powershell", "perl", "dart", "elixir", "haskell", "lua",
    # Web / frontend
    "html", "css", "sass", "scss", "react", "vue", "angular", "next.js",
    "nuxt", "svelte", "tailwind", "bootstrap", "jquery", "webpack", "vite",
    "redux", "graphql", "rest api", "web sockets",
    # Backend / frameworks
    "flask", "django", "fastapi", "express", "spring boot", "rails",
    "laravel", "node.js", "asp.net", "gin", "fiber", "nestjs",
    # Data / ML / AI
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "pytorch", "tensorflow", "keras", "scikit-learn",
    "pandas", "numpy", "matplotlib", "seaborn", "plotly", "spark", "hadoop",
    "airflow", "mlflow", "hugging face", "langchain", "openai", "llm",
    "data analysis", "data visualization", "feature engineering",
    "model training", "transformers",
    # Cloud / DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "terraform",
    "ansible", "ci/cd", "jenkins", "github actions", "gitlab ci", "linux",
    "nginx", "apache", "serverless",
    # Databases
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "sqlite",
    "dynamodb", "cassandra", "oracle", "sql server", "firebase", "supabase",
    "neo4j", "influxdb",
    # Tools / soft
    "git", "github", "gitlab", "jira", "confluence", "figma", "postman",
    "tableau", "power bi", "excel", "agile", "scrum", "kanban",
    "test driven development", "tdd", "microservices", "system design",
    "object oriented programming", "oop", "solid",
]

# ── Titles: scored patterns ────────────────────────────────────────────────────
SENIORITY = r"(senior|sr\.?|junior|jr\.?|lead|principal|staff|head of|chief|vp of|director of|manager of|associate|mid[- ]level)?"
DOMAIN = (
    r"(software|frontend|front[- ]end|backend|back[- ]end|fullstack|full[- ]stack|"
    r"data|ml|ai|machine learning|devops|cloud|platform|site reliability|sre|"
    r"product|project|program|engineering|research|qa|quality assurance|"
    r"ux|ui|ux/ui|ui/ux|security|cyber|network|systems|mobile|ios|android|"
    r"embedded|firmware|blockchain|web3|game)"
)
ROLE = (
    r"(engineer|developer|dev|scientist|analyst|architect|manager|lead|intern|"
    r"consultant|specialist|designer|officer|technician|administrator|admin|"
    r"director|head|vp|president|founder|co-founder|cto|ceo|coo)"
)
TITLE_PATTERN = re.compile(
    rf"{SENIORITY}\s*{DOMAIN}\s*{ROLE}", re.I
)

# Standalone roles (e.g. "Product Manager", "Data Analyst")
STANDALONE_TITLES = re.compile(
    r"\b(product manager|project manager|program manager|data analyst|"
    r"business analyst|data engineer|devops engineer|site reliability engineer|"
    r"machine learning engineer|ai engineer|research engineer|research scientist|"
    r"solutions architect|cloud architect|security engineer|mobile developer|"
    r"ios developer|android developer|game developer|blockchain developer|"
    r"technical lead|tech lead|engineering manager|vp of engineering|"
    r"chief technology officer|chief executive officer|software architect)\b",
    re.I
)

# ── Date range patterns ────────────────────────────────────────────────────────
MONTH = (
    r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|"
    r"jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|"
    r"oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
)
DATE_RANGE_PATTERN = re.compile(
    rf"(?:{MONTH}[\s.,]*)?"
    rf"(\d{{4}})"
    rf"\s*[-–—to/]+\s*"
    rf"(?:{MONTH}[\s.,]*)?"
    rf"(\d{{4}}|present|current|now|today)",
    re.I
)
EXPLICIT_YEARS = re.compile(r"(\d+)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:experience|exp)", re.I)

DEGREE_PATTERN = re.compile(
    r"\b(b\.?\s*s\.?|b\.?\s*e\.?|b\.?\s*tech\.?|b\.?\s*sc\.?|"
    r"bachelor(?:\'?s)?(?:\s+of\s+\w+)?|"
    r"m\.?\s*s\.?|m\.?\s*e\.?|m\.?\s*tech\.?|m\.?\s*sc\.?|"
    r"master(?:\'?s)?(?:\s+of\s+\w+)?|"
    r"ph\.?\s*d\.?|doctorate|"
    r"mba|m\.?\s*b\.?\s*a\.?|"
    r"associate(?:\'?s)?(?:\s+of\s+\w+)?|"
    r"b\.?\s*a\.?|bachelor\s+of\s+arts|"
    r"b\.?\s*com\.?|m\.?\s*com\.?)\b",
    re.I,
)

SECTION_HEADERS = re.compile(
    r"^[\s]*(?:technical\s+)?(?:skills?|expertise|technologies|tools|"
    r"proficiencies|competencies|languages?|frameworks?)[\s:]*$",
    re.I | re.MULTILINE
)

EXPERIENCE_HEADERS = re.compile(
    r"^[\s]*(?:work\s+)?(?:experience|employment|history|career|positions?)[\s:]*$",
    re.I | re.MULTILINE
)


# ── PDF text extraction ────────────────────────────────────────────────────────
def extract_text(pdf_path: str) -> str:
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Use layout-aware extraction for better column handling
            text = page.extract_text(x_tolerance=3, y_tolerance=3)
            if text:
                pages.append(text)
    return "\n".join(pages)


def get_section(text: str, header_pattern: re.Pattern, max_chars: int = 600) -> str:
    """Extract text under a specific section header."""
    match = header_pattern.search(text)
    if not match:
        return ""
    return text[match.end(): match.end() + max_chars]


# ── Skills extraction ──────────────────────────────────────────────────────────
def extract_skills(text: str) -> list:
    lower = text.lower()

    # Boost skills found in the dedicated skills section
    skills_section = get_section(text, SECTION_HEADERS).lower()

    found = {}  # skill -> confidence score
    for skill in SKILLS_DB:
        escaped = re.escape(skill)
        # Use word boundary but allow for common separators after (e.g. "Python,")
        pattern = r"(?<![a-z])" + escaped + r"(?![a-z])"
        if re.search(pattern, lower):
            score = 1
            if skills_section and re.search(pattern, skills_section):
                score = 2  # higher confidence if in skills section
            found[skill] = score

    # Return sorted by confidence desc, then alpha
    sorted_skills = sorted(found.keys(), key=lambda s: (-found[s], s))
    return [s.title() for s in sorted_skills]


# ── Job title extraction ───────────────────────────────────────────────────────
def extract_job_titles(text: str) -> list:
    titles = set()

    # 1. Regex pattern matching
    for match in TITLE_PATTERN.finditer(text):
        title = " ".join(match.group(0).split()).strip()
        if len(title) > 5:
            titles.add(title.title())

    # 2. Standalone known titles
    for match in STANDALONE_TITLES.finditer(text):
        titles.add(match.group(0).title())

    # 3. spaCy: look for lines that follow ORG entities (job title usually near org)
    exp_section = get_section(text, EXPERIENCE_HEADERS, max_chars=1500)
    if exp_section:
        for line in exp_section.splitlines():
            line = line.strip()
            if 3 < len(line.split()) <= 6:
                for match in TITLE_PATTERN.finditer(line.lower()):
                    titles.add(line.title())

    # Deduplicate substrings (remove "Software Engineer" if "Senior Software Engineer" exists)
    final = list(titles)
    deduped = []
    for t in sorted(final, key=len, reverse=True):
        if not any(t.lower() in other.lower() for other in deduped):
            deduped.append(t)

    return sorted(deduped)


# ── Years of experience ────────────────────────────────────────────────────────
def calculate_experience(text: str) -> dict:
    lower = text.lower()
    date_ranges = []
    seen_pairs = set()

    for match in DATE_RANGE_PATTERN.finditer(lower):
        start_year = int(match.group(1))
        end_raw = match.group(2).lower()

        # Skip clearly wrong years
        if start_year < 1970 or start_year > 2030:
            continue

        end_year = 2025 if end_raw in ("present", "current", "now", "today") else int(end_raw)
        is_present = end_raw in ("present", "current", "now", "today")

        if end_year < start_year or end_year > 2030:
            continue

        pair = (start_year, end_year)
        if pair in seen_pairs:
            continue
        seen_pairs.add(pair)

        years = max(0, end_year - start_year)
        date_ranges.append({
            "from": start_year,
            "to": "Present" if is_present else end_year,
            "years": years
        })

    # Sort by start year descending (most recent first)
    date_ranges.sort(key=lambda x: x["from"], reverse=True)

    # Try to estimate non-overlapping total
    total_years = sum(r["years"] for r in date_ranges)

    # Cap unrealistic totals
    if total_years > 50:
        total_years = 0

    # Fallback: explicit "N years of experience" mentions
    if total_years == 0:
        for match in EXPLICIT_YEARS.finditer(text):
            total_years = max(total_years, int(match.group(1)))

    return {
        "total_years": total_years,
        "date_ranges": date_ranges[:6],
    }


# ── Contact info ───────────────────────────────────────────────────────────────
def extract_contact_info(text: str) -> dict:
    # Email
    email_match = re.search(r"[\w.+\-]+@[\w\-]+(?:\.[\w\-]+)+", text, re.I)

    # Phone — international aware, avoid matching years or zip codes
    phone_match = re.search(
        r"(?<!\d)(\+?(?:\d[\s\-.]?){9,14}\d)(?!\d)", text
    )

    # LinkedIn / GitHub
    linkedin_match = re.search(r"linkedin\.com/in/[\w\-]+", text, re.I)
    github_match = re.search(r"github\.com/[\w\-]+", text, re.I)

    # Website / portfolio
    website_match = re.search(
        r"(?:portfolio|website|web)[\s:]*([a-z0-9\-]+\.(?:com|dev|io|me|site)[/\w\-.]*)",
        text, re.I
    )

    # Name detection: use spaCy on first 600 chars, fallback to first short caps line
    header_text = text[:600]
    doc = nlp(header_text)
    name = ""
    for ent in doc.ents:
        if ent.label_ == "PERSON" and len(ent.text.split()) >= 2:
            name = ent.text.strip()
            break

    if not name:
        for line in text.splitlines()[:10]:
            line = line.strip()
            words = line.split()
            # Name: 2-4 words, each capitalized, no special chars
            if (2 <= len(words) <= 4
                    and all(w[0].isupper() for w in words if w)
                    and not re.search(r"[@|•|/|\\|@]", line)
                    and not any(kw in line.lower() for kw in
                                ["resume", "cv", "curriculum", "summary", "profile", "objective"])):
                name = line
                break

    return {
        "name": name,
        "email": email_match.group(0) if email_match else "",
        "phone": phone_match.group(1).strip() if phone_match else "",
        "linkedin": linkedin_match.group(0) if linkedin_match else "",
        "github": github_match.group(0) if github_match else "",
        "website": website_match.group(1) if website_match else "",
    }


# ── Education ──────────────────────────────────────────────────────────────────
def extract_education(text: str) -> list:
    found = []
    seen = set()

    for match in DEGREE_PATTERN.finditer(text):
        # Grab a generous window around the match
        start = max(0, match.start() - 10)
        end = min(len(text), match.end() + 120)
        snippet = text[start:end].replace("\n", " ").strip()

        # Clean up whitespace
        snippet = re.sub(r"\s{2,}", " ", snippet)[:140]

        # Deduplicate by degree keyword
        key = match.group(0).lower().replace(".", "").replace(" ", "")
        if key not in seen:
            seen.add(key)
            found.append(snippet)

    return found[:5]


# ── Summary stats ──────────────────────────────────────────────────────────────
def extract_summary(text: str) -> str:
    """Try to find a professional summary/objective section."""
    pattern = re.compile(
        r"(?:summary|objective|profile|about me|professional summary)[\s:]*\n(.*?)(?:\n[A-Z][A-Z\s]{3,}|\Z)",
        re.I | re.DOTALL
    )
    match = pattern.search(text)
    if match:
        summary = match.group(1).strip()
        summary = re.sub(r"\s+", " ", summary)
        return summary[:400]
    return ""


# ── Master extractor ───────────────────────────────────────────────────────────
def extract_resume_data(pdf_path: str) -> dict:
    text = extract_text(pdf_path)
    if not text.strip():
        raise ValueError(
            "Could not extract text from this PDF. "
            "It may be image-based (scanned). Try a text-based PDF."
        )

    contact = extract_contact_info(text)
    skills = extract_skills(text)
    job_titles = extract_job_titles(text)
    experience = calculate_experience(text)
    education = extract_education(text)
    summary = extract_summary(text)

    return {
        "contact": contact,
        "skills": skills,
        "job_titles": job_titles,
        "experience": experience,
        "education": education,
        "summary": summary,
        "word_count": len(text.split()),
    }