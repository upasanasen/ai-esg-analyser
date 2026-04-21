import streamlit as st
import anthropic
import pymupdf
import json
import re
import os
from pathlib import Path

st.set_page_config(
    page_title="AI ESG Report Analyser",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.main { background: #FAFAF8; }
.block-container { padding: 2rem 2.5rem 4rem; max-width: 1100px; }

.hero {
    background: #0F6E56;
    border-radius: 16px;
    padding: 2.5rem 2.5rem 2rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::after {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 220px; height: 220px;
    border-radius: 50%;
    background: rgba(255,255,255,0.04);
}
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: .18em;
    color: rgba(255,255,255,.55);
    text-transform: uppercase;
    margin-bottom: 10px;
}
.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 32px;
    color: #fff;
    margin: 0 0 8px;
    line-height: 1.15;
}
.hero-sub {
    font-size: 14px;
    color: rgba(255,255,255,.7);
    margin: 0;
    line-height: 1.6;
}
.hero-tags {
    display: flex; gap: 8px; flex-wrap: wrap;
    margin-top: 16px;
}
.hero-tag {
    font-size: 11px; font-weight: 500;
    padding: 4px 10px; border-radius: 99px;
    background: rgba(255,255,255,.12);
    color: rgba(255,255,255,.85);
    letter-spacing: .03em;
}

.score-ring-wrap { text-align: center; padding: 1rem 0; }
.score-val {
    font-family: 'DM Serif Display', serif;
    font-size: 64px; line-height: 1;
    margin-bottom: 4px;
}
.score-grade {
    font-family: 'DM Serif Display', serif;
    font-size: 28px;
}
.score-label { font-size: 12px; color: #888780; margin-top: 4px; }

.kpi-card {
    background: #fff;
    border: 0.5px solid #E5E5E3;
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 12px;
}
.kpi-val {
    font-family: 'DM Serif Display', serif;
    font-size: 22px; color: #0F6E56;
    margin-bottom: 4px;
}
.kpi-name { font-size: 12px; color: #5F5E5A; line-height: 1.4; }

.fw-section { margin-bottom: 1.5rem; }
.fw-label-row {
    display: flex; justify-content: space-between;
    align-items: center; margin-bottom: 4px;
}
.fw-name { font-size: 13px; font-weight: 500; color: #2C2C2A; }
.fw-pct { font-size: 13px; font-weight: 500; }

.flag-card {
    border-left: 4px solid;
    border-radius: 0 10px 10px 0;
    padding: 12px 14px;
    margin-bottom: 10px;
}
.flag-high { background: #FCEBEB; border-color: #A32D2D; }
.flag-medium { background: #FAEEDA; border-color: #BA7517; }
.flag-low { background: #F1EFE8; border-color: #5F5E5A; }
.flag-title { font-size: 13px; font-weight: 500; margin-bottom: 3px; }
.flag-high .flag-title { color: #791F1F; }
.flag-medium .flag-title { color: #633806; }
.flag-low .flag-title { color: #444441; }
.flag-body { font-size: 12px; line-height: 1.6; }
.flag-high .flag-body { color: #A32D2D; }
.flag-medium .flag-body { color: #854F0B; }
.flag-low .flag-body { color: #5F5E5A; }

.esrs-pill {
    display: inline-block;
    font-size: 11px; font-weight: 500;
    padding: 3px 9px; border-radius: 99px;
    margin: 3px;
}
.esrs-disclosed { background: #E1F5EE; color: #085041; }
.esrs-partial   { background: #FAEEDA; color: #633806; }
.esrs-missing   { background: #FCEBEB; color: #791F1F; }

.rec-item {
    display: flex; gap: 12px; align-items: flex-start;
    padding: 12px 0; border-bottom: 0.5px solid #F0F0EE;
}
.rec-num {
    width: 26px; height: 26px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 500; flex-shrink: 0;
}
.rec-high { background: #FCEBEB; color: #791F1F; }
.rec-med  { background: #FAEEDA; color: #633806; }
.rec-text { font-size: 13px; color: #2C2C2A; line-height: 1.6; }
.rec-fw   { font-size: 11px; color: #888780; margin-top: 3px; }

.section-header {
    font-family: 'DM Serif Display', serif;
    font-size: 20px; color: #1A1A18;
    margin: 2rem 0 1rem;
    padding-bottom: 8px;
    border-bottom: 2px solid #0F6E56;
}

.upload-zone {
    border: 2px dashed #C8C8C4;
    border-radius: 12px;
    padding: 2.5rem;
    text-align: center;
    background: #fff;
    margin-bottom: 1rem;
}
.demo-badge {
    display: inline-block;
    background: #E1F5EE; color: #085041;
    font-size: 11px; font-weight: 500;
    padding: 4px 10px; border-radius: 99px;
    margin-bottom: 12px;
}
.author-credit {
    font-size: 11px; color: #888780;
    text-align: center; margin-top: 3rem;
    padding-top: 1rem; border-top: 0.5px solid #E5E5E3;
}
.stProgress > div > div { background: #1D9E75 !important; }
div[data-testid="stProgress"] div { background: #1D9E75; }
</style>
""", unsafe_allow_html=True)

# ── SYSTEM PROMPT ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert ESG analyst specialising in CSRD, ESRS, GRI Standards, TCFD, and GHG Protocol.
Analyse the sustainability report and respond ONLY with a valid JSON object — no markdown, no preamble.

JSON schema:
{
  "company": "string",
  "report_year": "string",
  "overall_score": number (0-100),
  "grade": "A|B|C|D|F",
  "executive_summary": "2-3 sentence assessment",
  "kpis": [
    {"name": "string", "value": "string", "framework": "GRI|ESRS|TCFD|GHG Protocol", "topic": "E|S|G", "confidence": "high|medium|low"}
  ],
  "framework_coverage": {
    "GRI":          {"score": number, "gaps": ["string"], "strengths": ["string"]},
    "ESRS":         {"score": number, "gaps": ["string"], "strengths": ["string"]},
    "TCFD":         {"score": number, "gaps": ["string"], "strengths": ["string"]},
    "GHG_Protocol": {"score": number, "gaps": ["string"], "strengths": ["string"]}
  },
  "greenwashing_flags": [
    {"severity": "high|medium|low", "claim": "string", "issue": "string", "recommendation": "string"}
  ],
  "double_materiality": {
    "assessed": boolean,
    "quality": "strong|adequate|weak|absent",
    "impact_materiality": "string",
    "financial_materiality": "string",
    "gaps": ["string"]
  },
  "esrs_topics": [
    {"topic": "string", "code": "string", "status": "disclosed|partial|missing", "notes": "string"}
  ],
  "recommendations": [
    {"priority": "high|medium", "action": "string", "framework": "string"}
  ]
}

Extract at least 8 KPIs. Flag greenwashing aggressively. Be rigorous."""



# ── HELPERS ──────────────────────────────────────────────────────────────────
def extract_pdf_text(uploaded_file) -> str:
    data = uploaded_file.read()
    doc = pymupdf.open(stream=data, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text[:80000]

def score_color(score: int) -> str:
    if score >= 70: return "#1D9E75"
    if score >= 50: return "#BA7517"
    return "#E24B4A"

def grade_color(grade: str) -> str:
    return {"A": "#1D9E75", "B": "#0F6E56", "C": "#BA7517", "D": "#E24B4A", "F": "#A32D2D"}.get(grade, "#888780")

def render_progress(label: str, value: int, color: str):
    st.markdown(f"""
    <div class="fw-section">
      <div class="fw-label-row">
        <span class="fw-name">{label}</span>
        <span class="fw-pct" style="color:{color}">{value}%</span>
      </div>
    </div>""", unsafe_allow_html=True)
    st.progress(value / 100)

def call_claude(text: str) -> dict:
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Analyse this sustainability report comprehensively:\n\n{text}"}]
    )
    raw = response.content[0].text
    clean = re.sub(r"```json|```", "", raw).strip()
    return json.loads(clean)

def render_dashboard(data: dict):
    # ── SCORE HEADER ──────────────────────────────────────────────────────────
    col_score, col_summary = st.columns([1, 3])
    with col_score:
        gc = grade_color(data["grade"])
        sc = score_color(data["overall_score"])
        st.markdown(f"""
        <div class="score-ring-wrap">
          <div class="score-val" style="color:{sc}">{data['overall_score']}</div>
          <div class="score-grade" style="color:{gc}">Grade {data['grade']}</div>
          <div class="score-label">Overall ESG score</div>
        </div>""", unsafe_allow_html=True)

    with col_summary:
        st.markdown(f"### {data['company']}")
        st.caption(f"Reporting period: {data['report_year']}")
        st.markdown(f"*{data['executive_summary']}*")

        dm = data.get("double_materiality", {})
        dm_color = {"strong": "#1D9E75", "adequate": "#BA7517", "weak": "#E24B4A", "absent": "#A32D2D"}.get(dm.get("quality",""), "#888780")
        dm_label = dm.get("quality", "unknown").title()
        dma_done = "Yes" if dm.get("assessed") else "No"
        st.markdown(f"""
        <div style="display:flex;gap:10px;margin-top:10px;flex-wrap:wrap">
          <span style="font-size:12px;background:#E1F5EE;color:#085041;padding:3px 10px;border-radius:99px;font-weight:500">
            {len(data.get('kpis',[]))} KPIs extracted
          </span>
          <span style="font-size:12px;background:#FCEBEB;color:#791F1F;padding:3px 10px;border-radius:99px;font-weight:500">
            {len([f for f in data.get('greenwashing_flags',[]) if f['severity']=='high'])} high-severity flags
          </span>
          <span style="font-size:12px;background:{dm_color}22;color:{dm_color};padding:3px 10px;border-radius:99px;font-weight:500">
            DMA: {dma_done} · {dm_label}
          </span>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # ── TABS ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Framework scores",
        "📈 Key KPIs",
        "🚩 Greenwashing flags",
        "🗂 ESRS coverage",
        "⚖️ Double materiality",
        "✅ Recommendations"
    ])

    # TAB 1 — FRAMEWORK SCORES
    with tab1:
        st.markdown('<div class="section-header">Framework coverage analysis</div>', unsafe_allow_html=True)
        fw = data.get("framework_coverage", {})
        fw_names = {"GRI": "GRI Standards", "ESRS": "ESRS (EU)", "TCFD": "TCFD", "GHG_Protocol": "GHG Protocol"}
        for key, label in fw_names.items():
            if key not in fw: continue
            d = fw[key]
            color = score_color(d["score"])
            render_progress(label, d["score"], color)

            with st.expander(f"View {label} gap analysis"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Strengths**")
                    for s in d.get("strengths", []):
                        st.markdown(f"✓ {s}")
                with c2:
                    st.markdown("**Gaps**")
                    for g in d.get("gaps", []):
                        st.markdown(f"✗ {g}")

    # TAB 2 — KPIs
    with tab2:
        st.markdown('<div class="section-header">Extracted KPIs</div>', unsafe_allow_html=True)
        kpis = data.get("kpis", [])
        topic_filter = st.selectbox("Filter by topic", ["All", "Environmental (E)", "Social (S)", "Governance (G)"])
        fw_filter = st.selectbox("Filter by framework", ["All", "GHG Protocol", "GRI", "ESRS", "TCFD"])

        filtered = kpis
        if topic_filter != "All":
            t = topic_filter[topic_filter.index("(")+1]
            filtered = [k for k in filtered if k.get("topic") == t]
        if fw_filter != "All":
            filtered = [k for k in filtered if fw_filter.lower() in k.get("framework","").lower()]

        cols = st.columns(3)
        for i, kpi in enumerate(filtered):
            conf_color = {"high": "#1D9E75", "medium": "#BA7517", "low": "#888780"}.get(kpi.get("confidence",""), "#888780")
            with cols[i % 3]:
                st.markdown(f"""
                <div class="kpi-card">
                  <div class="kpi-val">{kpi['value']}</div>
                  <div class="kpi-name">{kpi['name']}</div>
                  <div style="margin-top:7px;display:flex;gap:5px">
                    <span style="font-size:10px;background:#E6F1FB;color:#0C447C;padding:2px 7px;border-radius:99px;font-weight:500">{kpi.get('framework','')}</span>
                    <span style="font-size:10px;background:{conf_color}22;color:{conf_color};padding:2px 7px;border-radius:99px;font-weight:500">{kpi.get('confidence','')} confidence</span>
                  </div>
                </div>""", unsafe_allow_html=True)

    # TAB 3 — GREENWASHING
    with tab3:
        st.markdown('<div class="section-header">Greenwashing risk flags</div>', unsafe_allow_html=True)
        flags = data.get("greenwashing_flags", [])
        if not flags:
            st.success("No significant greenwashing risks detected.")
        else:
            sev_order = {"high": 0, "medium": 1, "low": 2}
            flags_sorted = sorted(flags, key=lambda x: sev_order.get(x.get("severity","low"), 2))
            for f in flags_sorted:
                sev = f.get("severity","low")
                css = f"flag-{sev}"
                sev_label = {"high": "HIGH RISK", "medium": "MEDIUM RISK", "low": "LOW RISK"}.get(sev,"")
                st.markdown(f"""
                <div class="flag-card {css}">
                  <div style="font-size:10px;font-weight:700;letter-spacing:.08em;margin-bottom:5px;opacity:.7">{sev_label}</div>
                  <div class="flag-title">"{f.get('claim','')}"</div>
                  <div class="flag-body"><strong>Issue:</strong> {f.get('issue','')}</div>
                  <div class="flag-body" style="margin-top:5px"><strong>Fix:</strong> {f.get('recommendation','')}</div>
                </div>""", unsafe_allow_html=True)

    # TAB 4 — ESRS
    with tab4:
        st.markdown('<div class="section-header">ESRS topic coverage</div>', unsafe_allow_html=True)
        topics = data.get("esrs_topics", [])
        legend_html = """
        <div style="display:flex;gap:12px;margin-bottom:1rem;flex-wrap:wrap">
          <span class="esrs-pill esrs-disclosed">Disclosed</span>
          <span class="esrs-pill esrs-partial">Partial</span>
          <span class="esrs-pill esrs-missing">Missing</span>
        </div>"""
        st.markdown(legend_html, unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        for i, t in enumerate(topics):
            status = t.get("status","missing")
            css = f"esrs-{status}"
            with (c1 if i % 2 == 0 else c2):
                st.markdown(f"""
                <div style="border:0.5px solid #E5E5E3;border-radius:10px;padding:12px 14px;margin-bottom:8px;background:#fff">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px">
                    <span style="font-size:13px;font-weight:500;color:#2C2C2A">{t.get('code','')} &ndash; {t.get('topic','')}</span>
                    <span class="esrs-pill {css}">{status}</span>
                  </div>
                  <div style="font-size:11px;color:#5F5E5A;line-height:1.5">{t.get('notes','')}</div>
                </div>""", unsafe_allow_html=True)

    # TAB 5 — DOUBLE MATERIALITY
    with tab5:
        st.markdown('<div class="section-header">Double materiality assessment</div>', unsafe_allow_html=True)
        dm = data.get("double_materiality", {})
        assessed = dm.get("assessed", False)
        quality = dm.get("quality", "absent")

        if not assessed:
            st.error("Double materiality assessment: **not conducted**")
        else:
            q_color = {"strong":"#1D9E75","adequate":"#BA7517","weak":"#E24B4A","absent":"#A32D2D"}.get(quality,"#888780")
            st.markdown(f"Quality: **{quality.title()}**")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Impact materiality**")
            st.info(dm.get("impact_materiality", "Not assessed"))
        with c2:
            st.markdown("**Financial materiality**")
            st.warning(dm.get("financial_materiality", "Not assessed"))

        if dm.get("gaps"):
            st.markdown("**Gaps identified**")
            for g in dm["gaps"]:
                st.markdown(f"- {g}")

    # TAB 6 — RECOMMENDATIONS
    with tab6:
        st.markdown('<div class="section-header">Prioritised recommendations</div>', unsafe_allow_html=True)
        recs = data.get("recommendations", [])
        high = [r for r in recs if r.get("priority") == "high"]
        med  = [r for r in recs if r.get("priority") == "medium"]

        if high:
            st.markdown("#### High priority")
            for i, r in enumerate(high, 1):
                st.markdown(f"""
                <div class="rec-item">
                  <div class="rec-num rec-high">{i}</div>
                  <div>
                    <div class="rec-text">{r['action']}</div>
                    <div class="rec-fw">{r.get('framework','')}</div>
                  </div>
                </div>""", unsafe_allow_html=True)

        if med:
            st.markdown("#### Medium priority")
            for i, r in enumerate(med, len(high)+1):
                st.markdown(f"""
                <div class="rec-item">
                  <div class="rec-num rec-med">{i}</div>
                  <div>
                    <div class="rec-text">{r['action']}</div>
                    <div class="rec-fw">{r.get('framework','')}</div>
                  </div>
                </div>""", unsafe_allow_html=True)

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    # Hero
    st.markdown("""
    <div class="hero">
      <div class="hero-eyebrow">ESG Intelligence Suite &middot; Upasana Sen</div>
      <div class="hero-title">AI ESG Report Analyser</div>
      <div class="hero-sub">
        Upload any sustainability report PDF. Claude AI extracts KPIs, scores against
        GRI, ESRS, TCFD &amp; GHG Protocol, flags greenwashing risks, and assesses
        CSRD readiness — in under 60 seconds.
      </div>
      <div class="hero-tags">
        <span class="hero-tag">CSRD / ESRS</span>
        <span class="hero-tag">GRI Standards</span>
        <span class="hero-tag">TCFD</span>
        <span class="hero-tag">GHG Protocol</span>
        <span class="hero-tag">Greenwashing detection</span>
        <span class="hero-tag">Double materiality</span>
      </div>
    </div>""", unsafe_allow_html=True)

    # Sidebar — about
    with st.sidebar:
        st.markdown("### About this tool")
        st.markdown("""
Built by **Upasana Sen** — Sustainability PM & ESG Data Specialist.

This tool demonstrates applied AI in ESG compliance work, combining:
- Claude Sonnet AI for structured document analysis
- CSRD/ESRS framework expertise
- GHG Protocol Scope 1–3 methodology
- TCFD & GRI Standards knowledge

**Tech stack:** Python · Streamlit · Claude API · PyMuPDF

[Portfolio](https://upasanasen.github.io/pm-sustainability-portfolio/) ·
[GitHub](https://github.com/upasanasen) ·
[LinkedIn](https://linkedin.com/in/upasana-sen)
        """)
        st.divider()
        st.markdown("### Methodology")
        st.markdown("""
1. **PDF extraction** — PyMuPDF extracts full text
2. **AI analysis** — Claude Sonnet analyses against 4 frameworks
3. **Structured output** — JSON schema ensures consistency
4. **Scoring** — Based on disclosure completeness, not claims
        """)

    # Upload zone
    st.markdown("""
    <div class="upload-zone">
      <div style="font-size:15px;font-weight:500;color:#2C2C2A;margin-bottom:6px">
        Drop your sustainability report here
      </div>
      <div style="font-size:13px;color:#888780">
        PDF format &middot; Annual reports, CSRD disclosures, ESG reports &middot; Up to 50MB
      </div>
    </div>""", unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="collapsed")

    if uploaded:
        st.success(f"Uploaded: **{uploaded.name}** ({uploaded.size/1024:.0f} KB)")
        if st.button("🔍 Analyse report", type="primary", use_container_width=True):
            with st.spinner(""):
                prog = st.progress(0, text="Extracting text from PDF...")
                text = extract_pdf_text(uploaded)
                prog.progress(30, text=f"Extracted {len(text):,} characters · Sending to Claude AI...")
                try:
                    result = call_claude(text)
                    prog.progress(90, text="Processing analysis...")
                    prog.progress(100, text="Done")
                    st.balloons()
                    render_dashboard(result)
                except Exception as e:
                    prog.empty()
                    st.error(f"Analysis failed: {e}")
                    st.info("Tip: If the PDF is scanned/image-based, text extraction may be limited.")
    else:
        st.markdown("""
        <div style="margin-top:1.5rem;display:grid;grid-template-columns:repeat(3,1fr);gap:12px">
          <div style="padding:14px 16px;background:#fff;border:0.5px solid #E5E5E3;border-radius:10px">
            <div style="font-size:13px;font-weight:500;color:#2C2C2A;margin-bottom:5px">KPI extraction</div>
            <div style="font-size:11px;color:#5F5E5A;line-height:1.5">Pulls GHG emissions, energy, water, social metrics — mapped to GRI, ESRS, TCFD and GHG Protocol</div>
          </div>
          <div style="padding:14px 16px;background:#fff;border:0.5px solid #E5E5E3;border-radius:10px">
            <div style="font-size:13px;font-weight:500;color:#2C2C2A;margin-bottom:5px">Framework scoring</div>
            <div style="font-size:11px;color:#5F5E5A;line-height:1.5">Scores disclosure completeness against 4 frameworks with detailed gap analysis per standard</div>
          </div>
          <div style="padding:14px 16px;background:#fff;border:0.5px solid #E5E5E3;border-radius:10px">
            <div style="font-size:13px;font-weight:500;color:#2C2C2A;margin-bottom:5px">Greenwashing detection</div>
            <div style="font-size:11px;color:#5F5E5A;line-height:1.5">Flags vague claims, missing baselines, softened targets and unverified assertions by severity</div>
          </div>
        </div>""", unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div class="author-credit">
      Built by Upasana Sen · Sustainability PM & ESG Data Specialist ·
      <a href="https://upasanasen.github.io/pm-sustainability-portfolio/" target="_blank">Portfolio</a> ·
      <a href="https://github.com/upasanasen" target="_blank">GitHub</a>
    </div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
