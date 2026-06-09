"""
analyzer.py — Core AI analysis logic using Groq API.
"""

import os
import json
import re
from groq import Groq
from utils.prompts import SYSTEM_PROMPT, build_single_analysis_prompt, build_multi_analysis_prompt

MODEL = "llama-3.3-70b-versatile"


def _get_client() -> Groq:
    """Lazy-load Groq client so Streamlit secrets are already available."""
    try:
        import streamlit as st
        api_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        api_key = ""

    if not api_key:
        api_key = os.environ.get("GROQ_API_KEY", "")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY tidak ditemukan!\n\n"
            "Pastikan file .streamlit/secrets.toml berisi:\n"
            'GROQ_API_KEY = "gsk_xxx..."\n\n'
            "Dapatkan API key gratis di https://console.groq.com"
        )

    return Groq(api_key=api_key)


def _parse_json_response(raw: str) -> dict:
    """Safely extract and parse JSON from LLM response."""
    raw = re.sub(r"```json\s*", "", raw)
    raw = re.sub(r"```\s*", "", raw)
    raw = raw.strip()

    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start != -1 and end > start:
        raw = raw[start:end]

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        return {
            "match_score": 0,
            "gap_analysis": {},
            "suggestions": [{
                "priority": "high",
                "title": "Error parsing AI response",
                "detail": f"Gagal memproses respons AI: {str(e)}. Coba lagi."
            }],
            "matched_keywords": [],
            "missing_keywords": [],
            "summary": "Terjadi error saat memproses analisis."
        }


def analyze_single(cv_text: str, jd_text: str) -> dict:
    """Analyze one CV against one Job Description."""
    client = _get_client()
    prompt = build_single_analysis_prompt(cv_text, jd_text)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000,
        temperature=0.2,
    )

    raw = response.choices[0].message.content
    return _parse_json_response(raw)


def analyze_multi(cv_text: str, jd_list: list, labels: list) -> list:
    """Analyze one CV against multiple Job Descriptions."""
    client = _get_client()
    results = []
    for jd, label in zip(jd_list, labels):
        prompt = build_multi_analysis_prompt(cv_text, jd, label)
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.2,
        )
        raw = response.choices[0].message.content
        result = _parse_json_response(raw)
        result["label"] = label
        results.append(result)
    return results


def analyze_career(cv_text: str) -> dict:
    """Generate career advice based on CV."""
    from utils.prompts import CAREER_SYSTEM_PROMPT, build_career_advisor_prompt
    client = _get_client()
    prompt = build_career_advisor_prompt(cv_text)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": CAREER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2500,
        temperature=0.3,
    )
    raw = response.choices[0].message.content
    return _parse_json_response(raw)


def screen_candidate(cv_text: str, jd_text: str, candidate_name: str) -> dict:
    """Screen one candidate CV against a JD for HRD mode."""
    from utils.prompts import HRD_SYSTEM_PROMPT, build_hrd_screen_prompt
    client = _get_client()
    prompt = build_hrd_screen_prompt(cv_text, jd_text, candidate_name)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": HRD_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1200,
        temperature=0.2,
    )
    raw = response.choices[0].message.content
    result = _parse_json_response(raw)
    result["candidate_name"] = candidate_name
    return result


def screen_batch(cv_files_data: list, jd_text: str) -> list:
    """Screen multiple candidates. cv_files_data = list of (name, text)."""
    results = []
    for name, cv_text in cv_files_data:
        result = screen_candidate(cv_text, jd_text, name)
        results.append(result)
    # Sort by match_score descending
    results.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    return results
