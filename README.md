# AI ESG Report Analyser

**Live demo → [esg-analyser.streamlit.app](https://esg-analyser.streamlit.app)**

A production-grade AI tool that analyses corporate sustainability reports against four major ESG frameworks — GRI, ESRS, TCFD, and GHG Protocol — and flags greenwashing risks using Claude Sonnet AI.

Built by **Upasana Sen** as part of a portfolio demonstrating applied AI in ESG compliance work.

---

## What it does

Upload any sustainability report PDF. The tool:

- Extracts full text using PyMuPDF
- Sends the report to Claude Sonnet for structured AI analysis
- Returns a scored, tabbed dashboard covering:
  - **Framework coverage** — GRI, ESRS, TCFD, GHG Protocol scores with gap analysis
  - **KPI extraction** — all disclosed metrics mapped to frameworks with confidence levels
  - **Greenwashing detection** — specific claims flagged by severity with fix recommendations
  - **ESRS topic coverage** — E1–G1 topic status (disclosed / partial / missing)
  - **Double materiality** — impact and financial materiality assessment quality
  - **Recommendations** — prioritised action list for reporting improvement

---

## Tech stack

```
Python 3.11+
Streamlit          — UI framework
Anthropic SDK      — Claude Sonnet AI analysis
PyMuPDF            — PDF text extraction
```

---

## Methodology

### Framework scoring
Scores are based on **disclosure completeness**, not the quality of sustainability performance. A company can have excellent environmental practices but score low if disclosures are absent or unquantified.

Scoring criteria per framework:

**GHG Protocol (0–100)**
- Scope 1, 2, 3 coverage and completeness
- Baseline year definition and consistency
- Science-based target alignment
- Methodological transparency

**GRI Standards (0–100)**
- Coverage of core GRI 2 (General Disclosures) topics
- Material topic identification and disclosure
- Stakeholder engagement documentation
- GRI content index presence

**TCFD (0–100)**
- Governance pillar: board oversight, management roles
- Strategy pillar: climate risks and opportunities, scenario analysis
- Risk management pillar: identification and integration processes
- Metrics and targets pillar: Scope 1–3 and progress metrics

**ESRS (0–100)**
- Double materiality assessment quality
- E1–G1 topical standard coverage
- ESRS 1 (General Requirements) compliance
- Data point disclosure against ESRS 2 requirements

### Greenwashing detection
Flags are raised when reports contain:
- Vague qualitative claims without quantitative backing
- Missing baseline years or comparison periods
- Unverified certifications or endorsements
- Cherry-picked metrics omitting negative trends
- Softened or removed targets without explanation
- Social impact claims without outcome metrics

Severity classification:
- **High** — material misrepresentation risk or removed commitments
- **Medium** — incomplete disclosure, unverifiable claims
- **Low** — minor omissions or stylistic concerns

---

## Run locally

```bash
git clone https://github.com/upasanasen/ai-esg-analyser
cd ai-esg-analyser
pip install -r requirements.txt

# Add your API key
mkdir .streamlit
echo 'ANTHROPIC_API_KEY = "your-key"' > .streamlit/secrets.toml

streamlit run app.py
```

---

## Deploy to Streamlit Cloud

1. Fork this repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Add `ANTHROPIC_API_KEY` in the Secrets section
5. Deploy

---

## Limitations

- Text-based PDFs only — scanned/image PDFs have limited extraction
- First 80,000 characters are analysed (covers most annual reports)
- Scoring is AI-generated and should be used as a starting point, not a definitive audit
- Framework interpretation reflects publicly available standards as of 2024–2025

---

## About the author

**Upasana Sen** — Sustainability Project Manager & ESG Data Specialist

MSc Environmental Studies & Sustainability Science (Lund University LUMES) ·
MSc Project Management (EAE Business School) ·
TCFD Practitioner · MIT LCA · Professional Scrum Master · Sustainability Reporting Practitioner

[Portfolio](https://upasanasen.github.io/pm-sustainability-portfolio/) ·
[LinkedIn](https://linkedin.com/in/upasana-sen) ·
[GitHub](https://github.com/upasanasen)

---

## Licence

MIT — free to use, modify, and distribute with attribution.
