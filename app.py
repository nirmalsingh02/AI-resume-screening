import html
import json
import os
import tempfile

import plotly.graph_objects as go
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.intelligence.experience_extractor import (
    calculate_experience_score,
    extract_experience_years,
)
from src.intelligence.pdf_reader import extract_text_from_pdf
from src.intelligence.resume_parser import build_candidate_profile
from src.intelligence.scoring import calculate_final_score, get_recommendation
from src.preprocessing.skill_extractor import extract_skills

st.set_page_config(page_title="Resume Intelligence", page_icon="🤖", layout="wide")

# ---------------------------------------------------------------- THEME
INK, TEAL, AMBER, ORANGE, ROSE = "#1F2A37", "#0F766E", "#B45309", "#C2410C", "#BE123C"

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
.block-container { padding-top: 2rem; max-width: 1200px; }

.hero { padding: 28px 32px; border-radius: 18px; color: #fff;
        background: linear-gradient(120deg, #1F2A37 0%, #134E4A 100%); margin-bottom: 22px; }
.hero h1 { margin: 0; font-size: 34px; font-weight: 700; letter-spacing: -0.5px; }
.hero p  { margin: 6px 0 0; font-size: 16px; opacity: .8; }

.kpi { border: 1px solid rgba(128,128,128,.25); border-radius: 14px; padding: 16px 18px; }
.kpi .v { font-size: 30px; font-weight: 700; line-height: 1.1; }
.kpi .l { font-size: 13px; opacity: .65; margin-top: 4px; }

.verdict { border-radius: 14px; padding: 18px 22px; border-left: 8px solid; margin: 8px 0 18px; }
.verdict b { font-size: 20px; }

.pill { display: inline-block; padding: 5px 12px; margin: 4px 6px 4px 0; border-radius: 999px;
        font-size: 13px; font-weight: 500; border: 1px solid; }
.pill.ok   { color: #0F766E; background: rgba(15,118,110,.10); border-color: rgba(15,118,110,.35); }
.pill.miss { color: #BE123C; background: rgba(190,18,60,.08);  border-color: rgba(190,18,60,.30); }
.pill.neu  { background: rgba(128,128,128,.10); border-color: rgba(128,128,128,.30); }

.contact { border: 1px solid rgba(128,128,128,.25); border-radius: 14px; padding: 14px 18px; }
div.stButton > button[kind="primary"] { border-radius: 12px; font-weight: 600; height: 3rem; }
</style>
""",
    unsafe_allow_html=True,
)


# -------------------------------------------------------------- HELPERS
def esc(x):
    return html.escape(str(x))


def pills(items, kind):
    if not items:
        return ""
    return "".join(f'<span class="pill {kind}">{esc(i)}</span>' for i in items)


def band(score, threshold):
    """Return (color, emoji, message) for a score."""
    if score >= 75:
        return TEAL, "🟢", "Strong candidate. High alignment with the job description."
    if score >= threshold:
        return AMBER, "🟡", "Reasonable alignment. Worth a review."
    if score >= 45:
        return ORANGE, "🟠", "Partial alignment with the position."
    return ROSE, "🔴", "Significant skill or requirement gaps."


def gauge(score, threshold, color):
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": "%", "font": {"size": 44}},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": color, "thickness": 0.28},
                "steps": [
                    {"range": [0, 45], "color": "rgba(190,18,60,.12)"},
                    {"range": [45, threshold], "color": "rgba(194,65,12,.12)"},
                    {"range": [threshold, 75], "color": "rgba(180,83,9,.12)"},
                    {"range": [75, 100], "color": "rgba(15,118,110,.14)"},
                ],
                "threshold": {"line": {"color": INK, "width": 3}, "value": threshold},
            },
        )
    )
    fig.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=10),
                      paper_bgcolor="rgba(0,0,0,0)")
    return fig


def radar(skill, text, exp):
    labels = ["Skill match", "Text similarity", "Experience"]
    vals = [skill, text, exp]
    fig = go.Figure(
        go.Scatterpolar(r=vals + vals[:1], theta=labels + labels[:1], fill="toself",
                        line=dict(color=TEAL), fillcolor="rgba(15,118,110,.25)")
    )
    fig.update_layout(height=280, margin=dict(l=50, r=50, t=30, b=20),
                      polar=dict(radialaxis=dict(range=[0, 100], showticklabels=False)),
                      showlegend=False, paper_bgcolor="rgba(0,0,0,0)")
    return fig


def bar_breakdown(skill, text, exp):
    fig = go.Figure(
        go.Bar(x=[skill, text, exp], y=["Skill match", "Text similarity", "Experience"],
               orientation="h", marker_color=[TEAL, "#2563EB", AMBER],
               text=[f"{v:.1f}%" for v in (skill, text, exp)], textposition="outside")
    )
    fig.update_layout(height=240, xaxis=dict(range=[0, 115]), margin=dict(l=10, r=10, t=10, b=10),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig


def analyze(resume_file, job_text):
    """Heavy work: runs once per click; results are cached in session_state."""
    pdf_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(resume_file.getvalue())
            pdf_path = tmp.name

        with st.status("Analyzing candidate…", expanded=True) as status:
            st.write("📄 Reading resume")
            resume_text = extract_text_from_pdf(pdf_path)
            if not resume_text.strip():
                status.update(label="Could not read resume", state="error")
                st.error("No text could be extracted. The PDF may be a scanned image.")
                return None

            st.write("👤 Building candidate profile")
            profile = build_candidate_profile(resume_text)

            st.write("🛠 Extracting skills")
            resume_skills = set(extract_skills(resume_text))
            job_skills = set(extract_skills(job_text))

            st.write("📊 Measuring text similarity")
            tfidf = TfidfVectorizer(stop_words="english").fit_transform([resume_text, job_text])
            text_similarity = float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]) * 100

            st.write("💼 Analyzing experience")
            years = extract_experience_years(resume_text)

            status.update(label="Analysis complete", state="complete", expanded=False)

        return {
            "profile": profile,
            "resume_text": resume_text,
            "job_text": job_text,
            "resume_skills": sorted(resume_skills),
            "job_skills": sorted(job_skills),
            "text_similarity": text_similarity,
            "years": years,
        }
    except Exception as e:
        st.error(f"Analysis error: {e}")
        return None
    finally:
        if pdf_path and os.path.exists(pdf_path):
            os.remove(pdf_path)


# --------------------------------------------------------------- HEADER
st.markdown(
    '<div class="hero"><h1>🤖 Resume Intelligence</h1>'
    "<p>Screen a resume against a job description in seconds: skills, similarity and experience in one score.</p></div>",
    unsafe_allow_html=True,
)

# -------------------------------------------------------------- SIDEBAR
with st.sidebar:
    st.header("⚙️ Screening settings")
    threshold = st.slider("Minimum match score", 0, 100, 60,
                          help="Scores at or above this are marked 'review'.")
    st.caption("Required experience for this role")
    req_min, req_max = st.slider("Years (min – max)", 0, 15, (0, 2))
    st.divider()
    st.caption("Changing these updates the result instantly. No need to re-analyze.")
    if st.button("🗑 Clear results", use_container_width=True):
        st.session_state.pop("result", None)
        st.rerun()

# --------------------------------------------------------------- INPUTS
c1, c2 = st.columns(2, gap="large")
with c1:
    st.subheader("📄 Candidate resume")
    resume_file = st.file_uploader("Upload resume (PDF)", type=["pdf"])
with c2:
    st.subheader("💼 Job description")
    tab_up, tab_paste = st.tabs(["Upload .txt", "Paste text"])
    with tab_up:
        job_file = st.file_uploader("Upload job description (TXT)", type=["txt"],
                                    label_visibility="collapsed")
    with tab_paste:
        pasted = st.text_area("Paste job description", height=150,
                              label_visibility="collapsed",
                              placeholder="Paste the job description here…")

job_text = pasted.strip() if pasted.strip() else (
    job_file.getvalue().decode("utf-8", errors="ignore") if job_file else ""
)

if st.button("🔍 Analyze candidate", type="primary", use_container_width=True):
    if resume_file is None:
        st.error("Upload a resume PDF to continue.")
    elif not job_text.strip():
        st.error("Add a job description (upload a .txt file or paste text).")
    else:
        result = analyze(resume_file, job_text)
        if result:
            st.session_state["result"] = result

# -------------------------------------------------------------- RESULTS
R = st.session_state.get("result")
if not R:
    st.info("Upload a resume and a job description, then select **Analyze candidate**.")
    st.stop()

profile = R["profile"]
resume_skills, job_skills = set(R["resume_skills"]), set(R["job_skills"])
matched, missing = resume_skills & job_skills, job_skills - resume_skills

skill_score = (len(matched) / len(job_skills) * 100) if job_skills else 0
text_similarity = R["text_similarity"]
experience_score = calculate_experience_score(
    candidate_years=R["years"], required_min=req_min, required_max=req_max
)
final_score = calculate_final_score(
    skill_score=skill_score, text_similarity=text_similarity, experience_score=experience_score
)
recommendation = get_recommendation(final_score)
color, emoji, message = band(final_score, threshold)

st.divider()

# Verdict banner
st.markdown(
    f'<div class="verdict" style="border-color:{color};background:{color}14">'
    f"<b>{emoji} {esc(recommendation)}</b><br>{esc(message)}</div>",
    unsafe_allow_html=True,
)

# KPI row
k = st.columns(4)
kpis = [
    (f"{final_score:.1f}%", "Final score"),
    (f"{skill_score:.0f}%", f"Skill match ({len(matched)}/{len(job_skills)})"),
    (f"{text_similarity:.0f}%", "Text similarity"),
    (f"{R['years']:.1f} yrs", f"Experience (need {req_min}–{req_max})"),
]
for col, (v, l) in zip(k, kpis):
    col.markdown(f'<div class="kpi"><div class="v">{v}</div><div class="l">{l}</div></div>',
                 unsafe_allow_html=True)

st.write("")

tab_over, tab_skills, tab_prof, tab_text = st.tabs(
    ["📈 Overview", "🧠 Skills", "👤 Profile", "📄 Documents"]
)

# ---- Overview
with tab_over:
    g, r = st.columns(2)
    with g:
        st.caption("Final score. The dark marker is your minimum match score.")
        st.plotly_chart(gauge(final_score, threshold, color), use_container_width=True)
    with r:
        st.caption("Score balance across the three signals")
        st.plotly_chart(radar(skill_score, text_similarity, experience_score),
                        use_container_width=True)
    st.plotly_chart(bar_breakdown(skill_score, text_similarity, experience_score),
                    use_container_width=True)

# ---- Skills
with tab_skills:
    view = st.radio("Show", ["All", "Matched", "Missing"], horizontal=True)
    query = st.text_input("Filter skills", placeholder="Type to filter, e.g. python")

    def keep(items):
        return [s for s in sorted(items) if query.lower() in s.lower()]

    a, b = st.columns(2)
    if view in ("All", "Matched"):
        with a:
            st.subheader(f"✅ Matched ({len(matched)})")
            st.markdown(pills(keep(matched), "ok") or "_None found._", unsafe_allow_html=True)
    if view in ("All", "Missing"):
        with b:
            st.subheader(f"⚠️ Missing ({len(missing)})")
            st.markdown(pills(keep(missing), "miss") or "🎉 No skill gaps.",
                        unsafe_allow_html=True)
    with st.expander(f"All candidate skills ({len(resume_skills)})"):
        st.markdown(pills(keep(resume_skills), "neu") or "_None detected._",
                    unsafe_allow_html=True)
    with st.expander(f"All required job skills ({len(job_skills)})"):
        st.markdown(pills(keep(job_skills), "neu") or "_None detected._",
                    unsafe_allow_html=True)

# ---- Profile
with tab_prof:
    p1, p2, p3 = st.columns(3)
    p1.metric("Name", profile.get("name", "Unknown"))
    p2.metric("Experience", f"{profile.get('experience', 0)} years")
    p3.metric("Skills", len(profile.get("skills", [])))

    st.markdown(
        f'<div class="contact">📧 <b>Email:</b> {esc(profile.get("email", "Not found"))}'
        f' &nbsp;&nbsp; 📱 <b>Phone:</b> {esc(profile.get("phone", "Not found"))}</div>',
        unsafe_allow_html=True,
    )
    st.write("")

    e, p = st.columns(2)
    with e:
        st.subheader("🎓 Education")
        for item in profile.get("education", []) or []:
            st.write(f"• {item}")
        if not profile.get("education"):
            st.info("No education information detected.")
    with p:
        st.subheader("🚀 Projects")
        for item in profile.get("projects", []) or []:
            st.write(f"• {item}")
        if not profile.get("projects"):
            st.info("No projects detected.")

    st.subheader("🧠 Core competencies")
    comps = profile.get("competencies", [])
    st.markdown(pills(comps, "neu") if comps else "_None detected._", unsafe_allow_html=True)

# ---- Documents
with tab_text:
    d1, d2 = st.columns(2)
    with d1:
        st.subheader("Extracted resume text")
        st.text_area("resume", R["resume_text"], height=380, label_visibility="collapsed")
    with d2:
        st.subheader("Job description")
        st.text_area("job", R["job_text"], height=380, label_visibility="collapsed")

# ------------------------------------------------------------- EXPORT
report = {
    "candidate": profile.get("name", "Unknown"),
    "final_score": round(final_score, 1),
    "recommendation": recommendation,
    "skill_score": round(skill_score, 1),
    "text_similarity": round(text_similarity, 1),
    "experience_years": R["years"],
    "matched_skills": sorted(matched),
    "missing_skills": sorted(missing),
}
st.download_button("⬇️ Download report (JSON)", json.dumps(report, indent=2),
                   file_name="screening_report.json", mime="application/json")