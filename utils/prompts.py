"""
prompts.py — Centralized prompt templates for SmartCV Analyzer.
Keeping prompts separate from logic makes them easy to iterate and improve.
"""

SYSTEM_PROMPT = """You are an expert HR consultant and ATS (Applicant Tracking System) specialist with 15+ years of experience reviewing resumes across tech, data, and business roles.

Your job is to analyze a CV against a job description and return ONLY valid JSON — no preamble, no markdown fences, no explanation outside the JSON.

Always return complete, valid JSON. Be specific, honest, and constructive in your analysis."""


def build_single_analysis_prompt(cv_text: str, jd_text: str) -> str:
    cv_trimmed = cv_text[:3000]
    jd_trimmed = jd_text[:1500]

    return f"""Analyze this CV against the Job Description carefully.

Return ONLY a JSON object with this exact schema (no extra keys, no markdown):

{{
  "match_score": <integer 0-100, honest assessment of overall fit>,
  "gap_analysis": {{
    "Skills & Technical": {{
      "score": <integer 0-100>,
      "status": "<good|warn|bad>",
      "note": "<specific 1-2 sentence analysis in Bahasa Indonesia>"
    }},
    "Work Experience": {{
      "score": <integer 0-100>,
      "status": "<good|warn|bad>",
      "note": "<specific 1-2 sentence analysis in Bahasa Indonesia>"
    }},
    "Education": {{
      "score": <integer 0-100>,
      "status": "<good|warn|bad>",
      "note": "<specific 1-2 sentence analysis in Bahasa Indonesia>"
    }},
    "Soft Skills & Leadership": {{
      "score": <integer 0-100>,
      "status": "<good|warn|bad>",
      "note": "<specific 1-2 sentence analysis in Bahasa Indonesia>"
    }},
    "Keyword Alignment": {{
      "score": <integer 0-100>,
      "status": "<good|warn|bad>",
      "note": "<specific 1-2 sentence analysis in Bahasa Indonesia>"
    }}
  }},
  "suggestions": [
    {{
      "priority": "<high|medium|low>",
      "title": "<short action-oriented title in Bahasa Indonesia>",
      "detail": "<specific, actionable improvement advice in Bahasa Indonesia, 2-4 sentences>"
    }}
  ],
  "matched_keywords": ["<keyword present in both CV and JD>"],
  "missing_keywords": ["<important JD keyword missing from CV>"],
  "summary": "<2-3 sentence overall assessment in Bahasa Indonesia>"
}}

Rules:
- match_score: be honest — do not inflate scores
- suggestions: 4–6 items, ordered high → medium → low priority
- matched_keywords: max 10, only keywords genuinely present in CV
- missing_keywords: max 10, most impactful missing keywords
- status "good" = score 70+, "warn" = 40–69, "bad" = below 40
- All text fields must be in Bahasa Indonesia
- Return ONLY the JSON object, nothing else

--- CV (truncated to 3000 chars) ---
{cv_trimmed}

--- JOB DESCRIPTION (truncated to 1500 chars) ---
{jd_trimmed}"""


def build_multi_analysis_prompt(cv_text: str, jd_text: str, job_label: str) -> str:
    """Slightly lighter prompt for multi-JD mode to reduce latency."""
    cv_trimmed = cv_text[:2500]
    jd_trimmed = jd_text[:1200]

    return f"""Analyze this CV against the job description for position: "{job_label}".

Return ONLY a JSON object:

{{
  "match_score": <integer 0-100>,
  "gap_analysis": {{
    "Skills & Technical": {{"score": <int>, "status": "<good|warn|bad>", "note": "<Bahasa Indonesia>"}},
    "Work Experience":    {{"score": <int>, "status": "<good|warn|bad>", "note": "<Bahasa Indonesia>"}},
    "Education":          {{"score": <int>, "status": "<good|warn|bad>", "note": "<Bahasa Indonesia>"}},
    "Soft Skills & Leadership": {{"score": <int>, "status": "<good|warn|bad>", "note": "<Bahasa Indonesia>"}},
    "Keyword Alignment":  {{"score": <int>, "status": "<good|warn|bad>", "note": "<Bahasa Indonesia>"}}
  }},
  "suggestions": [
    {{"priority": "<high|medium|low>", "title": "<Bahasa Indonesia>", "detail": "<Bahasa Indonesia>"}}
  ],
  "matched_keywords": ["<keyword>"],
  "missing_keywords": ["<keyword>"],
  "summary": "<2-3 sentence assessment in Bahasa Indonesia>"
}}

Rules: 3–5 suggestions, max 8 keywords each, all text in Bahasa Indonesia, return ONLY JSON.

--- CV ---
{cv_trimmed}

--- JOB DESCRIPTION: {job_label} ---
{jd_trimmed}"""


