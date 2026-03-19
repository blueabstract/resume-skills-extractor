"""
ATS Job Match Scorer
────────────────────
Uses TF-IDF vectorization + cosine similarity to score how well
a resume matches a job description. Pure scikit-learn ML.
"""

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ── Stop words to ignore (domain-specific additions) ──────────────────────────
EXTRA_STOP_WORDS = {
    "experience", "work", "working", "worked", "years", "year",
    "strong", "good", "excellent", "knowledge", "understanding",
    "ability", "responsibilities", "responsible", "including",
    "required", "requirements", "preferred", "plus", "bonus",
    "team", "teams", "company", "role", "position", "candidate",
    "looking", "seeking", "join", "help", "hands", "proven",
}

# Skill categories for breakdown analysis
SKILL_CATEGORIES = {
    "Languages": [
        "python", "javascript", "typescript", "java", "c++", "c#", "go",
        "rust", "kotlin", "swift", "ruby", "php", "scala", "r", "matlab",
        "bash", "sql", "dart", "perl", "elixir",
    ],
    "Frontend": [
        "react", "vue", "angular", "next.js", "svelte", "html", "css",
        "tailwind", "bootstrap", "redux", "webpack", "vite", "jquery",
    ],
    "Backend": [
        "flask", "django", "fastapi", "express", "spring boot", "rails",
        "node.js", "graphql", "rest api", "laravel", "nestjs", "asp.net",
    ],
    "Data / ML": [
        "machine learning", "deep learning", "nlp", "pytorch", "tensorflow",
        "keras", "scikit-learn", "pandas", "numpy", "spark", "airflow",
        "mlflow", "hugging face", "langchain", "computer vision", "llm",
        "data analysis", "transformers",
    ],
    "Cloud / DevOps": [
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ci/cd",
        "jenkins", "github actions", "linux", "ansible", "serverless",
    ],
    "Databases": [
        "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "sqlite",
        "dynamodb", "cassandra", "firebase", "oracle", "neo4j",
    ],
    "Tools": [
        "git", "github", "jira", "figma", "postman", "tableau", "power bi",
        "agile", "scrum", "docker", "linux",
    ],
}


def clean_text(text: str) -> str:
    """Normalize text for TF-IDF."""
    text = text.lower()
    # Keep alphanumeric, spaces, dots (for next.js, c++, etc.), slashes
    text = re.sub(r"[^\w\s./#+]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_keywords(text: str) -> set:
    """Extract meaningful single and bigram keywords from text."""
    text_lower = text.lower()
    keywords = set()

    # Check all skills across categories
    for skills in SKILL_CATEGORIES.values():
        for skill in skills:
            pattern = r"(?<![a-z])" + re.escape(skill) + r"(?![a-z])"
            if re.search(pattern, text_lower):
                keywords.add(skill)

    return keywords


def compute_ats_score(resume_text: str, job_description: str) -> dict:
    """
    Core ML function: TF-IDF cosine similarity between resume and JD.

    Returns a detailed breakdown including:
    - overall score (0-100)
    - matched skills
    - missing skills
    - category-level scores
    - keyword analysis
    """
    if not resume_text.strip() or not job_description.strip():
        raise ValueError("Both resume text and job description are required.")

    # ── 1. TF-IDF Vectorization ────────────────────────────────────────────────
    # This is the core ML step: convert text to TF-IDF feature vectors
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 3),        # unigrams, bigrams, trigrams
        stop_words="english",      # remove common English stop words
        min_df=1,
        max_features=10000,        # vocabulary cap
        sublinear_tf=True,         # log normalization for term frequency
    )

    try:
        tfidf_matrix = vectorizer.fit_transform([
            clean_text(resume_text),
            clean_text(job_description),
        ])
    except ValueError:
        return _empty_result()

    # ── 2. Cosine Similarity ───────────────────────────────────────────────────
    # Measures the angle between the two TF-IDF vectors (0 = no match, 1 = identical)
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

    # Scale to 0-100 and apply a calibration curve so scores feel realistic
    # Raw cosine on resume/JD pairs tends to cluster in 0.1-0.4, so we scale up
    raw_score = float(similarity)
    calibrated_score = min(100, round(raw_score * 180))  # calibrated scale

    # ── 3. Keyword extraction ──────────────────────────────────────────────────
    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(job_description)

    matched_skills = sorted(resume_keywords & jd_keywords)
    missing_skills = sorted(jd_keywords - resume_keywords)
    bonus_skills = sorted(resume_keywords - jd_keywords)  # skills not in JD but still good

    # Keyword match ratio — secondary ML signal
    keyword_ratio = 0.0
    if jd_keywords:
        keyword_ratio = len(matched_skills) / len(jd_keywords)

    # ── 4. Blend scores ────────────────────────────────────────────────────────
    # Final score = 60% TF-IDF cosine + 40% keyword match ratio
    # This gives a more balanced and realistic result
    final_score = round((calibrated_score * 0.6) + (keyword_ratio * 100 * 0.4))
    final_score = max(0, min(100, final_score))

    # ── 5. Category breakdown ──────────────────────────────────────────────────
    category_scores = {}
    for category, skills in SKILL_CATEGORIES.items():
        jd_cat = {s for s in skills if s in jd_keywords}
        resume_cat = {s for s in skills if s in resume_keywords}
        if jd_cat:
            score = round((len(resume_cat & jd_cat) / len(jd_cat)) * 100)
            category_scores[category] = {
                "score": score,
                "matched": sorted(resume_cat & jd_cat),
                "missing": sorted(jd_cat - resume_cat),
            }

    # ── 6. Verdict ────────────────────────────────────────────────────────────
    if final_score >= 80:
        verdict = "Excellent match"
        verdict_color = "green"
    elif final_score >= 60:
        verdict = "Good match"
        verdict_color = "blue"
    elif final_score >= 40:
        verdict = "Partial match"
        verdict_color = "amber"
    else:
        verdict = "Low match"
        verdict_color = "red"

    return {
        "score": final_score,
        "verdict": verdict,
        "verdict_color": verdict_color,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "bonus_skills": bonus_skills[:10],
        "category_scores": category_scores,
        "keyword_match_pct": round(keyword_ratio * 100),
        "tfidf_similarity": round(raw_score * 100, 1),
        "total_jd_keywords": len(jd_keywords),
        "total_resume_keywords": len(resume_keywords),
    }


def _empty_result() -> dict:
    return {
        "score": 0, "verdict": "Could not analyze", "verdict_color": "red",
        "matched_skills": [], "missing_skills": [], "bonus_skills": [],
        "category_scores": {}, "keyword_match_pct": 0,
        "tfidf_similarity": 0, "total_jd_keywords": 0,
        "total_resume_keywords": 0,
    }