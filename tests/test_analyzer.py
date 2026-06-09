"""
tests/test_analyzer.py — Unit tests for SmartCV Analyzer.

Run with:
    pytest tests/ -v

Note: AI-dependent tests (analyze_single, analyze_multi) require GROQ_API_KEY.
      Mock tests run without API key.
"""

import sys
import os
import json
import pytest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.helpers import (
    score_to_color, score_to_label, score_to_grade,
    status_to_emoji, priority_to_icon, priority_to_label,
    truncate, sanitize_filename, get_best_match_index,
    format_keywords_as_tags, safe_get
)
from utils.prompts import build_single_analysis_prompt, build_multi_analysis_prompt
from utils.analyzer import _parse_json_response


# ══════════════════════════════════════════════════════════════════════════════
# helpers.py tests
# ══════════════════════════════════════════════════════════════════════════════

class TestScoreHelpers:
    def test_score_to_color_green(self):
        assert score_to_color(80) == "#10b981"
        assert score_to_color(70) == "#10b981"

    def test_score_to_color_amber(self):
        assert score_to_color(69) == "#f59e0b"
        assert score_to_color(50) == "#f59e0b"

    def test_score_to_color_red(self):
        assert score_to_color(49) == "#ef4444"
        assert score_to_color(0) == "#ef4444"

    def test_score_to_grade_boundaries(self):
        assert score_to_grade(90) == "A"
        assert score_to_grade(75) == "B"
        assert score_to_grade(60) == "C"
        assert score_to_grade(45) == "D"
        assert score_to_grade(30) == "E"

    def test_score_to_label_returns_string(self):
        for score in [0, 35, 50, 65, 80, 100]:
            result = score_to_label(score)
            assert isinstance(result, str)
            assert len(result) > 0


class TestStatusHelpers:
    def test_status_to_emoji(self):
        assert status_to_emoji("good") == "🟢"
        assert status_to_emoji("warn") == "🟡"
        assert status_to_emoji("bad") == "🔴"
        assert status_to_emoji("unknown") == "⚪"

    def test_priority_to_icon(self):
        assert priority_to_icon("high") == "🔴"
        assert priority_to_icon("medium") == "🟡"
        assert priority_to_icon("low") == "🟢"

    def test_priority_to_label(self):
        assert "Tinggi" in priority_to_label("high")
        assert "Sedang" in priority_to_label("medium")
        assert "Rendah" in priority_to_label("low")


class TestTextHelpers:
    def test_truncate_short_text(self):
        text = "Hello"
        assert truncate(text, 10) == "Hello"

    def test_truncate_long_text(self):
        text = "A" * 100
        result = truncate(text, 20)
        assert len(result) <= 23  # 20 + "..."
        assert result.endswith("...")

    def test_sanitize_filename_removes_special_chars(self):
        result = sanitize_filename("My CV (Final) v2!")
        assert "(" not in result
        assert ")" not in result
        assert "!" not in result

    def test_sanitize_filename_max_length(self):
        long_name = "A" * 100
        result = sanitize_filename(long_name)
        assert len(result) <= 50

    def test_format_keywords_as_tags(self):
        keywords = ["Python", "SQL", "Machine Learning"]
        result = format_keywords_as_tags(keywords)
        assert "`Python`" in result
        assert "`SQL`" in result

    def test_format_keywords_empty(self):
        result = format_keywords_as_tags([])
        assert result == "*Tidak ada*"


class TestResultHelpers:
    def test_get_best_match_index(self):
        results = [
            {"match_score": 60},
            {"match_score": 85},
            {"match_score": 45},
        ]
        assert get_best_match_index(results) == 1

    def test_get_best_match_index_empty(self):
        assert get_best_match_index([]) == 0

    def test_safe_get_nested(self):
        data = {"gap_analysis": {"Skills": {"score": 80}}}
        assert safe_get(data, "gap_analysis", "Skills", "score") == 80

    def test_safe_get_missing_key(self):
        data = {"match_score": 75}
        assert safe_get(data, "nonexistent", default="fallback") == "fallback"


# ══════════════════════════════════════════════════════════════════════════════
# prompts.py tests
# ══════════════════════════════════════════════════════════════════════════════

