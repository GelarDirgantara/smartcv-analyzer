import streamlit as st
import base64
import pandas as pd
from utils.pdf_reader import extract_text_from_pdf
from utils.analyzer import analyze_single, analyze_multi, analyze_career, screen_batch
from utils.exporter import export_to_pdf
from utils.helpers import (
    score_to_color, score_to_label, score_to_grade,
    status_to_badge_html, priority_to_icon,
    get_best_match_index, truncate
)

st.set_page_config(
    page_title="SmartCV Analyzer — by Dirga",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def load_css(path):
    with open(path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("assets/styles.css")

def img_to_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_b64 = img_to_b64("assets/logo.png")

# ── Hero — logo kanan, konten kiri ───────────────────────────────────────────
st.markdown(f"""
<div class="hero-section">
    <div style="display:grid;grid-template-columns:1fr auto;align-items:center;gap:2rem">
        <div>
            <div class="hero-title">Smart<span>CV</span> Analyzer</div>
            <div class="hero-subtitle">
                Platform AI lengkap untuk pencari kerja &amp; HRD.<br>
                Analisis CV, screening kandidat, saran karir — semua dalam satu tempat.
            </div>
            <div class="hero-stats">
                <div class="hero-stat"><div class="hero-stat-number">4</div><div class="hero-stat-label">Mode Analisis</div></div>
                <div class="hero-stat"><div class="hero-stat-number">AI</div><div class="hero-stat-label">Powered LLaMA 3.3</div></div>
                <div class="hero-stat"><div class="hero-stat-number">∞</div><div class="hero-stat-label">CV Screening</div></div>
                <div class="hero-stat"><div class="hero-stat-number">PDF</div><div class="hero-stat-label">Export Report</div></div>
            </div>
            <div style="display:flex;gap:.6rem;margin-top:1.2rem;flex-wrap:wrap">
                <span style="background:rgba(255,255,255,.12);color:#c7d2fe;padding:4px 14px;border-radius:20px;font-size:.78rem;border:1px solid rgba(255,255,255,.15)">👤 Untuk Pencari Kerja</span>
                <span style="background:rgba(255,255,255,.12);color:#c7d2fe;padding:4px 14px;border-radius:20px;font-size:.78rem;border:1px solid rgba(255,255,255,.15)">🏢 Untuk HRD / Recruiter</span>
                <span style="background:rgba(99,102,241,.4);color:#e0e7ff;padding:4px 14px;border-radius:20px;font-size:.78rem;border:1px solid rgba(165,180,252,.3)">⚡ Groq Ultra-Fast AI</span>
            </div>
        </div>
        <div style="display:flex;align-items:center;justify-content:flex-end;padding-right:.5rem">
            <img src="data:image/png;base64,{logo_b64}"
                 style="height:210px;width:auto;object-fit:contain;
                        filter:drop-shadow(0 8px 32px rgba(99,102,241,0.7));">
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── How It Works ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="how-it-works">
    <div class="step-card"><div class="step-number">01</div><div class="step-title">📄 CV vs JD</div><div class="step-desc">Analisis kecocokan CV dengan satu lowongan. Dapat skor, gap, dan saran perbaikan spesifik.</div></div>
    <div class="step-card"><div class="step-number">02</div><div class="step-title">📋 Multi JD</div><div class="step-desc">Bandingkan 1 CV dengan 3 posisi berbeda sekaligus. Temukan yang paling cocok.</div></div>
    <div class="step-card"><div class="step-number">03</div><div class="step-title">🧭 Career Advisor</div><div class="step-desc">Rekomendasi karir, estimasi gaji, skill gap, dan jalur pengembangan diri.</div></div>
    <div class="step-card"><div class="step-number">04</div><div class="step-title">🏢 HRD Screener</div><div class="step-desc">Upload banyak CV sekaligus, AI ranking otomatis kandidat terbaik sesuai JD.</div></div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# RENDER FUNCTIONS
# ═══════════════════════════════════════════════════════

def render_single_result(result: dict):
    score = result.get("match_score", 0)
    color = score_to_color(score)
    label = score_to_label(score)
    grade = score_to_grade(score)
    st.markdown(f"""
    <div class="score-card" style="background:linear-gradient(135deg,{color}22,{color}44);border:1px solid {color}55">
        <div style="font-size:.8rem;text-transform:uppercase;letter-spacing:2px;color:{color};font-weight:600;margin-bottom:.5rem">MATCH SCORE</div>
        <div class="score-number" style="color:#1e1b4b">{score}<span style="font-size:2.5rem;color:{color}">%</span></div>
        <div style="font-size:1rem;color:#64748b;margin-top:.5rem">{label} &nbsp;·&nbsp; Grade <span style="color:{color};font-weight:700">{grade}</span></div>
    </div>""", unsafe_allow_html=True)
    st.progress(score / 100)
    if result.get("summary"):
        st.info(f"💬 **Ringkasan AI:** {result['summary']}")
    st.markdown("#### 📊 Gap Analysis per Section")
    for section, data in result.get("gap_analysis", {}).items():
        with st.expander(f"{section}  —  {data.get('score',0)}/100"):
            st.markdown(status_to_badge_html(data.get("status","warn")), unsafe_allow_html=True)
            st.markdown(f"**Catatan:** {data.get('note','-')}")
    st.markdown("#### 💡 Saran Perbaikan")
    for i, sug in enumerate(result.get("suggestions", []), 1):
        with st.expander(f"{priority_to_icon(sug.get('priority','medium'))} #{i} — {sug.get('title','')}"):
            st.markdown(sug.get("detail",""))
    st.markdown("#### 🏷️ Keyword Match")
    kw1, kw2 = st.columns(2)
    with kw1:
        st.markdown("**✅ Ada di CV:**")
        matched = result.get("matched_keywords", [])
        st.markdown(" ".join(f'<span class="kw-match">{k}</span>' for k in matched) if matched else "*Tidak ada*", unsafe_allow_html=True)
    with kw2:
        st.markdown("**❌ Hilang:**")
        missing = result.get("missing_keywords", [])
        st.markdown(" ".join(f'<span class="kw-missing">{k}</span>' for k in missing) if missing else "*Semua sudah ada 🎉*", unsafe_allow_html=True)


def render_multi_result(results, labels):
    st.divider()
    st.markdown("### 📊 Hasil Perbandingan")
    best_idx = get_best_match_index(results)
    cols = st.columns(len(results))
    for i, (col, result, label) in enumerate(zip(cols, results, labels)):
        score = result.get("match_score", 0)
        color = score_to_color(score)
        is_best = i == best_idx
        with col:
            st.markdown(f"""<div class="compare-card" style="border:{'2px solid '+color if is_best else '1px solid #e0e7ff'};background:{'#f5f3ff' if is_best else '#fff'}">
                {"<div style='font-size:.72rem;font-weight:700;color:"+color+";margin-bottom:4px;text-transform:uppercase'>⭐ REKOMENDASI</div>" if is_best else ""}
                <div style="font-size:.85rem;font-weight:600;color:#1e1b4b;margin-bottom:6px">{label}</div>
                <div style="font-family:'Syne',sans-serif;font-size:3rem;font-weight:800;color:{color};line-height:1">{score}%</div>
                <div style="font-size:.72rem;color:#94a3b8;margin-top:4px;text-transform:uppercase;letter-spacing:.5px">match score</div>
            </div>""", unsafe_allow_html=True)
    for result, label in zip(results, labels):
        with st.expander(f"📋 Detail — {label} ({result.get('match_score',0)}%)"):
            render_single_result(result)


def render_career_result(result: dict):
    level = result.get("current_level", "")
    level_color = {"Junior":"#f59e0b","Mid-level":"#6366f1","Senior":"#10b981","Expert":"#06b6d4"}.get(level,"#6366f1")
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#f5f3ff,#ede9fe);border:1px solid #c4b5fd;border-radius:16px;padding:1.5rem 2rem;margin-bottom:1.5rem">
        <div style="display:flex;align-items:center;gap:1rem;margin-bottom:.8rem">
            <span style="background:{level_color};color:white;padding:4px 16px;border-radius:20px;font-size:.8rem;font-weight:700;text-transform:uppercase">{level}</span>
            <span style="color:#6366f1;font-size:.85rem;font-weight:600">Profil Profesional</span>
        </div>
        <p style="color:#1e1b4b;font-size:.95rem;line-height:1.7;margin:0">{result.get('profile_summary','')}</p>
    </div>""", unsafe_allow_html=True)
    top_skills = result.get("top_skills", [])
    if top_skills:
        st.markdown("**🏆 Top Skills:**")
        st.markdown(" ".join(f'<span class="kw-match">✓ {s}</span>' for s in top_skills), unsafe_allow_html=True)
        st.markdown("")
    st.markdown("#### 💼 Rekomendasi Posisi")
    roles = result.get("recommended_roles", [])
    cols = st.columns(min(len(roles), 3))
    for i, role in enumerate(roles):
        color = score_to_color(role.get("match_pct", 0))
        demand = role.get("demand", "Sedang")
        dc = {"Tinggi":"#10b981","Sedang":"#f59e0b","Rendah":"#ef4444"}.get(demand,"#f59e0b")
        with cols[i % 3]:
            st.markdown(f"""<div class="compare-card" style="border:1px solid #e0e7ff;text-align:left;padding:1.2rem">
                <div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;color:#1e1b4b">{role.get('title','')}</div>
                <div style="font-size:.8rem;color:#6366f1;margin-bottom:.8rem">{role.get('title_id','')}</div>
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:.6rem">
                    <span style="font-size:1.4rem;font-weight:800;color:{color}">{role.get('match_pct',0)}%</span>
                    <span style="background:{dc}22;color:{dc};border:1px solid {dc}44;padding:2px 10px;border-radius:12px;font-size:.75rem;font-weight:600">Demand: {demand}</span>
                </div>
                <div style="font-size:.78rem;color:#64748b;line-height:1.5;margin-bottom:.5rem">{role.get('reason','')}</div>
                <div style="font-size:.8rem;color:#10b981;font-weight:500">💰 {role.get('avg_salary_idr','')}</div>
            </div>""", unsafe_allow_html=True)
    st.markdown("#### 🛤️ Jalur Karir")
    paths = result.get("career_paths", [])
    if paths:
        path_cols = st.columns(len(paths))
        for col, path in zip(path_cols, paths):
            with col:
                st.markdown(f"**{path.get('path_name','')}** · *{path.get('timeline','')}*")
                for j, step in enumerate(path.get("steps", []), 1):
                    st.markdown(f"`{j}` {step}")
    st.markdown("#### 📚 Skill yang Perlu Dikembangkan")
    for sd in result.get("missing_skills", []):
        icon = "🔴" if sd.get("importance") == "high" else "🟡"
        with st.expander(f"{icon} **{sd.get('skill','')}**"):
            st.markdown(f"💡 {sd.get('how_to_learn','')}")
    st.markdown("#### 🎯 Action Plan")
    for i, action in enumerate(result.get("action_plan", []), 1):
        st.markdown(f"{priority_to_icon(action.get('priority','medium'))} **#{i}** `{action.get('timeframe','')}` — {action.get('action','')}")
    st.markdown("#### 🌐 Platform Cari Kerja")
    platforms = result.get("job_platforms", [])
    p_cols = st.columns(min(len(platforms), 4))
    for col, p in zip(p_cols, platforms):
        with col:
            st.markdown(f"""<a href="{p.get('url','#')}" target="_blank" style="text-decoration:none">
            <div style="background:#fff;border:1px solid #e0e7ff;border-radius:12px;padding:1rem;text-align:center">
                <div style="font-weight:700;color:#1e1b4b;font-size:.9rem">{p.get('name','')}</div>
                <div style="font-size:.75rem;color:#6366f1;margin-top:4px">{p.get('best_for','')}</div>
            </div></a>""", unsafe_allow_html=True)


def render_hrd_results(results: list):
    st.divider()
    st.markdown(f"### 📊 Hasil Screening — {len(results)} Kandidat")

    # Summary stats
    lolos = sum(1 for r in results if r.get("recommendation") == "LOLOS")
    pertimbang = sum(1 for r in results if r.get("recommendation") == "PERTIMBANGKAN")
    ditolak = sum(1 for r in results if r.get("recommendation") == "DITOLAK")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div style="background:#d1fae5;border:1px solid #a7f3d0;border-radius:12px;padding:1rem;text-align:center">
            <div style="font-size:2rem;font-weight:800;color:#065f46">{lolos}</div>
            <div style="font-size:.8rem;color:#065f46;font-weight:600;text-transform:uppercase;letter-spacing:.5px">✅ Lolos</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div style="background:#fef3c7;border:1px solid #fde68a;border-radius:12px;padding:1rem;text-align:center">
            <div style="font-size:2rem;font-weight:800;color:#92400e">{pertimbang}</div>
            <div style="font-size:.8rem;color:#92400e;font-weight:600;text-transform:uppercase;letter-spacing:.5px">🤔 Pertimbangkan</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div style="background:#fee2e2;border:1px solid #fecaca;border-radius:12px;padding:1rem;text-align:center">
            <div style="font-size:2rem;font-weight:800;color:#991b1b">{ditolak}</div>
            <div style="font-size:.8rem;color:#991b1b;font-weight:600;text-transform:uppercase;letter-spacing:.5px">❌ Ditolak</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        avg = round(sum(r.get("match_score",0) for r in results) / len(results)) if results else 0
        st.markdown(f"""<div style="background:#ede9fe;border:1px solid #c4b5fd;border-radius:12px;padding:1rem;text-align:center">
            <div style="font-size:2rem;font-weight:800;color:#4338ca">{avg}%</div>
            <div style="font-size:.8rem;color:#4338ca;font-weight:600;text-transform:uppercase;letter-spacing:.5px">📊 Avg Score</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Ranking table
    st.markdown("#### 🏆 Ranking Kandidat")
    table_data = []
    for i, r in enumerate(results, 1):
        rec = r.get("recommendation", "")
        rec_badge = {"LOLOS": "✅ LOLOS", "PERTIMBANGKAN": "🤔 PERTIMBANGKAN", "DITOLAK": "❌ DITOLAK"}.get(rec, rec)
        table_data.append({
            "Rank": f"#{i}",
            "Nama Kandidat": r.get("candidate_name", "-"),
            "Score": f"{r.get('match_score', 0)}%",
            "Rekomendasi": rec_badge,
            "Pengalaman": f"{r.get('experience_years', '?')} thn",
            "Pendidikan": r.get("education_fit", "-"),
        })
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Export CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Export Ranking ke CSV", data=csv,
                       file_name="screening_results.csv", mime="text/csv")

    st.markdown("<br>", unsafe_allow_html=True)

    # Detail per kandidat
    st.markdown("#### 📋 Detail per Kandidat")
    for i, r in enumerate(results, 1):
        score = r.get("match_score", 0)
        color = score_to_color(score)
        rec = r.get("recommendation", "")
        rec_color = {"LOLOS":"#10b981","PERTIMBANGKAN":"#f59e0b","DITOLAK":"#ef4444"}.get(rec,"#6366f1")
        name = r.get("candidate_name", f"Kandidat {i}")

        with st.expander(f"#{i} · {name} — {score}% · {rec}"):
            col_a, col_b = st.columns([1, 1])
            with col_a:
                st.markdown(f"""<div style="background:{color}15;border:1px solid {color}44;border-radius:12px;padding:1rem;text-align:center;margin-bottom:1rem">
                    <div style="font-size:2.5rem;font-weight:800;color:{color}">{score}%</div>
                    <div style="font-size:.85rem;color:{rec_color};font-weight:700">{rec}</div>
                    <div style="font-size:.8rem;color:#64748b;margin-top:.4rem">{r.get('recommendation_reason','')}</div>
                </div>""", unsafe_allow_html=True)
                st.markdown("**✅ Kekuatan:**")
                for s in r.get("strengths", []):
                    st.markdown(f"- {s}")
                st.markdown("**⚠️ Kelemahan:**")
                for w in r.get("weaknesses", []):
                    st.markdown(f"- {w}")
            with col_b:
                st.markdown("**🏷️ Keyword Match:**")
                matched = r.get("matched_keywords", [])
                st.markdown(" ".join(f'<span class="kw-match">{k}</span>' for k in matched) if matched else "*-*", unsafe_allow_html=True)
                st.markdown("**❌ Keyword Hilang:**")
                missing = r.get("missing_keywords", [])
                st.markdown(" ".join(f'<span class="kw-missing">{k}</span>' for k in missing) if missing else "*-*", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("**❓ Pertanyaan Interview yang Disarankan:**")
                for q in r.get("interview_questions", []):
                    st.markdown(f"- {q}")


# ═══════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "📄  CV vs Job Description",
    "📋  Multi JD Comparison",
    "🧭  Career Advisor",
    "🏢  HRD Screener"
])

# ── TAB 1 ─────────────────────────────────────────────
with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns([1,1], gap="large")
    with col_left:
        st.markdown("#### 📎 Upload CV")
        cv_file = st.file_uploader("PDF", type=["pdf"], key="cv_single", label_visibility="collapsed")
        if cv_file: st.success(f"✅ **{cv_file.name}** berhasil diupload")
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📝 Job Description")
        st.markdown("<small style='color:#6366f1'>Copy-paste dari LinkedIn, Jobstreet, atau website perusahaan</small>", unsafe_allow_html=True)
        jd_text = st.text_area("JD", height=280,
            placeholder="We are looking for a Data Scientist with 3+ years experience in Python, SQL, machine learning...",
            key="jd_single", label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀  Analisis Sekarang", type="primary", use_container_width=True, key="btn_single"):
            if not cv_file: st.error("❌ Upload CV dulu!")
            elif not jd_text.strip(): st.error("❌ Job description tidak boleh kosong!")
            else:
                with st.spinner("🤖 AI sedang menganalisis..."):
                    cv_text = extract_text_from_pdf(cv_file)
                    if cv_text:
                        st.session_state["single_result"] = analyze_single(cv_text, jd_text)
                        st.session_state["jd_preview"] = truncate(jd_text, 80)
                    else: st.error("❌ Gagal membaca PDF.")
    with col_right:
        if "single_result" in st.session_state:
            render_single_result(st.session_state["single_result"])
            st.divider()
            if st.button("📥  Export ke PDF", use_container_width=True, key="export_single"):
                with st.spinner("Membuat laporan..."):
                    pdf_bytes = export_to_pdf(st.session_state["single_result"], st.session_state.get("jd_preview",""))
                    st.download_button("⬇️  Download PDF", data=pdf_bytes, file_name="smartcv_report.pdf", mime="application/pdf", use_container_width=True)
        else:
            st.markdown("""<div class="empty-state"><div style="font-size:3rem">🎯</div>
                <div style="color:#6366f1;font-size:.95rem;text-align:center;line-height:1.7;font-weight:500">
                Upload CV dan paste job description<br>
                <span style="color:#94a3b8;font-weight:400;font-size:.85rem">lalu klik Analisis Sekarang</span>
                </div></div>""", unsafe_allow_html=True)

# ── TAB 2 ─────────────────────────────────────────────
with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📎 Upload CV")
    cv_file_multi = st.file_uploader("PDF", type=["pdf"], key="cv_multi", label_visibility="collapsed")
    if cv_file_multi: st.success(f"✅ **{cv_file_multi.name}** berhasil diupload")
    st.markdown("<br>#### 📝 3 Job Description")
    st.markdown("<small style='color:#6366f1'>Bandingkan 1 CV ke 3 posisi berbeda</small>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    cols_jd = st.columns(3, gap="medium")
    jd_list, jd_labels = [], []
    for i, col in enumerate(cols_jd):
        with col:
            lbl = st.text_input(f"Nama Posisi #{i+1}", placeholder="e.g. Data Scientist", key=f"jd_label_{i}")
            jd = st.text_area(f"JD #{i+1}", height=220, placeholder="Paste JD...", key=f"jd_multi_{i}", label_visibility="collapsed")
            jd_list.append(jd); jd_labels.append(lbl if lbl else f"Posisi {i+1}")
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀  Bandingkan 3 JD", type="primary", use_container_width=True, key="btn_multi"):
        if not cv_file_multi: st.error("❌ Upload CV dulu!")
        elif not all(jd.strip() for jd in jd_list): st.error("❌ Isi semua 3 JD!")
        else:
            with st.spinner("🤖 Menganalisis 3 JD... (~30 detik)"):
                cv_text_multi = extract_text_from_pdf(cv_file_multi)
                if cv_text_multi:
                    st.session_state["multi_results"] = analyze_multi(cv_text_multi, jd_list, jd_labels)
                    st.session_state["multi_labels"] = jd_labels
                else: st.error("❌ Gagal membaca PDF.")
    if "multi_results" in st.session_state:
        render_multi_result(st.session_state["multi_results"], st.session_state["multi_labels"])

# ── TAB 3 ─────────────────────────────────────────────
with tab3:
    st.markdown("<br>", unsafe_allow_html=True)
    col_ca_l, col_ca_r = st.columns([1, 1.8], gap="large")
    with col_ca_l:
        st.markdown("#### 🧭 Career Advisor")
        st.markdown("""<div style="background:#f5f3ff;border:1px solid #e0e7ff;border-radius:14px;padding:1.2rem 1.5rem;margin-bottom:1rem">
            <div style="font-weight:600;color:#4338ca;margin-bottom:.5rem">✨ Yang kamu dapatkan:</div>
            <ul style="color:#4338ca;font-size:.87rem;line-height:2;margin:0;padding-left:1.2rem">
                <li>4-5 rekomendasi posisi + estimasi gaji</li>
                <li>Skill gap &amp; cara belajarnya</li>
                <li>2 jalur karir yang bisa dipilih</li>
                <li>Action plan mingguan/bulanan</li>
                <li>Platform cari kerja terbaik</li>
            </ul></div>""", unsafe_allow_html=True)
        cv_career = st.file_uploader("PDF", type=["pdf"], key="cv_career", label_visibility="collapsed")
        if cv_career: st.success(f"✅ **{cv_career.name}** berhasil diupload")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🧭  Analisis Karir Saya", type="primary", use_container_width=True, key="btn_career"):
            if not cv_career: st.error("❌ Upload CV dulu!")
            else:
                with st.spinner("🤖 Menganalisis potensi karir... (~20 detik)"):
                    cv_text_c = extract_text_from_pdf(cv_career)
                    if cv_text_c: st.session_state["career_result"] = analyze_career(cv_text_c)
                    else: st.error("❌ Gagal membaca PDF.")
    with col_ca_r:
        if "career_result" in st.session_state:
            render_career_result(st.session_state["career_result"])
        else:
            st.markdown("""<div class="empty-state" style="height:350px"><div style="font-size:3rem">🧭</div>
                <div style="color:#6366f1;font-size:.95rem;text-align:center;line-height:1.7;font-weight:500">
                Upload CV dan klik <b>Analisis Karir Saya</b><br>
                <span style="color:#94a3b8;font-weight:400;font-size:.85rem">AI analisis potensi karir kamu secara menyeluruh</span>
                </div></div>""", unsafe_allow_html=True)

# ── TAB 4 — HRD SCREENER ──────────────────────────────
with tab4:
    st.markdown("<br>", unsafe_allow_html=True)
    col_hrd_l, col_hrd_r = st.columns([1, 1.8], gap="large")

    with col_hrd_l:
        st.markdown("#### 🏢 HRD CV Screener")
        st.markdown("""<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:14px;padding:1.2rem 1.5rem;margin-bottom:1rem">
            <div style="font-weight:600;color:#065f46;margin-bottom:.5rem">🎯 Untuk HRD & Recruiter:</div>
            <ul style="color:#065f46;font-size:.87rem;line-height:2;margin:0;padding-left:1.2rem">
                <li>Upload <b>banyak CV sekaligus</b> (PDF)</li>
                <li>AI ranking otomatis berdasarkan JD</li>
                <li>Status: Lolos / Pertimbangkan / Ditolak</li>
                <li>Kekuatan &amp; kelemahan per kandidat</li>
                <li>Saran pertanyaan interview</li>
                <li>Export ranking ke CSV</li>
            </ul></div>""", unsafe_allow_html=True)

        st.markdown("#### 📎 Upload CV Kandidat (bisa banyak)")
        cv_files_hrd = st.file_uploader(
            "Upload semua CV kandidat (PDF)",
            type=["pdf"], accept_multiple_files=True,
            key="cv_hrd", label_visibility="collapsed"
        )
        if cv_files_hrd:
            st.success(f"✅ **{len(cv_files_hrd)} CV** berhasil diupload")
            for f in cv_files_hrd:
                st.markdown(f"<small style='color:#6366f1'>· {f.name}</small>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📝 Job Description yang Dibuka")
        jd_hrd = st.text_area("JD HRD", height=200,
            placeholder="Paste job description posisi yang sedang dibuka...\n\nContoh:\nKami mencari Data Analyst dengan pengalaman minimal 2 tahun...",
            key="jd_hrd", label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🔍  Screen Semua Kandidat", type="primary", use_container_width=True, key="btn_hrd"):
            if not cv_files_hrd:
                st.error("❌ Upload minimal 1 CV kandidat!")
            elif not jd_hrd.strip():
                st.error("❌ Job description tidak boleh kosong!")
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()
                cv_data = []
                for i, f in enumerate(cv_files_hrd):
                    status_text.markdown(f"<small style='color:#6366f1'>📄 Membaca {f.name}...</small>", unsafe_allow_html=True)
                    text = extract_text_from_pdf(f)
                    name = f.name.replace(".pdf", "").replace("_", " ").replace("-", " ").title()
                    cv_data.append((name, text if text else ""))
                    progress_bar.progress((i+1) / len(cv_files_hrd) * 0.3)

                status_text.markdown(f"<small style='color:#6366f1'>🤖 AI menganalisis {len(cv_data)} kandidat...</small>", unsafe_allow_html=True)

                results_hrd = []
                for i, (name, cv_text) in enumerate(cv_data):
                    status_text.markdown(f"<small style='color:#6366f1'>🤖 Menganalisis {name}... ({i+1}/{len(cv_data)})</small>", unsafe_allow_html=True)
                    from utils.analyzer import screen_candidate
                    result = screen_candidate(cv_text, jd_hrd, name)
                    results_hrd.append(result)
                    progress_bar.progress(0.3 + (i+1)/len(cv_data)*0.7)

                results_hrd.sort(key=lambda x: x.get("match_score", 0), reverse=True)
                st.session_state["hrd_results"] = results_hrd
                progress_bar.empty()
                status_text.empty()
                st.success(f"✅ Screening selesai! {len(results_hrd)} kandidat dianalisis.")

    with col_hrd_r:
        if "hrd_results" in st.session_state:
            render_hrd_results(st.session_state["hrd_results"])
        else:
            st.markdown("""<div class="empty-state" style="height:400px"><div style="font-size:3rem">🏢</div>
                <div style="color:#6366f1;font-size:.95rem;text-align:center;line-height:1.7;font-weight:500">
                Upload CV kandidat &amp; paste job description<br>
                <span style="color:#94a3b8;font-weight:400;font-size:.85rem">AI akan ranking semua kandidat otomatis</span>
                </div></div>""", unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""<div class="footer">
    🎯 SmartCV Analyzer &nbsp;·&nbsp; by <strong style="color:#6366f1">Dirga</strong>
    &nbsp;·&nbsp; Powered by Groq + LLaMA 3.3 70B
    &nbsp;·&nbsp; <a href="https://github.com" target="_blank">GitHub</a>
</div>""", unsafe_allow_html=True)
