"""
helpers.py — Shared utility functions for UI rendering and data formatting.
"""

from datetime import datetime


# ── Score Helpers ────────────────────────────────────────────────────────────

def score_to_color(score: int) -> str:
    """Return hex color based on score threshold."""
    if score >= 70:
        return "#10b981"   # green
    elif score >= 50:
        return "#f59e0b"   # amber
    return "#ef4444"       # red


def score_to_label(score: int) -> str:
    """Return human-readable label for a match score."""
    if score >= 80:
        return "Sangat Cocok 🎉"
    elif score >= 65:
        return "Cocok 👍"
    elif score >= 50:
        return "Cukup Cocok 🙂"
    elif score >= 35:
        return "Kurang Cocok 😐"
    return "Tidak Cocok 💪 — Perlu Banyak Peningkatan"


def score_to_grade(score: int) -> str:
    """Return letter grade for a match score."""
    if score >= 85: return "A"
    if score >= 70: return "B"
    if score >= 55: return "C"
    if score >= 40: return "D"
    return "E"


# ── Status Helpers ───────────────────────────────────────────────────────────

def status_to_badge_html(status: str) -> str:
    """Return HTML badge string for a gap status."""
    mapping = {
        "good": ('<span class="badge-good">✓ Kuat</span>', "badge-good"),
        "warn": ('<span class="badge-warn">⚠ Perlu Ditingkatkan</span>', "badge-warn"),
        "bad":  ('<span class="badge-bad">✗ Lemah</span>', "badge-bad"),
    }
    return mapping.get(status, mapping["warn"])[0]


def status_to_emoji(status: str) -> str:
    return {"good": "🟢", "warn": "🟡", "bad": "🔴"}.get(status, "⚪")


def priority_to_icon(priority: str) -> str:
    return {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority, "⚪")


def priority_to_label(priority: str) -> str:
    return {"high": "Prioritas Tinggi", "medium": "Prioritas Sedang", "low": "Prioritas Rendah"}.get(priority, priority)


# ── Text Helpers ─────────────────────────────────────────────────────────────

def truncate(text: str, max_chars: int = 80) -> str:
    """Truncate text and add ellipsis if needed."""
    return text if len(text) <= max_chars else text[:max_chars].rstrip() + "..."


def sanitize_filename(name: str) -> str:
    """Make a string safe for use as filename."""
    import re
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"\s+", "_", name.strip())
    return name[:50]


def now_str() -> str:
    """Return formatted current datetime string."""
    return datetime.now().strftime("%d %B %Y, %H:%M")


def format_keywords_as_tags(keywords: list) -> str:
    """Format a list of keywords as inline code tags (Markdown)."""
    return "  ".join(f"`{kw}`" for kw in keywords) if keywords else "*Tidak ada*"


# ── Result Helpers ───────────────────────────────────────────────────────────

def get_best_match_index(results: list) -> int:
    """Return index of the result with the highest match_score."""
    if not results:
        return 0
    return max(range(len(results)), key=lambda i: results[i].get("match_score", 0))


def safe_get(result: dict, *keys, default=None):
    """Safely traverse nested dict."""
    val = result
    for key in keys:
        if not isinstance(val, dict):
            return default
        val = val.get(key, default)
    return val