# ══════════════════════════════════════════════════════════════════════════════
# Career Advisor prompts
# ══════════════════════════════════════════════════════════════════════════════

CAREER_SYSTEM_PROMPT = """You are an expert career counselor and job market specialist with deep knowledge of the Indonesian and global job market.
Return ONLY valid JSON — no preamble, no markdown fences, no text outside the JSON."""


def build_career_advisor_prompt(cv_text: str) -> str:
    cv_trimmed = cv_text[:3000]
    return f"""Analyze this CV and provide comprehensive career advice. Return ONLY this JSON:

{{
  "profile_summary": "<2-3 sentence professional summary of this person in Bahasa Indonesia>",
  "current_level": "<Junior | Mid-level | Senior | Expert>",
  "recommended_roles": [
    {{
      "title": "<Job title in English>",
      "title_id": "<Job title in Bahasa Indonesia>",
      "match_pct": <integer 60-99>,
      "reason": "<why this role fits, 1-2 sentences in Bahasa Indonesia>",
      "avg_salary_idr": "<range, e.g. Rp 8-15 juta/bulan>",
      "demand": "<Tinggi | Sedang | Rendah>"
    }}
  ],
  "top_skills": ["<skill1>", "<skill2>"],
  "missing_skills": [
    {{
      "skill": "<skill name>",
      "importance": "<high|medium>",
      "how_to_learn": "<short suggestion in Bahasa Indonesia>"
    }}
  ],
  "career_paths": [
    {{
      "path_name": "<e.g. Data Science Track>",
      "steps": ["<step 1>", "<step 2>", "<step 3>"],
      "timeline": "<e.g. 1-2 tahun>"
    }}
  ],
  "action_plan": [
    {{
      "priority": "<high|medium|low>",
      "action": "<specific action in Bahasa Indonesia>",
      "timeframe": "<e.g. 1 minggu, 1 bulan>"
    }}
  ],
  "job_platforms": [
    {{
      "name": "<platform name>",
      "url": "<url>",
      "best_for": "<what type of jobs>"
    }}
  ]
}}

Rules:
- recommended_roles: 4-5 roles
- missing_skills: 4-5 skills  
- career_paths: 2 paths
- action_plan: 5-6 items ordered by priority
- job_platforms: 4-5 platforms relevant for Indonesia
- All descriptive text in Bahasa Indonesia
- Return ONLY JSON

--- CV ---
{cv_trimmed}"""


# ══════════════════════════════════════════════════════════════════════════════
# HRD Screener prompt
# ══════════════════════════════════════════════════════════════════════════════

HRD_SYSTEM_PROMPT = """You are an expert ATS (Applicant Tracking System) and HR specialist.
Analyze ONE candidate's CV against a job description and return ONLY valid JSON — no preamble, no markdown."""


def build_hrd_screen_prompt(cv_text: str, jd_text: str, candidate_name: str) -> str:
    cv_trimmed = cv_text[:2500]
    jd_trimmed = jd_text[:1200]
    return f"""Screen this candidate CV against the job description.

Return ONLY this JSON:
{{
  "candidate_name": "{candidate_name}",
  "match_score": <integer 0-100>,
  "recommendation": "<LOLOS | PERTIMBANGKAN | DITOLAK>",
  "recommendation_reason": "<1-2 sentence reason in Bahasa Indonesia>",
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "weaknesses": ["<weakness 1>", "<weakness 2>"],
  "matched_keywords": ["<kw1>", "<kw2>"],
  "missing_keywords": ["<kw1>", "<kw2>"],
  "experience_years": <estimated years as integer>,
  "education_fit": "<Sangat Sesuai | Sesuai | Kurang Sesuai>",
  "interview_questions": ["<pertanyaan interview 1>", "<pertanyaan interview 2>", "<pertanyaan interview 3>"]
}}

Rules: all text in Bahasa Indonesia, return ONLY JSON.

--- CV: {candidate_name} ---
{cv_trimmed}

--- JOB DESCRIPTION ---
{jd_trimmed}"""