class TestPrompts:
    SAMPLE_CV = "John Doe\nData Scientist\nSkills: Python, SQL, TensorFlow\nExperience: 3 years at Google"
    SAMPLE_JD = "We need a Data Scientist with Python, SQL, and deep learning experience."

    def test_single_prompt_contains_cv(self):
        prompt = build_single_analysis_prompt(self.SAMPLE_CV, self.SAMPLE_JD)
        assert "Python" in prompt
        assert "Data Scientist" in prompt

    def test_single_prompt_contains_jd(self):
        prompt = build_single_analysis_prompt(self.SAMPLE_CV, self.SAMPLE_JD)
        assert "deep learning" in prompt

    def test_prompt_truncates_long_cv(self):
        long_cv = "X" * 10000
        prompt = build_single_analysis_prompt(long_cv, self.SAMPLE_JD)
        # Prompt should not be astronomically long
        assert len(prompt) < 8000

    def test_multi_prompt_includes_label(self):
        prompt = build_multi_analysis_prompt(self.SAMPLE_CV, self.SAMPLE_JD, "Senior Data Scientist")
        assert "Senior Data Scientist" in prompt


# ══════════════════════════════════════════════════════════════════════════════
# analyzer.py — JSON parsing tests (no API needed)
# ══════════════════════════════════════════════════════════════════════════════

class TestJsonParsing:
    VALID_RESULT = {
        "match_score": 75,
        "gap_analysis": {
            "Skills & Technical": {"score": 80, "status": "good", "note": "Skill kuat"}
        },
        "suggestions": [
            {"priority": "high", "title": "Tambah keyword", "detail": "Tambahkan lebih banyak keyword relevan."}
        ],
        "matched_keywords": ["Python", "SQL"],
        "missing_keywords": ["Docker"],
        "summary": "CV cukup cocok dengan JD ini."
    }

    def test_parse_clean_json(self):
        raw = json.dumps(self.VALID_RESULT)
        result = _parse_json_response(raw)
        assert result["match_score"] == 75
        assert result["matched_keywords"] == ["Python", "SQL"]

    def test_parse_json_with_markdown_fences(self):
        raw = "```json\n" + json.dumps(self.VALID_RESULT) + "\n```"
        result = _parse_json_response(raw)
        assert result["match_score"] == 75

    def test_parse_json_with_preamble(self):
        raw = "Here is the analysis:\n\n" + json.dumps(self.VALID_RESULT)
        result = _parse_json_response(raw)
        assert result["match_score"] == 75

    def test_parse_invalid_json_returns_fallback(self):
        raw = "this is not json at all"
        result = _parse_json_response(raw)
        assert "match_score" in result
        assert result["match_score"] == 0
        assert len(result["suggestions"]) > 0


# ══════════════════════════════════════════════════════════════════════════════
# Integration test (requires GROQ_API_KEY env var)
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.skipif(
    not os.environ.get("GROQ_API_KEY"),
    reason="GROQ_API_KEY not set — skipping live API test"
)
class TestAnalyzerIntegration:
    SAMPLE_CV = """
    John Doe — Data Scientist
    Education: S1 Computer Science, Universitas Indonesia
    Skills: Python, Pandas, Scikit-learn, SQL, Tableau
    Experience: 2 years as Data Analyst at Tokopedia
    Projects: Customer churn prediction, Sales forecasting
    """

    SAMPLE_JD = """
    We are looking for a Data Scientist with:
    - 2+ years experience in Python and machine learning
    - Experience with SQL and data visualization
    - Strong analytical and communication skills
    - Degree in Computer Science or related field
    """

    def test_analyze_single_returns_score(self):
        from utils.analyzer import analyze_single
        result = analyze_single(self.SAMPLE_CV, self.SAMPLE_JD)
        assert "match_score" in result
        assert 0 <= result["match_score"] <= 100

    def test_analyze_single_has_all_keys(self):
        from utils.analyzer import analyze_single
        result = analyze_single(self.SAMPLE_CV, self.SAMPLE_JD)
        for key in ["match_score", "gap_analysis", "suggestions", "matched_keywords", "missing_keywords"]:
            assert key in result, f"Missing key: {key}"

    def test_analyze_single_gap_sections(self):
        from utils.analyzer import analyze_single
        result = analyze_single(self.SAMPLE_CV, self.SAMPLE_JD)
        gap = result.get("gap_analysis", {})
        assert len(gap) >= 3, "Expected at least 3 gap sections"

    def test_analyze_multi_returns_list(self):
        from utils.analyzer import analyze_multi
        results = analyze_multi(
            self.SAMPLE_CV,
            [self.SAMPLE_JD, self.SAMPLE_JD],
            ["Posisi A", "Posisi B"]
        )
        assert len(results) == 2
        for r in results:
            assert "match_score" in r
