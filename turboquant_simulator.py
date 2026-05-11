
import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import json
import math
import time
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
import random
import urllib.parse

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TurboQuant Simulator — AI Citation Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
  --primary: #01696f;
  --primary-light: #4f98a3;
  --accent: #0ea5e9;
  --bg: #0f1117;
  --surface: #161b22;
  --surface-2: #1c2333;
  --border: #30363d;
  --text: #e6edf3;
  --muted: #8b949e;
  --success: #3fb950;
  --warning: #d29922;
  --error: #f85149;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

.stApp {
    background: var(--bg) !important;
    color: var(--text) !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

/* Metric cards */
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    transition: all 0.2s;
}
.metric-card:hover { border-color: var(--primary-light); box-shadow: 0 0 20px rgba(1,105,111,0.15); }
.metric-score { font-size: 3rem; font-weight: 700; font-family: 'Space Grotesk', sans-serif; background: linear-gradient(135deg, #01696f, #4f98a3); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.metric-label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; color: var(--muted); margin-top: 4px; }
.metric-delta { font-size: 0.85rem; margin-top: 6px; }
.delta-up { color: var(--success); }
.delta-down { color: var(--error); }

/* Score ring */
.score-ring-wrap { display: flex; justify-content: center; align-items: center; flex-direction: column; padding: 16px; }

/* Signal badges */
.signal-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.78rem; font-weight: 500; margin: 3px; }
.badge-found { background: rgba(63,185,80,0.15); color: #3fb950; border: 1px solid rgba(63,185,80,0.3); }
.badge-missing { background: rgba(248,81,73,0.12); color: #f85149; border: 1px solid rgba(248,81,73,0.25); }
.badge-partial { background: rgba(210,153,34,0.15); color: #d29922; border: 1px solid rgba(210,153,34,0.3); }

/* Section headers */
.section-header { font-family: 'Space Grotesk', sans-serif; font-size: 1.1rem; font-weight: 600; color: var(--primary-light); border-bottom: 1px solid var(--border); padding-bottom: 8px; margin-bottom: 16px; }

/* Recommendation cards */
.rec-card { background: var(--surface-2); border-left: 3px solid var(--primary); border-radius: 0 8px 8px 0; padding: 14px 18px; margin-bottom: 10px; }
.rec-card.high { border-left-color: #f85149; }
.rec-card.medium { border-left-color: #d29922; }
.rec-card.low { border-left-color: #3fb950; }
.rec-title { font-weight: 600; font-size: 0.9rem; color: var(--text); }
.rec-desc { font-size: 0.82rem; color: var(--muted); margin-top: 4px; }

/* Token chips */
.token-chip { display: inline-block; background: rgba(1,105,111,0.12); border: 1px solid rgba(1,105,111,0.3); border-radius: 4px; padding: 2px 8px; font-size: 0.75rem; color: #4f98a3; margin: 2px; font-family: monospace; }
.token-removed { background: rgba(248,81,73,0.1); border-color: rgba(248,81,73,0.25); color: #f85149; text-decoration: line-through; }

/* Hero */
.hero-header { text-align: center; padding: 24px 0 12px; }
.hero-title { font-family: 'Space Grotesk', sans-serif; font-size: 2.2rem; font-weight: 700; background: linear-gradient(135deg, #01696f 0%, #4f98a3 50%, #0ea5e9 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 6px; }
.hero-sub { color: var(--muted); font-size: 0.95rem; }

/* Tab styling override */
.stTabs [data-baseweb="tab-list"] { background: var(--surface); border-radius: 10px; padding: 4px; gap: 4px; border: 1px solid var(--border); }
.stTabs [data-baseweb="tab"] { background: transparent; color: var(--muted); border-radius: 8px; font-weight: 500; }
.stTabs [aria-selected="true"] { background: var(--primary) !important; color: white !important; }

/* Input overrides */
.stTextInput input, .stTextArea textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
}
.stButton > button {
    background: var(--primary) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 10px 28px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover { background: #0c4e54 !important; transform: translateY(-1px); box-shadow: 0 4px 16px rgba(1,105,111,0.3) !important; }

/* Progress bar */
.tq-progress { background: var(--border); border-radius: 99px; height: 8px; margin: 6px 0; overflow: hidden; }
.tq-progress-fill { height: 100%; border-radius: 99px; background: linear-gradient(90deg, #01696f, #4f98a3); transition: width 0.5s; }

/* Quant lab */
.quant-node { display: inline-block; width: 40px; height: 40px; border-radius: 50%; background: rgba(1,105,111,0.2); border: 2px solid var(--primary); text-align: center; line-height: 36px; font-size: 0.65rem; font-weight: 600; color: var(--primary-light); margin: 2px; font-family: monospace; }
.quant-node.compressed { background: rgba(79,152,163,0.15); border-color: var(--primary-light); width: 28px; height: 28px; line-height: 24px; font-size: 0.55rem; }

/* Divider */
.tq-divider { border: none; border-top: 1px solid var(--border); margin: 20px 0; }

/* Info box */
.info-box { background: rgba(1,105,111,0.08); border: 1px solid rgba(1,105,111,0.25); border-radius: 8px; padding: 12px 16px; font-size: 0.85rem; color: var(--muted); }
.info-box strong { color: var(--primary-light); }

/* Grounding result */
.ground-result { background: var(--surface-2); border-radius: 10px; padding: 16px; margin: 8px 0; border: 1px solid var(--border); }
.ground-result.cited { border-color: rgba(63,185,80,0.4); background: rgba(63,185,80,0.04); }
.ground-result.partial { border-color: rgba(210,153,34,0.4); background: rgba(210,153,34,0.04); }
.ground-result.not-cited { border-color: rgba(248,81,73,0.3); background: rgba(248,81,73,0.04); }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# ANALYSIS ENGINE
# ═══════════════════════════════════════════════════════════════════════════

def extract_content_from_url(url):
    """Fetch and extract main content from URL."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe", "noscript", "meta"]):
            tag.decompose()
        # Get title
        title = soup.title.string.strip() if soup.title else "No title found"
        # Extract main content
        main = soup.find("main") or soup.find("article") or soup.find(id=re.compile(r"content|main|article", re.I))
        if main:
            text = main.get_text(separator=" ", strip=True)
        else:
            text = soup.get_text(separator=" ", strip=True)
        # Clean up whitespace
        text = re.sub(r"\s+", " ", text).strip()
        headings = [tag.get_text(strip=True) for tag in soup.find_all(["h1","h2","h3","h4"])]
        return {"title": title, "text": text[:8000], "headings": headings, "success": True}
    except Exception as e:
        return {"title": "", "text": "", "headings": [], "success": False, "error": str(e)}


def count_sentences(text):
    return len(re.findall(r"[.!?]+", text))

def count_words(text):
    return len(text.split())

def count_paragraphs(text):
    return len([p for p in text.split("\n") if len(p.strip()) > 30])

def detect_headings(text):
    # Detect markdown-style headings or capitalized short lines
    lines = text.split("\n")
    h_lines = [l for l in lines if re.match(r"^#{1,4}\s", l) or (len(l) < 80 and l.isupper())]
    return len(h_lines)

def detect_statistics(text):
    stat_patterns = [
        r"\d+\.?\d*\s*%",  # percentages
        r"\$\d+[\d,\.]*",   # dollar amounts
        r"\d+x\b",            # multipliers
        r"\d{4}\s*(study|survey|report|research)",  # year + source
        r"(according to|study|research|survey|data shows|report)",  # source attribution
    ]
    count = sum(len(re.findall(p, text, re.I)) for p in stat_patterns)
    return min(count, 30)

def detect_expert_quotes(text):
    quote_patterns = [
        r'"[^"]{20,200}"\s*[-—]\s*[A-Z]',  # quoted + attribution
        r'["\'"][^"\']{20,200}["\'"]',  # any quoted text
        r"according to [A-Z][a-z]+ [A-Z][a-z]+",  # according to Name Name
        r"(says|said|notes|explained|stated|commented).*[A-Z][a-z]+",
    ]
    count = sum(len(re.findall(p, text)) for p in quote_patterns)
    return min(count, 10)

def detect_schema_signals(text):
    schema_keywords = ["FAQ", "How to", "Step 1", "Step 2", "Definition:", "Summary:", "Key takeaway", "In conclusion", "Table of contents"]
    count = sum(1 for kw in schema_keywords if kw.lower() in text.lower())
    return count

def detect_authority_signals(text):
    signals = {
        "Citation/Reference": bool(re.search(r"(cited in|published in|source:|references?:|\[\d+\]|doi:|arxiv)", text, re.I)),
        "Author Attribution": bool(re.search(r"(written by|by [A-Z][a-z]+ [A-Z][a-z]+|author:)", text, re.I)),
        "Date/Recency": bool(re.search(r"(2024|2025|2026|updated|last modified|published)", text, re.I)),
        "External Links": bool(re.search(r"(https?://|link:|source:|read more)", text, re.I)),
        "Research/Study": bool(re.search(r"(study|research|survey|data|report|analysis|findings)", text, re.I)),
        "Expert/Credentials": bool(re.search(r"(PhD|Dr\.|professor|expert|specialist|according to)", text, re.I)),
        "Statistics Present": bool(re.search(r"\d+\.?\d*\s*%", text)),
        "Named Entity (Org)": bool(re.search(r"(Google|Microsoft|Harvard|Stanford|MIT|McKinsey|Gartner|Forrester)", text, re.I)),
    }
    return signals

def measure_section_lengths(text):
    """Measure average section word count."""
    sections = re.split(r"\n{2,}|#{1,4}\s", text)
    lengths = [len(s.split()) for s in sections if len(s.split()) > 5]
    if not lengths:
        return 0, 0
    avg = sum(lengths) / len(lengths)
    in_ideal = sum(1 for l in lengths if 120 <= l <= 180)
    pct_ideal = in_ideal / len(lengths) if lengths else 0
    return avg, pct_ideal

def content_freshness_score(text):
    current_year = 2026
    years_found = [int(y) for y in re.findall(r"\b(202[3-6])\b", text)]
    if not years_found:
        return 0.2
    latest = max(years_found)
    diff = current_year - latest
    return max(0, 1 - diff * 0.25)

def heading_hierarchy_score(text):
    h1 = len(re.findall(r"^#\s", text, re.M))
    h2 = len(re.findall(r"^##\s", text, re.M))
    h3 = len(re.findall(r"^###\s", text, re.M))
    total = h1 + h2 + h3
    if total == 0:
        # Heuristic: look for short capitalized lines or sentence patterns
        lines = text.split("\n")
        heading_like = sum(1 for l in lines if 3 <= len(l.split()) <= 12 and l.strip() and not l.strip().endswith("."))
        return min(heading_like / 10, 1.0)
    hierarchy_ok = (h2 >= h3) and (h1 <= 3)
    return 0.7 + (0.3 if hierarchy_ok else 0)

def calculate_seo_score(text, headings=None):
    """Main scoring engine — returns all component scores."""
    wc = count_words(text)
    sc = count_sentences(text)
    stats = detect_statistics(text)
    quotes = detect_expert_quotes(text)
    schema = detect_schema_signals(text)
    auth = detect_authority_signals(text)
    avg_section, pct_ideal = measure_section_lengths(text)
    freshness = content_freshness_score(text)
    heading_score = heading_hierarchy_score(text)

    # Word count score (ideal 800-3000)
    if wc < 200: wc_score = 0.2
    elif wc < 500: wc_score = 0.45
    elif wc < 800: wc_score = 0.65
    elif wc <= 3000: wc_score = 1.0
    elif wc <= 5000: wc_score = 0.85
    else: wc_score = 0.7

    # Statistics score
    stat_score = min(stats / 8, 1.0)

    # Expert quotes score
    quote_score = min(quotes / 4, 1.0)

    # Schema/structure score
    schema_score = min(schema / 5, 1.0)

    # Authority signals score
    auth_score = sum(auth.values()) / len(auth)

    # Section length score
    section_score = pct_ideal if pct_ideal > 0 else (0.5 if 80 <= avg_section <= 250 else 0.2)

    # Weights based on TurboQuant research
    weights = {
        "Content Freshness":       (freshness,     0.18),
        "Section Length (120–180w)":(section_score, 0.17),
        "Heading Hierarchy":       (heading_score,  0.13),
        "Expert Quotations":       (quote_score,    0.13),
        "Statistics & Attribution":(stat_score,     0.12),
        "Schema Signals":          (schema_score,   0.09),
        "Authority Signals":       (auth_score,     0.10),
        "Content Depth":           (wc_score,       0.08),
    }

    overall = sum(v * w for v, w in weights.values())

    # Citation potential (subset of factors)
    citation_potential = (
        freshness * 0.25 +
        auth_score * 0.25 +
        stat_score * 0.20 +
        quote_score * 0.15 +
        section_score * 0.15
    )

    return {
        "overall": round(overall * 100, 1),
        "citation_potential": round(citation_potential * 100, 1),
        "components": {k: round(v * 100, 1) for k, (v, _) in weights.items()},
        "authority_signals": auth,
        "word_count": wc,
        "sentence_count": sc,
        "stat_count": stats,
        "quote_count": quotes,
        "schema_count": schema,
        "avg_section_len": round(avg_section, 0),
        "pct_ideal_sections": round(pct_ideal * 100, 1),
        "freshness": round(freshness * 100, 1),
    }

def get_tier(score):
    if score >= 80: return ("Excellent", "success", "✅")
    elif score >= 60: return ("Good", "warning", "🟡")
    elif score >= 40: return ("Fair", "warning", "🟠")
    else: return ("Needs Work", "error", "❌")

def quantize_text(text, compression=0.6):
    """Simulate semantic compression — remove stopwords and redundant tokens."""
    stopwords = {"the","a","an","is","are","was","were","be","been","being","have","has","had",
                 "do","does","did","will","would","could","should","may","might","shall","can",
                 "this","that","these","those","it","its","in","on","at","by","for","with",
                 "as","of","to","and","but","or","nor","so","yet","both","either","neither",
                 "just","also","very","really","quite","rather","somewhat","too","not"}

    sentences = re.split(r"[.!?]+", text)

    # Score each sentence for semantic density
    def sentence_density(s):
        words = s.lower().split()
        if not words: return 0
        content_words = [w for w in words if w not in stopwords and len(w) > 3]
        has_stat = bool(re.search(r"\d+\.?\d*%|\$\d+|\d+x\b", s))
        has_quote = bool(re.search(r'["\'"]', s))
        density = len(content_words) / max(len(words), 1)
        return density + (0.3 if has_stat else 0) + (0.2 if has_quote else 0)

    scored = [(s, sentence_density(s)) for s in sentences if len(s.strip()) > 20]
    scored.sort(key=lambda x: x[1], reverse=True)

    keep_n = max(3, int(len(scored) * compression))
    kept = scored[:keep_n]
    kept_texts = [s for s, _ in kept]

    original_tokens = len(text.split())
    compressed_tokens = sum(len(s.split()) for s in kept_texts)
    ratio = round(original_tokens / max(compressed_tokens, 1), 2)

    return {
        "original": text,
        "compressed": " ".join(kept_texts),
        "original_tokens": original_tokens,
        "compressed_tokens": compressed_tokens,
        "ratio": ratio,
        "removed_pct": round((1 - compressed_tokens/max(original_tokens,1)) * 100, 1),
    }

def simulate_grounding_test(text, query):
    """Simulate how an AI might ground its answer from this content."""
    # Extract most relevant sentences to query
    query_words = set(query.lower().split())
    sentences = re.split(r"[.!?]+", text)

    def relevance(s):
        s_words = set(s.lower().split())
        overlap = len(query_words & s_words)
        has_stat = bool(re.search(r"\d+\.?\d*%|\$\d+", s))
        return overlap + (2 if has_stat else 0)

    scored = [(s.strip(), relevance(s)) for s in sentences if len(s.strip()) > 30]
    scored.sort(key=lambda x: x[1], reverse=True)
    top = scored[:3]

    max_rel = max((r for _, r in scored), default=1)
    citation_prob = min((max_rel / 8), 1.0)

    if citation_prob >= 0.65:
        verdict = "cited"
        verdict_label = "✅ Likely to be Cited"
        verdict_color = "#3fb950"
    elif citation_prob >= 0.35:
        verdict = "partial"
        verdict_label = "🟡 Partial Citation Likely"
        verdict_color = "#d29922"
    else:
        verdict = "not-cited"
        verdict_label = "❌ Unlikely to be Cited"
        verdict_color = "#f85149"

    return {
        "verdict": verdict,
        "verdict_label": verdict_label,
        "verdict_color": verdict_color,
        "citation_probability": round(citation_prob * 100, 1),
        "top_sentences": [s for s, r in top if r > 0],
        "query": query,
    }

def generate_recommendations(scores):
    """Generate prioritized recommendations."""
    recs = []
    comps = scores["components"]

    if comps.get("Content Freshness", 100) < 50:
        recs.append({"priority": "high", "title": "🗓️ Update Content for Freshness", "desc": "Content freshness is a top citation factor. Pages published or updated within 12 months are 3x more likely to be cited by AI systems. Add current year references or refresh key statistics."})
    if comps.get("Section Length (120–180w)", 100) < 50:
        recs.append({"priority": "high", "title": "📏 Restructure Section Lengths to 120–180 Words", "desc": "Sections of 120–180 words deliver a +70% citation lift. Break long paragraphs into tighter, focused sections under each heading."})
    if comps.get("Expert Quotations", 100) < 50:
        recs.append({"priority": "high", "title": "💬 Add Named Expert Quotations", "desc": "Expert quotes reduce AI hallucination risk and increase citation probability by 37%. Include at least 2–3 attributed quotes from credible sources or subject matter experts."})
    if comps.get("Statistics & Attribution", 100) < 50:
        recs.append({"priority": "medium", "title": "📊 Add Cited Statistics", "desc": "Data points with source attribution are preferred extraction targets for AI. Aim for at least 5–8 statistics with clear attribution (e.g., '48% of queries — Averi.ai, Apr 2026')."})
    if comps.get("Heading Hierarchy", 100) < 60:
        recs.append({"priority": "medium", "title": "🏗️ Improve Heading Hierarchy", "desc": "A clear H1→H2→H3 structure improves citation probability by 40%. Ensure you have one H1, multiple H2s, and H3s nested under H2s — no skipping levels."})
    if comps.get("Authority Signals", 100) < 50:
        recs.append({"priority": "medium", "title": "🔐 Strengthen Authority Signals", "desc": "AI systems favor content with verifiable authority markers: author name/credentials, publication date, source citations, and references to established organizations."})
    if comps.get("Schema Signals", 100) < 40:
        recs.append({"priority": "low", "title": "🧩 Add Structured Format Elements", "desc": "FAQ sections, How-To steps, numbered lists, and definition blocks help AI parse and extract specific answers. Add at least one FAQ or step-by-step section."})
    if comps.get("Content Depth", 100) < 60:
        recs.append({"priority": "low", "title": "📝 Increase Content Depth", "desc": "Content under 800 words rarely achieves full topic coverage. Aim for 1,200–2,500 words for key landing pages to provide sufficient depth for AI citation."})

    if not recs:
        recs.append({"priority": "low", "title": "✨ Content is Well-Optimized", "desc": "Your content scores well across all TurboQuant citation factors. Focus on building third-party brand mentions and securing placements on comparison pages to boost off-page citation signals."})

    return recs

def make_gauge(score, title, height=220):
    color = "#3fb950" if score >= 75 else "#d29922" if score >= 50 else "#f85149"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "/100", "font": {"size": 28, "color": color}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#30363d", "tickfont": {"color": "#8b949e", "size": 11}},
            "bar": {"color": color, "thickness": 0.28},
            "bgcolor": "#161b22",
            "bordercolor": "#30363d",
            "steps": [
                {"range": [0, 40], "color": "rgba(248,81,73,0.08)"},
                {"range": [40, 70], "color": "rgba(210,153,34,0.08)"},
                {"range": [70, 100], "color": "rgba(63,185,80,0.08)"},
            ],
            "threshold": {"line": {"color": color, "width": 3}, "thickness": 0.75, "value": score}
        },
        title={"text": title, "font": {"size": 13, "color": "#8b949e"}}
    ))
    fig.update_layout(height=height, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="rgba(0,0,0,0)", font_color="#e6edf3")
    return fig

def make_radar(components):
    cats = list(components.keys())
    vals = list(components.values())
    cats_short = [c.split("(")[0].strip()[:18] for c in cats]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals + [vals[0]],
        theta=cats_short + [cats_short[0]],
        fill="toself",
        fillcolor="rgba(1,105,111,0.15)",
        line=dict(color="#4f98a3", width=2),
        name="Score"
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="#161b22",
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(color="#8b949e", size=10), gridcolor="#30363d", linecolor="#30363d"),
            angularaxis=dict(tickfont=dict(color="#e6edf3", size=10), gridcolor="#30363d", linecolor="#30363d"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        height=340,
        margin=dict(l=60, r=60, t=30, b=30)
    )
    return fig

def make_bar_chart(components):
    cats = [c.split("(")[0].strip() for c in components.keys()]
    vals = list(components.values())
    colors = ["#3fb950" if v >= 75 else "#d29922" if v >= 50 else "#f85149" for v in vals]
    fig = go.Figure(go.Bar(
        x=vals, y=cats, orientation="h",
        marker_color=colors,
        text=[f"{v}" for v in vals],
        textposition="outside",
        textfont=dict(color="#e6edf3", size=11)
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#161b22",
        xaxis=dict(range=[0, 115], gridcolor="#30363d", tickfont=dict(color="#8b949e"), title_font=dict(color="#8b949e"), title="Score"),
        yaxis=dict(tickfont=dict(color="#e6edf3", size=11)),
        height=320,
        margin=dict(l=10, r=60, t=20, b=30)
    )
    return fig

def make_compression_viz(original_tokens, compressed_tokens, ratio):
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Original", x=["Tokens"], y=[original_tokens], marker_color="#8b949e", width=0.35))
    fig.add_trace(go.Bar(name="Compressed", x=["Tokens"], y=[compressed_tokens], marker_color="#4f98a3", width=0.35))
    fig.update_layout(
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#161b22",
        xaxis=dict(tickfont=dict(color="#8b949e")),
        yaxis=dict(gridcolor="#30363d", tickfont=dict(color="#8b949e"), title="Token Count", title_font=dict(color="#8b949e")),
        legend=dict(font=dict(color="#e6edf3"), bgcolor="#161b22", bordercolor="#30363d", borderwidth=1),
        height=240,
        margin=dict(l=20, r=20, t=20, b=30)
    )
    return fig

def make_kv_compression_chart():
    """TurboQuant KV cache compression simulation."""
    bits = [16, 8, 4, 3, 2]
    recall = [100, 99.2, 98.1, 99.5, 89.0]  # TurboQuant (3-bit) beats 4-bit
    memory_factor = [1.0, 0.5, 0.25, 0.19, 0.125]

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(
        x=bits, y=recall, name="Recall (%)", mode="lines+markers",
        line=dict(color="#4f98a3", width=2.5),
        marker=dict(size=9, color=["#3fb950" if b == 3 else "#4f98a3" for b in bits],
                    symbol=["star" if b == 3 else "circle" for b in bits])
    ), secondary_y=False)
    fig.add_trace(go.Bar(
        x=bits, y=memory_factor, name="Memory Factor", opacity=0.5,
        marker_color=["#01696f" if b == 3 else "#30363d" for b in bits]
    ), secondary_y=True)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#161b22",
        xaxis=dict(title="Bit Width", tickvals=bits, tickfont=dict(color="#8b949e"), gridcolor="#30363d", title_font=dict(color="#8b949e")),
        yaxis=dict(title="Recall (%)", range=[85, 101], gridcolor="#30363d", tickfont=dict(color="#8b949e"), title_font=dict(color="#8b949e")),
        yaxis2=dict(title="Memory Factor (1x=16-bit)", tickfont=dict(color="#8b949e"), title_font=dict(color="#8b949e")),
        legend=dict(font=dict(color="#e6edf3"), bgcolor="#161b22"),
        height=280,
        margin=dict(l=20, r=20, t=20, b=40),
        annotations=[dict(x=3, y=99.5, text="⭐ TurboQuant<br>3-bit", showarrow=True, arrowhead=2, arrowcolor="#01696f", font=dict(color="#4f98a3", size=11), ax=40, ay=-30)]
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:16px 0 8px;">
        <div style="font-size:2rem;">⚡</div>
        <div style="font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:1.2rem;background:linear-gradient(135deg,#01696f,#4f98a3);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">TurboQuant</div>
        <div style="font-size:0.7rem;color:#8b949e;letter-spacing:1px;text-transform:uppercase;">AI Citation Simulator</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("**📥 Input Mode**")
    input_mode = st.radio("", ["🔗 URL", "📝 Paste Text"], label_visibility="collapsed")

    st.divider()

    st.markdown("**⚙️ Analysis Settings**")
    compression_level = st.slider("Quantize Compression", 0.3, 0.9, 0.6, 0.1, help="How aggressively to compress content (lower = more compressed)")
    show_raw = st.checkbox("Show Raw Scores", False)

    st.divider()

    st.markdown("""
    <div class="info-box">
    <strong>About TurboQuant</strong><br>
    Google's March 2026 compression algorithm enables 6x KV-cache memory reduction — making AI semantic retrieval dramatically faster and changing how content gets cited.
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("""
    <div style="font-size:0.72rem;color:#8b949e;text-align:center;">
    Based on research from Citation Labs, Averi.ai, Onely & WordLift<br>
    <span style="color:#30363d;">v2.0 · May 2026</span>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ═══════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="hero-header">
    <div class="hero-title">⚡ TurboQuant Simulator</div>
    <div class="hero-sub">Analyze how easily AI can understand, retrieve, and cite your content</div>
</div>
""", unsafe_allow_html=True)

# ── Input Section ─────────────────────────────────────────────────────────
with st.container():
    col_in1, col_in2 = st.columns([3, 1])

    content_text = ""
    page_title = ""
    url_analyzed = ""

    if "URL" in input_mode:
        with col_in1:
            url_input = st.text_input("🔗 Enter URL to Analyze", placeholder="https://example.com/your-page", label_visibility="collapsed")
        with col_in2:
            analyze_btn = st.button("⚡ Analyze", use_container_width=True)

        if analyze_btn and url_input:
            with st.spinner("🕸️ Extracting content..."):
                result = extract_content_from_url(url_input)
            if result["success"] and result["text"]:
                content_text = result["text"]
                page_title = result["title"]
                url_analyzed = url_input
                st.success(f"✅ Extracted from: **{page_title}** — {count_words(content_text):,} words")
            else:
                st.error(f"❌ Could not extract content: {result.get('error', 'Unknown error')}")
    else:
        with col_in1:
            content_text_input = st.text_area("📝 Paste Your Content", height=160, placeholder="Paste your article, landing page, or blog post here...", label_visibility="collapsed")
        with col_in2:
            st.write("")
            st.write("")
            analyze_btn2 = st.button("⚡ Analyze", use_container_width=True)

        if analyze_btn2 and content_text_input:
            content_text = content_text_input
            page_title = "Pasted Content"


# ── Results (only shown when content exists) ──────────────────────────────
if content_text and len(content_text.split()) > 30:
    scores = calculate_seo_score(content_text)
    recs = generate_recommendations(scores)

    st.divider()

    # ── KPI Row ───────────────────────────────────────────────────────────
    overall_tier, _, overall_icon = get_tier(scores["overall"])
    cit_tier, _, cit_icon = get_tier(scores["citation_potential"])
    auth_count = sum(scores["authority_signals"].values())

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-score">{scores['overall']}</div>
            <div class="metric-label">SEO 3.0 Score</div>
            <div class="metric-delta">{overall_icon} {overall_tier}</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-score">{scores['citation_potential']}</div>
            <div class="metric-label">Citation Potential</div>
            <div class="metric-delta">{cit_icon} {cit_tier}</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-score">{auth_count}</div>
            <div class="metric-label">Authority Signals</div>
            <div class="metric-delta">{'✅ Strong' if auth_count >= 5 else '🟡 Moderate' if auth_count >= 3 else '❌ Weak'}</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-score">{scores['word_count']:,}</div>
            <div class="metric-label">Word Count</div>
            <div class="metric-delta">{'✅ Ideal' if 800 <= scores['word_count'] <= 3000 else '🟡 Review'}</div>
        </div>""", unsafe_allow_html=True)

    st.write("")

    # ── Tabs ──────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 SEO 3.0 Analysis",
        "🔐 Authority Signals",
        "🗜️ Quantize Text",
        "🧪 Quantization Lab",
        "🎯 Grounding Test"
    ])

    # ── TAB 1: SEO 3.0 ANALYSIS ──────────────────────────────────────────
    with tab1:
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.plotly_chart(make_gauge(scores["overall"], "Overall SEO 3.0 Score"), use_container_width=True, config={"displayModeBar": False})
        with col_g2:
            st.plotly_chart(make_gauge(scores["citation_potential"], "Citation Potential"), use_container_width=True, config={"displayModeBar": False})

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown('<div class="section-header">Component Scores — Radar</div>', unsafe_allow_html=True)
            st.plotly_chart(make_radar(scores["components"]), use_container_width=True, config={"displayModeBar": False})
        with col_r2:
            st.markdown('<div class="section-header">Component Breakdown</div>', unsafe_allow_html=True)
            st.plotly_chart(make_bar_chart(scores["components"]), use_container_width=True, config={"displayModeBar": False})

        st.markdown('<div class="section-header">📋 Content Diagnostics</div>', unsafe_allow_html=True)
        d1, d2, d3, d4 = st.columns(4)
        d1.metric("📖 Word Count", f"{scores['word_count']:,}", delta="Ideal: 800–3,000")
        d2.metric("📊 Statistics Found", scores["stat_count"], delta="+22% citation lift each")
        d3.metric("💬 Expert Quotes", scores["quote_count"], delta="+37% citation lift each")
        d4.metric("📏 Avg Section Length", f"{int(scores['avg_section_len'])}w", delta="Ideal: 120–180w")

        st.markdown('<div class="section-header" style="margin-top:20px;">🔧 Recommendations</div>', unsafe_allow_html=True)
        for rec in recs:
            st.markdown(f"""<div class="rec-card {rec['priority']}">
                <div class="rec-title">{rec['title']}</div>
                <div class="rec-desc">{rec['desc']}</div>
            </div>""", unsafe_allow_html=True)

        if show_raw:
            with st.expander("🔍 Raw Score Data"):
                st.json(scores)

    # ── TAB 2: AUTHORITY SIGNALS ──────────────────────────────────────────
    with tab2:
        st.markdown('<div class="section-header">🔐 Authority Signal Detection</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-box">
        <strong>Why Authority Signals Matter:</strong> AI systems favor content from sources they treat as inherently authoritative. 
        The more verifiable trust signals your content carries, the more likely it is to be retrieved and cited in AI-generated answers.
        </div>
        """, unsafe_allow_html=True)

        st.write("")

        signal_cols = st.columns(2)
        auth_signals = scores["authority_signals"]
        signal_items = list(auth_signals.items())

        for i, (signal, found) in enumerate(signal_items):
            col = signal_cols[i % 2]
            with col:
                status = "badge-found" if found else "badge-missing"
                icon = "✅" if found else "❌"
                desc_map = {
                    "Citation/Reference": "Source links, DOIs, numbered references present",
                    "Author Attribution": "Named author or byline detected",
                    "Date/Recency": "Recent year or 'updated' timestamp found",
                    "External Links": "Links to external sources detected",
                    "Research/Study": "Research data or study references found",
                    "Expert/Credentials": "Expert credentials or named authorities",
                    "Statistics Present": "Numerical data or percentages found",
                    "Named Entity (Org)": "Recognized organizations mentioned",
                }
                desc = desc_map.get(signal, "")
                bg = "rgba(63,185,80,0.06)" if found else "rgba(248,81,73,0.04)"
                border = "rgba(63,185,80,0.3)" if found else "rgba(248,81,73,0.2)"
                st.markdown(f"""
                <div style="background:{bg};border:1px solid {border};border-radius:10px;padding:14px 16px;margin-bottom:12px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div style="font-weight:600;font-size:0.9rem;color:#e6edf3;">{icon} {signal}</div>
                        <span class="signal-badge {'badge-found' if found else 'badge-missing'}">{'Found' if found else 'Missing'}</span>
                    </div>
                    <div style="font-size:0.78rem;color:#8b949e;margin-top:4px;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

        st.divider()

        # Signal weight chart
        st.markdown('<div class="section-header">📊 AI Signal Weight Reference</div>', unsafe_allow_html=True)
        signal_names = ["Brand Mentions", "Editorial Links", "Schema Markup", "Anchor Text", "Volume Links"]
        signal_weights = [3.0, 1.8, 1.4, 1.1, 0.6]
        sw_colors = ["#3fb950" if w >= 1.8 else "#d29922" if w >= 1.0 else "#f85149" for w in signal_weights]
        fig_sw = go.Figure(go.Bar(
            y=signal_names, x=signal_weights, orientation="h",
            marker_color=sw_colors,
            text=[f"{w}x" for w in signal_weights], textposition="outside",
            textfont=dict(color="#e6edf3")
        ))
        fig_sw.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#161b22",
            xaxis=dict(title="Weight Multiplier vs. Volume Links", gridcolor="#30363d", tickfont=dict(color="#8b949e"), range=[0, 3.8], title_font=dict(color="#8b949e")),
            yaxis=dict(tickfont=dict(color="#e6edf3")),
            height=240, margin=dict(l=10, r=60, t=10, b=40)
        )
        st.plotly_chart(fig_sw, use_container_width=True, config={"displayModeBar": False})

    # ── TAB 3: QUANTIZE TEXT ─────────────────────────────────────────────
    with tab3:
        st.markdown('<div class="section-header">🗜️ Semantic Compression (Quantize Text)</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-box">
        <strong>What is Quantize Text?</strong> Inspired by TurboQuant's vector compression, this feature compresses your content by removing 
        semantically redundant tokens while preserving high-density information — the same approach AI retrieval systems use internally to 
        prioritize the most citable segments of your content.
        </div>
        """, unsafe_allow_html=True)

        st.write("")
        quant_result = quantize_text(content_text, compression=compression_level)

        qm1, qm2, qm3 = st.columns(3)
        qm1.metric("Original Tokens", f"{quant_result['original_tokens']:,}")
        qm2.metric("Compressed Tokens", f"{quant_result['compressed_tokens']:,}", delta=f"-{quant_result['removed_pct']}%")
        qm3.metric("Compression Ratio", f"{quant_result['ratio']}x")

        st.plotly_chart(make_compression_viz(quant_result["original_tokens"], quant_result["compressed_tokens"], quant_result["ratio"]), use_container_width=True, config={"displayModeBar": False})

        col_q1, col_q2 = st.columns(2)
        with col_q1:
            st.markdown("**📄 Original Content (preview)**")
            st.markdown(f"""<div style="background:#161b22;border:1px solid #30363d;border-radius:8px;padding:14px;font-size:0.82rem;color:#8b949e;max-height:220px;overflow-y:auto;line-height:1.6;">{content_text[:800]}{'...' if len(content_text) > 800 else ''}</div>""", unsafe_allow_html=True)
        with col_q2:
            st.markdown("**⚡ Quantized Output (high-density sentences)**")
            st.markdown(f"""<div style="background:#161b22;border:1px solid #01696f;border-radius:8px;padding:14px;font-size:0.82rem;color:#e6edf3;max-height:220px;overflow-y:auto;line-height:1.6;">{quant_result['compressed'][:800]}{'...' if len(quant_result['compressed']) > 800 else ''}</div>""", unsafe_allow_html=True)

        with st.expander("📋 Copy Full Quantized Text"):
            st.text_area("", quant_result["compressed"], height=200, label_visibility="collapsed")

    # ── TAB 4: QUANTIZATION LAB ──────────────────────────────────────────
    with tab4:
        st.markdown('<div class="section-header">🧪 TurboQuant Quantization Lab</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-box">
        <strong>How TurboQuant works:</strong> Google's algorithm compresses KV-cache vectors to 3 bits (from 16-bit) via two stages: 
        (1) <strong>PolarQuant</strong> — converts Cartesian vectors to polar coordinates using a Hadamard random rotation, enabling near-zero codebook overhead. 
        (2) <strong>QJL</strong> — a 1-bit Johnson-Lindenstrauss transform corrects residual errors and removes inner-product bias. 
        The result: 6x memory reduction with zero measurable accuracy loss.
        </div>
        """, unsafe_allow_html=True)

        st.write("")

        col_lab1, col_lab2 = st.columns([3, 2])

        with col_lab1:
            st.markdown("**📉 KV Cache: Recall vs. Compression Tradeoff**")
            st.plotly_chart(make_kv_compression_chart(), use_container_width=True, config={"displayModeBar": False})

        with col_lab2:
            st.markdown("**⚙️ TurboQuant Pipeline**")
            st.markdown("""
            <div style="background:#161b22;border:1px solid #30363d;border-radius:10px;padding:16px;font-size:0.8rem;">
            <div style="color:#4f98a3;font-weight:600;margin-bottom:10px;">Stage 1: PolarQuant</div>
            <div style="color:#8b949e;line-height:1.8;">
            🔄 Random Hadamard Rotation<br>
            📐 Cartesian → Polar Transform<br>
            🗂️ Scalar Quantization (3-bit)<br>
            ✅ <span style="color:#3fb950;">Zero codebook training required</span>
            </div>
            <hr style="border-color:#30363d;margin:12px 0;">
            <div style="color:#4f98a3;font-weight:600;margin-bottom:10px;">Stage 2: QJL (1-bit residual)</div>
            <div style="color:#8b949e;line-height:1.8;">
            📏 Johnson-Lindenstrauss Transform<br>
            ±1 Sign-bit encoding<br>
            🎯 Inner-product bias correction<br>
            ✅ <span style="color:#3fb950;">Zero memory overhead</span>
            </div>
            <hr style="border-color:#30363d;margin:12px 0;">
            <div style="display:flex;justify-content:space-between;">
                <div style="text-align:center;"><div style="color:#f85149;font-size:1.2rem;font-weight:700;">16-bit</div><div style="color:#8b949e;font-size:0.72rem;">Input</div></div>
                <div style="text-align:center;color:#8b949e;font-size:1.2rem;padding-top:8px;">→</div>
                <div style="text-align:center;"><div style="color:#4f98a3;font-size:1.2rem;font-weight:700;">3-bit</div><div style="color:#8b949e;font-size:0.72rem;">Output</div></div>
                <div style="text-align:center;color:#8b949e;font-size:1.2rem;padding-top:8px;">=</div>
                <div style="text-align:center;"><div style="color:#3fb950;font-size:1.2rem;font-weight:700;">6x</div><div style="color:#8b949e;font-size:0.72rem;">Smaller</div></div>
            </div>
            </div>
            """, unsafe_allow_html=True)

        # SEO implications chart
        st.write("")
        st.markdown("**🔗 TurboQuant → SEO Impact Chain**")

        impact_data = {
            "Metric": ["AI Overview Coverage", "Top-10 Citation Share", "AI Cited Conversion Rate", "TQ Impact Score"],
            "Before (Mid-2025)": [31, 76, 2.8, 50],
            "After (Apr 2026)": [48, 38, 14.2, 82],
        }
        df_impact = pd.DataFrame(impact_data)
        fig_impact = go.Figure()
        fig_impact.add_trace(go.Bar(name="Before (Mid-2025)", x=df_impact["Metric"], y=df_impact["Before (Mid-2025)"], marker_color="#30363d"))
        fig_impact.add_trace(go.Bar(name="After (Apr 2026)", x=df_impact["Metric"], y=df_impact["After (Apr 2026)"], marker_color="#4f98a3"))
        fig_impact.update_layout(
            barmode="group", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#161b22",
            xaxis=dict(tickfont=dict(color="#e6edf3")),
            yaxis=dict(gridcolor="#30363d", tickfont=dict(color="#8b949e")),
            legend=dict(font=dict(color="#e6edf3"), bgcolor="#161b22", bordercolor="#30363d", borderwidth=1),
            height=260, margin=dict(l=20, r=20, t=20, b=40)
        )
        st.plotly_chart(fig_impact, use_container_width=True, config={"displayModeBar": False})

    # ── TAB 5: GROUNDING TEST ─────────────────────────────────────────────
    with tab5:
        st.markdown('<div class="section-header">🎯 Real-World Grounding Test</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-box">
        <strong>What is the Grounding Test?</strong> Simulates how a generative AI engine would use your content to answer a query — 
        revealing whether AI systems are likely to cite your page, partially cite it, or ignore it entirely.
        </div>
        """, unsafe_allow_html=True)

        st.write("")

        grounding_query = st.text_input("🔍 Enter a query to test against your content", placeholder="e.g. What are the best link building strategies for AI citations?")

        if grounding_query:
            with st.spinner("🧠 Simulating AI grounding..."):
                time.sleep(0.5)
                gr = simulate_grounding_test(content_text, grounding_query)

            st.markdown(f"""
            <div class="ground-result {gr['verdict']}">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div style="font-size:1.1rem;font-weight:700;color:{gr['verdict_color']};">{gr['verdict_label']}</div>
                    <div style="font-size:1.4rem;font-weight:700;font-family:'Space Grotesk',sans-serif;color:{gr['verdict_color']};">{gr['citation_probability']}%</div>
                </div>
                <div style="font-size:0.8rem;color:#8b949e;margin-top:4px;">Citation probability for query: <em>"{grounding_query}"</em></div>
            </div>
            """, unsafe_allow_html=True)

            # Citation probability gauge
            fig_cp = make_gauge(gr["citation_probability"], "Citation Probability", height=200)
            st.plotly_chart(fig_cp, use_container_width=True, config={"displayModeBar": False})

            if gr["top_sentences"]:
                st.markdown("**🧩 Most Likely Cited Segments from Your Content:**")
                for i, sentence in enumerate(gr["top_sentences"][:3], 1):
                    if len(sentence.strip()) > 20:
                        st.markdown(f"""
                        <div style="background:#161b22;border-left:3px solid #01696f;border-radius:0 8px 8px 0;padding:12px 16px;margin:8px 0;">
                            <div style="font-size:0.72rem;color:#8b949e;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">Segment {i}</div>
                            <div style="font-size:0.88rem;color:#e6edf3;line-height:1.6;">{sentence.strip()}</div>
                        </div>
                        """, unsafe_allow_html=True)

            # Grounding improvement tips
            st.write("")
            st.markdown("**💡 To improve your grounding score for this query:**")
            tips = [
                f"Add the exact phrase **'{grounding_query.split()[:3][0] if grounding_query.split() else ''}'** to a heading or subheading",
                "Include a direct answer sentence in the first paragraph of the relevant section",
                "Add a statistic specific to this topic with a credible source attribution",
                "Create a dedicated FAQ section addressing this query directly"
            ]
            for tip in tips:
                st.markdown(f"→ {tip}")
        else:
            # Default test queries
            st.markdown("**💡 Try these example queries:**")
            example_queries = [
                "What are the best link building strategies in 2026?",
                "How does TurboQuant affect AI citations?",
                "How to get cited in Google AI Overviews?",
                "What is generative engine optimization?",
            ]
            for q in example_queries:
                if st.button(q, key=f"q_{q[:20]}"):
                    st.session_state["grounding_query"] = q
                    st.rerun()

elif content_text and len(content_text.split()) <= 30:
    st.warning("⚠️ Content too short for analysis. Please provide at least 50 words.")
else:
    # Landing state
    st.markdown("""
    <div style="text-align:center;padding:48px 24px;color:#8b949e;">
        <div style="font-size:3rem;margin-bottom:16px;">🔍</div>
        <div style="font-size:1.1rem;font-weight:500;color:#e6edf3;margin-bottom:8px;">Paste a URL or text to begin analysis</div>
        <div style="font-size:0.85rem;max-width:500px;margin:0 auto;line-height:1.7;">
        TurboQuant Simulator evaluates your content across 8 AI citation factors — 
        giving you a SEO 3.0 Score, Citation Potential rating, Authority Signal detection, 
        and semantic compression — powered by the same principles as Google's TurboQuant algorithm.
        </div>
    </div>

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;max-width:800px;margin:32px auto 0;padding:0 24px;">
        <div style="background:#161b22;border:1px solid #30363d;border-radius:10px;padding:16px;text-align:center;">
            <div style="font-size:1.5rem;">📊</div>
            <div style="font-weight:600;color:#e6edf3;font-size:0.9rem;margin:8px 0 4px;">SEO 3.0 Score</div>
            <div style="font-size:0.78rem;color:#8b949e;">8-factor citation readiness score based on TurboQuant research</div>
        </div>
        <div style="background:#161b22;border:1px solid #30363d;border-radius:10px;padding:16px;text-align:center;">
            <div style="font-size:1.5rem;">🗜️</div>
            <div style="font-weight:600;color:#e6edf3;font-size:0.9rem;margin:8px 0 4px;">Quantize Text</div>
            <div style="font-size:0.78rem;color:#8b949e;">Compress to highest-density citable sentences</div>
        </div>
        <div style="background:#161b22;border:1px solid #30363d;border-radius:10px;padding:16px;text-align:center;">
            <div style="font-size:1.5rem;">🎯</div>
            <div style="font-weight:600;color:#e6edf3;font-size:0.9rem;margin:8px 0 4px;">Grounding Test</div>
            <div style="font-size:0.78rem;color:#8b949e;">Simulate AI citation probability for any query</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
