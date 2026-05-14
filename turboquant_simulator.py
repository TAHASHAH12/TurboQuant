
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
from collections import Counter

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TurboQuant Simulator v2 — AI Citation Intelligence",
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

/* v2 NEW: Comparison table */
.compare-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.compare-table th { background: var(--surface-2); color: var(--primary-light); padding: 10px 14px; text-align: left; border-bottom: 2px solid var(--primary); font-weight: 600; }
.compare-table td { padding: 10px 14px; border-bottom: 1px solid var(--border); color: var(--text); }
.compare-table tr:hover td { background: rgba(1,105,111,0.04); }

/* v2 NEW: Keyword density bars */
.kw-bar-wrap { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.kw-label { font-size: 0.78rem; color: var(--text); width: 140px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-family: monospace; }
.kw-bar { flex: 1; height: 6px; background: var(--border); border-radius: 99px; overflow: hidden; }
.kw-fill { height: 100%; background: linear-gradient(90deg, #01696f, #4f98a3); border-radius: 99px; }
.kw-count { font-size: 0.75rem; color: var(--muted); width: 30px; text-align: right; }

/* v2 NEW: Badge pill */
.badge-pill { display: inline-block; padding: 3px 10px; border-radius: 99px; font-size: 0.72rem; font-weight: 600; letter-spacing: 0.5px; }
.badge-new { background: rgba(14,165,233,0.15); color: #0ea5e9; border: 1px solid rgba(14,165,233,0.3); }
.badge-v2 { background: rgba(1,105,111,0.2); color: #4f98a3; border: 1px solid rgba(1,105,111,0.4); }

/* v2 NEW: Entity chips */
.entity-chip { display: inline-block; padding: 4px 10px; border-radius: 16px; font-size: 0.78rem; font-weight: 500; margin: 3px 2px; }
.entity-covered { background: rgba(63,185,80,0.15); color: #3fb950; border: 1px solid rgba(63,185,80,0.35); }
.entity-missing { background: rgba(248,81,73,0.12); color: #f85149; border: 1px solid rgba(248,81,73,0.3); }
.entity-partial { background: rgba(210,153,34,0.12); color: #d29922; border: 1px solid rgba(210,153,34,0.3); }

/* v2 NEW: SERP cards */
.serp-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 16px 20px; margin-bottom: 12px; transition: all 0.2s; }
.serp-card:hover { border-color: var(--primary-light); }
.serp-rank { display: inline-block; width: 28px; height: 28px; border-radius: 50%; background: var(--primary); color: white; text-align: center; line-height: 28px; font-size: 0.75rem; font-weight: 700; margin-right: 10px; }
.serp-rank.top3 { background: linear-gradient(135deg, #d29922, #f5c842); color: #0f1117; }
.serp-title { font-weight: 600; font-size: 0.95rem; color: #e6edf3; }
.serp-url { font-size: 0.75rem; color: #8b949e; margin-top: 2px; }

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


# ── v2 NEW: Readability (Flesch-Kincaid) ─────────────────────────────────────
def calculate_readability(text):
    """Flesch Reading Ease score."""
    words = text.split()
    sentences = re.findall(r"[.!?]+", text)
    if not sentences or not words:
        return 50, "Average"
    syllables = sum(max(1, len(re.findall(r"[aeiouAEIOU]", w))) for w in words)
    asl = len(words) / max(len(sentences), 1)
    asw = syllables / max(len(words), 1)
    score = 206.835 - (1.015 * asl) - (84.6 * asw)
    score = max(0, min(100, round(score, 1)))
    if score >= 80:
        grade = "Very Easy"
    elif score >= 70:
        grade = "Easy"
    elif score >= 60:
        grade = "Standard"
    elif score >= 50:
        grade = "Fairly Difficult"
    elif score >= 30:
        grade = "Difficult"
    else:
        grade = "Very Difficult"
    return score, grade


# ── v2 NEW: Keyword density analysis ─────────────────────────────────────────
def keyword_density(text, top_n=15):
    stopwords = {"the","a","an","is","are","was","were","be","been","being","have","has","had",
                 "do","does","did","will","would","could","should","may","might","shall","can",
                 "this","that","these","those","it","its","in","on","at","by","for","with",
                 "as","of","to","and","but","or","nor","so","yet","both","either","neither",
                 "just","also","very","really","quite","rather","somewhat","too","not","i",
                 "we","you","he","she","they","them","their","our","my","your","his","her",
                 "from","into","about","which","who","what","when","where","how","than","if","then"}
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    filtered = [w for w in words if w not in stopwords]
    total = len(filtered)
    counts = Counter(filtered).most_common(top_n)
    return [(w, c, round(c / max(total, 1) * 100, 2)) for w, c in counts], total


# ── v2 NEW: Sentence variety analysis ────────────────────────────────────────
def sentence_variety(text):
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    if not sentences:
        return {"short": 0, "medium": 0, "long": 0, "very_long": 0, "avg_len": 0, "total": 0}
    lengths = [len(s.split()) for s in sentences]
    return {
        "short": sum(1 for l in lengths if l <= 10),
        "medium": sum(1 for l in lengths if 11 <= l <= 20),
        "long": sum(1 for l in lengths if 21 <= l <= 35),
        "very_long": sum(1 for l in lengths if l > 35),
        "avg_len": round(sum(lengths) / len(lengths), 1),
        "total": len(lengths)
    }


# ── v2 NEW: Simple entity extraction ─────────────────────────────────────────
def extract_entities(text):
    """Simple rule-based named entity detection."""
    orgs = list(set(re.findall(
        r"\b(Google|Microsoft|OpenAI|Meta|Apple|Amazon|Nvidia|Anthropic|Perplexity|Gemini|"
        r"ChatGPT|Bing|Harvard|Stanford|MIT|McKinsey|Gartner|Forrester|HubSpot|Ahrefs|"
        r"Semrush|Moz|BrightEdge|Conductor|Salesforce|Adobe|IBM|Oracle)\b", text)))
    years = list(set(re.findall(r"\b(20[12][0-9])\b", text)))
    percentages = re.findall(r"\d+\.?\d*\s*%", text)[:8]
    people = list(set(re.findall(r"\b([A-Z][a-z]+ [A-Z][a-z]+)\b", text)))[:6]
    return {"orgs": orgs, "years": years, "percentages": percentages, "people": people}


# ── v2 NEW: Multi-URL comparison scorer ──────────────────────────────────────
def score_multiple_urls(urls):
    results = []
    for url in urls:
        if not url.strip():
            continue
        data = extract_content_from_url(url.strip())
        if data["success"] and data["text"]:
            score_data = calculate_seo_score(data["text"], data.get("headings", []))
            results.append({
                "url": url.strip(),
                "title": data["title"][:60],
                "overall": score_data["overall"],
                "citation_potential": score_data["citation_potential"],
                "word_count": score_data["word_count"],
                "freshness": score_data["freshness"],
                "components": score_data["components"],
            })
        else:
            results.append({
                "url": url.strip(),
                "title": "Failed to fetch",
                "overall": 0,
                "citation_potential": 0,
                "word_count": 0,
                "freshness": 0,
                "components": {},
            })
    return results


# ── v2 NEW: Content gap analysis ─────────────────────────────────────────────
def content_gap_analysis(text, target_keywords):
    """Check which target keywords are present/missing in content."""
    text_lower = text.lower()
    results = []
    for kw in target_keywords:
        kw = kw.strip().lower()
        if not kw:
            continue
        count = len(re.findall(r"\b" + re.escape(kw) + r"\b", text_lower))
        density = round(count / max(len(text.split()), 1) * 100, 2)
        if count == 0:
            status = "missing"
        elif density < 0.3:
            status = "low"
        elif density > 3.0:
            status = "over"
        else:
            status = "optimal"
        results.append({"keyword": kw, "count": count, "density": density, "status": status})
    return results

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
# ENTITY EXTRACTION + GRAPH (v3 NEW)
# ═══════════════════════════════════════════════════════════════════════════

ENTITY_PATTERNS = {
    "Organizations": [
        r"\b(Google|Microsoft|OpenAI|Meta|Apple|Amazon|Nvidia|Anthropic|Perplexity|Gemini|ChatGPT|Bing|"
        r"Harvard|Stanford|MIT|McKinsey|Gartner|Forrester|HubSpot|Ahrefs|Semrush|Moz|BrightEdge|"
        r"Conductor|Salesforce|Adobe|IBM|Oracle|Netflix|Spotify|Uber|Airbnb|Twitter|LinkedIn|"
        r"Facebook|Instagram|YouTube|TikTok|Wikipedia|Reuters|Bloomberg|Forbes|BBC|CNN|NYT)\b"
    ],
    "Technologies": [
        r"\b(AI|GPT-?[0-9]?|LLM|RAG|KV.?[Cc]ache|NLP|ML|deep.?learning|neural.?network|"
        r"transformer|BERT|embedding|vector|semantic.?search|TurboQuant|SEO|SEM|SERP|"
        r"schema\.org|JSON-LD|structured.?data|PageRank|algorithm|Python|JavaScript|API|"
        r"blockchain|cloud|SaaS|CMS|WordPress|Shopify|Wikidata|knowledge.?graph)\b"
    ],
    "Concepts": [
        r"\b(citation|authority|E-E-A-T|trustworthiness|relevance|freshness|entity|"
        r"knowledge.?graph|semantic|ontology|taxonomy|topic.?cluster|pillar.?page|"
        r"content.?gap|link.?building|backlink|anchor.?text|domain.?authority|"
        r"page.?rank|indexing|crawling|rendering|Core.?Web.?Vitals|UX|CRO)\b"
    ],
    "People": [
        r"\b([A-Z][a-z]{2,}\s[A-Z][a-z]{2,})\b"
    ],
    "Years": [r"\b(20[1-2][0-9])\b"],
    "Statistics": [r"\d+\.?\d*\s*%|\$\d+[\d,]*(?:\s*(?:million|billion|M|B))?|\d+x\b"],
}

def extract_entities_advanced(text):
    """Extract rich named entities with categories and frequency."""
    entities = {}
    for category, patterns in ENTITY_PATTERNS.items():
        found = []
        for pat in patterns:
            matches = re.findall(pat, text, re.IGNORECASE if category != "People" else 0)
            found.extend([m if isinstance(m, str) else m[0] for m in matches])
        # Deduplicate and count
        counter = Counter(found)
        if category == "People":
            # Filter out common false positives
            skip = {"The The","In The","Of The","On The","At The","By The","From The","With The"}
            counter = Counter({k: v for k, v in counter.items() if k not in skip and len(k) > 5})
        entities[category] = dict(counter.most_common(15))
    return entities

def build_entity_cooccurrence(text, entities):
    """Build co-occurrence matrix for entities appearing in same sentences."""
    sentences = re.split(r"[.!?\n]+", text)
    # Flatten all entity names
    all_ents = []
    for cat, ent_dict in entities.items():
        if cat not in ("Years", "Statistics"):
            all_ents.extend(list(ent_dict.keys())[:8])

    cooccurrence = {}
    for ent1 in all_ents:
        for ent2 in all_ents:
            if ent1 >= ent2:
                continue
            count = sum(1 for s in sentences if ent1.lower() in s.lower() and ent2.lower() in s.lower())
            if count > 0:
                key = (ent1, ent2)
                cooccurrence[key] = count
    return cooccurrence

def make_entity_graph_chart(entities, cooccurrence, title="Entity Graph"):
    """Build a network-style scatter chart showing entity relationships."""
    import math, random
    all_nodes = []
    category_colors = {
        "Organizations": "#4f98a3",
        "Technologies": "#d29922",
        "Concepts": "#3fb950",
        "People": "#f85149",
    }
    # Build node list
    for cat, ent_dict in entities.items():
        if cat in ("Years", "Statistics"):
            continue
        color = category_colors.get(cat, "#8b949e")
        for name, freq in list(ent_dict.items())[:8]:
            all_nodes.append({"name": name, "cat": cat, "freq": freq, "color": color})

    if not all_nodes:
        return None

    # Place nodes in a circle, ordered by category
    n = len(all_nodes)
    node_x, node_y = [], []
    for i, node in enumerate(all_nodes):
        angle = 2 * math.pi * i / n
        r = 1 + node["freq"] * 0.05
        node_x.append(r * math.cos(angle))
        node_y.append(r * math.sin(angle))

    node_map = {node["name"]: (node_x[i], node_y[i]) for i, node in enumerate(all_nodes)}

    fig = go.Figure()

    # Draw edges
    for (e1, e2), weight in cooccurrence.items():
        if e1 in node_map and e2 in node_map:
            x1, y1 = node_map[e1]
            x2, y2 = node_map[e2]
            fig.add_trace(go.Scatter(
                x=[x1, x2, None], y=[y1, y2, None],
                mode="lines",
                line=dict(color=f"rgba(79,152,163,{min(0.1+weight*0.1,0.6)})", width=weight*0.5+0.5),
                hoverinfo="none", showlegend=False
            ))

    # Draw nodes by category
    for cat in category_colors:
        cat_nodes = [(i, n) for i, n in enumerate(all_nodes) if n["cat"] == cat]
        if not cat_nodes:
            continue
        fig.add_trace(go.Scatter(
            x=[node_x[i] for i, _ in cat_nodes],
            y=[node_y[i] for i, _ in cat_nodes],
            mode="markers+text",
            name=cat,
            marker=dict(
                size=[min(8 + n["freq"] * 3, 32) for _, n in cat_nodes],
                color=category_colors[cat],
                opacity=0.85,
                line=dict(color="#161b22", width=1.5)
            ),
            text=[n["name"] for _, n in cat_nodes],
            textposition="top center",
            textfont=dict(size=9, color="#e6edf3"),
            hovertemplate="<b>%{text}</b><br>Category: " + cat + "<extra></extra>"
        ))

    fig.update_layout(
        title=dict(text=title, font=dict(color="#e6edf3", size=14)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#161b22",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=500,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(font=dict(color="#e6edf3"), bgcolor="#161b22", bordercolor="#30363d", borderwidth=1),
        showlegend=True
    )
    return fig

def make_entity_coverage_chart(entities_list, labels):
    """Compare entity coverage across multiple pages."""
    categories = ["Organizations", "Technologies", "Concepts", "People"]
    fig = go.Figure()
    colors = ["#4f98a3","#d29922","#3fb950","#f85149","#8b949e"]
    for i, (ents, label) in enumerate(zip(entities_list, labels)):
        counts = [len(ents.get(cat, {})) for cat in categories]
        fig.add_trace(go.Bar(
            name=label[:30],
            x=categories,
            y=counts,
            marker_color=colors[i % len(colors)],
            text=counts,
            textposition="outside",
        ))
    fig.update_layout(
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#161b22",
        xaxis=dict(tickfont=dict(color="#8b949e")),
        yaxis=dict(gridcolor="#30363d", tickfont=dict(color="#8b949e"), title="Unique Entities"),
        legend=dict(font=dict(color="#e6edf3"), bgcolor="#161b22", bordercolor="#30363d"),
        height=320, margin=dict(l=20, r=20, t=20, b=40)
    )
    return fig

# ═══════════════════════════════════════════════════════════════════════════
# WIKIDATA INTEGRATION (v3 NEW)
# ═══════════════════════════════════════════════════════════════════════════

def query_wikidata_entity(entity_name):
    """Fetch Wikidata info for a named entity via SPARQL / Wikidata API."""
    try:
        # Use Wikidata search API
        search_url = "https://www.wikidata.org/w/api.php"
        params = {
            "action": "wbsearchentities",
            "search": entity_name,
            "language": "en",
            "limit": 1,
            "format": "json",
        }
        resp = requests.get(search_url, params=params, timeout=8)
        data = resp.json()
        results = data.get("search", [])
        if not results:
            return None
        item = results[0]
        return {
            "id": item.get("id"),
            "label": item.get("label"),
            "description": item.get("description", ""),
            "url": f"https://www.wikidata.org/wiki/{item.get('id','')}",
            "found": True
        }
    except Exception:
        return None

def batch_wikidata_lookup(entity_list, max_entities=10):
    """Lookup multiple entities on Wikidata."""
    results = {}
    for ent in entity_list[:max_entities]:
        if ent and len(ent) > 2:
            result = query_wikidata_entity(ent)
            results[ent] = result
    return results

def wikidata_coverage_score(entities, wikidata_results):
    """Calculate what % of entities have Wikidata records."""
    all_ents = []
    for cat, ent_dict in entities.items():
        if cat not in ("Years", "Statistics"):
            all_ents.extend(list(ent_dict.keys())[:5])
    if not all_ents:
        return 0, 0, 0
    found = sum(1 for e in all_ents if wikidata_results.get(e) and wikidata_results[e])
    return found, len(all_ents), round(found / len(all_ents) * 100, 1) if all_ents else 0

# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════

# ── Session state initialisation (prevents resets) ──────────────────────────
for _k, _v in {
    "content_text": "", "page_title": "", "url_analyzed": "",
    "scores": None, "recs": None,
    "grounding_result": None, "quant_result": None,
    "comp_results": None, "scored_serp": None,
    "serp_keyword_last": "", "serp_results": [],
    "entity_graph_data": None,
    "openai_key": "", "dfs_login": "", "dfs_pass": "",
    "wikidata_results": {},
}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:16px 0 8px;">
        <div style="font-size:2rem;">⚡</div>
        <div style="font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:1.2rem;background:linear-gradient(135deg,#01696f,#4f98a3);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">TurboQuant</div>
        <div style="font-size:0.7rem;color:#8b949e;letter-spacing:1px;text-transform:uppercase;">AI Citation Intelligence v3</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── API Keys ──────────────────────────────────────────────────────────
    st.markdown("**🔑 API Keys**")
    with st.expander("Configure API Keys", expanded=not bool(st.session_state.get("openai_key") or st.session_state.get("dfs_login"))):
        _oai = st.text_input("OpenAI API Key", value=st.session_state.get("openai_key",""), type="password", placeholder="sk-...", key="_oai_inp", help="Used for AI grounding tests and entity analysis")
        _dfl = st.text_input("DataForSEO Login", value=st.session_state.get("dfs_login",""), placeholder="you@example.com", key="_dfl_inp")
        _dfp = st.text_input("DataForSEO Password", value=st.session_state.get("dfs_pass",""), type="password", placeholder="API password", key="_dfp_inp")
        if st.button("💾 Save API Keys", key="save_api_keys"):
            st.session_state["openai_key"] = _oai
            st.session_state["dfs_login"] = _dfl
            st.session_state["dfs_pass"] = _dfp
            st.success("✅ Keys saved for this session.")

    st.divider()

    st.markdown("**📥 Input Mode**")
    input_mode = st.radio("Input Mode", ["🔗 URL", "📝 Paste Text"], label_visibility="hidden")

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
    <span style="color:#30363d;">v3.0 · May 2026</span>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ═══════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="hero-header">
    <div class="hero-title">⚡ TurboQuant Simulator <span class="badge-pill badge-v2" style="vertical-align:middle;font-size:0.9rem;">v2</span></div>
    <div class="hero-sub">Analyze how easily AI can understand, retrieve, and cite your content</div>
</div>
""", unsafe_allow_html=True)

# ── Input Section ─────────────────────────────────────────────────────────
with st.container():
    col_in1, col_in2 = st.columns([3, 1])

    if "URL" in input_mode:
        with col_in1:
            url_input = st.text_input("Enter URL to Analyze", placeholder="https://example.com/your-page", label_visibility="hidden", key="url_input_field")
        with col_in2:
            analyze_btn = st.button("⚡ Analyze", width='stretch', key="analyze_url_btn")

        if analyze_btn and url_input:
            with st.spinner("🕸️ Extracting content..."):
                result = extract_content_from_url(url_input)
            if result["success"] and result["text"]:
                st.session_state["content_text"] = result["text"]
                st.session_state["page_title"] = result["title"]
                st.session_state["url_analyzed"] = url_input
                st.session_state["scores"] = None
                st.session_state["recs"] = None
                st.success(f"✅ Extracted from: **{result['title']}** — {count_words(result['text']):,} words")
            else:
                st.error(f"❌ Could not extract content: {result.get('error', 'Unknown error')}")
    else:
        with col_in1:
            content_text_input = st.text_area("Paste Your Content", height=160, placeholder="Paste your article, landing page, or blog post here...", label_visibility="hidden", key="paste_content_field")
        with col_in2:
            st.write("")
            st.write("")
            analyze_btn2 = st.button("⚡ Analyze", width='stretch', key="analyze_paste_btn")

        if analyze_btn2 and content_text_input:
            st.session_state["content_text"] = content_text_input
            st.session_state["page_title"] = "Pasted Content"
            st.session_state["url_analyzed"] = ""
            st.session_state["scores"] = None
            st.session_state["recs"] = None

content_text = st.session_state.get("content_text", "")
page_title = st.session_state.get("page_title", "")
url_analyzed = st.session_state.get("url_analyzed", "")

# ── Results (only shown when content exists) ──────────────────────────────
if content_text and len(content_text.split()) > 30:
    if st.session_state.get("scores") is None:
        st.session_state["scores"] = calculate_seo_score(content_text)
        st.session_state["recs"] = generate_recommendations(st.session_state["scores"])
    scores = st.session_state["scores"]
    recs = st.session_state["recs"]

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
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
        "📊 SEO 3.0 Analysis",
        "🔐 Authority Signals",
        "🗜️ Quantize Text",
        "🧪 Quantization Lab",
        "🎯 Grounding Test",
        "📈 Keyword Density",
        "🔎 URL Comparator",
        "🌐 SERP Intelligence",
        "🕸️ Entity Graph",
        "🌍 Wikidata Intel",
    ])

    # ── TAB 1: SEO 3.0 ANALYSIS ──────────────────────────────────────────
    with tab1:
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.plotly_chart(make_gauge(scores["overall"], "Overall SEO 3.0 Score"), width='stretch', config={"displayModeBar": False})
        with col_g2:
            st.plotly_chart(make_gauge(scores["citation_potential"], "Citation Potential"), width='stretch', config={"displayModeBar": False})

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown('<div class="section-header">Component Scores — Radar</div>', unsafe_allow_html=True)
            st.plotly_chart(make_radar(scores["components"]), width='stretch', config={"displayModeBar": False})
        with col_r2:
            st.markdown('<div class="section-header">Component Breakdown</div>', unsafe_allow_html=True)
            st.plotly_chart(make_bar_chart(scores["components"]), width='stretch', config={"displayModeBar": False})

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
        st.plotly_chart(fig_sw, width='stretch', config={"displayModeBar": False})

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

        st.plotly_chart(make_compression_viz(quant_result["original_tokens"], quant_result["compressed_tokens"], quant_result["ratio"]), width='stretch', config={"displayModeBar": False})

        col_q1, col_q2 = st.columns(2)
        with col_q1:
            st.markdown("**📄 Original Content (preview)**")
            st.markdown(f"""<div style="background:#161b22;border:1px solid #30363d;border-radius:8px;padding:14px;font-size:0.82rem;color:#8b949e;max-height:220px;overflow-y:auto;line-height:1.6;">{content_text[:800]}{'...' if len(content_text) > 800 else ''}</div>""", unsafe_allow_html=True)
        with col_q2:
            st.markdown("**⚡ Quantized Output (high-density sentences)**")
            st.markdown(f"""<div style="background:#161b22;border:1px solid #01696f;border-radius:8px;padding:14px;font-size:0.82rem;color:#e6edf3;max-height:220px;overflow-y:auto;line-height:1.6;">{quant_result['compressed'][:800]}{'...' if len(quant_result['compressed']) > 800 else ''}</div>""", unsafe_allow_html=True)

        with st.expander("📋 Copy Full Quantized Text"):
            st.text_area("Compressed Content", quant_result["compressed"], height=200, label_visibility="hidden")

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
            st.plotly_chart(make_kv_compression_chart(), width='stretch', config={"displayModeBar": False})

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
        st.plotly_chart(fig_impact, width='stretch', config={"displayModeBar": False})

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

        grounding_query = st.text_input("🔍 Enter a query to test against your content", placeholder="e.g. What are the best link building strategies for AI citations?", key="grounding_query_input")

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
            st.plotly_chart(fig_cp, width='stretch', config={"displayModeBar": False})

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

    # ── TAB 6: KEYWORD DENSITY (v2 NEW) ─────────────────────────────────────
    with tab6:
        st.markdown('<div class="section-header">📈 Keyword Density & Content Gap <span class="badge-pill badge-new" style="font-size:0.7rem;vertical-align:middle;">NEW v2</span></div>', unsafe_allow_html=True)

        col_kd1, col_kd2 = st.columns([1, 1])

        with col_kd1:
            st.markdown("**🔑 Top Keywords by Frequency**")
            kw_data, total_kw = keyword_density(content_text, top_n=15)
            if kw_data:
                max_count = kw_data[0][1]
                kw_html = ""
                for word, count, density in kw_data:
                    bar_pct = int((count / max_count) * 100)
                    bar_color = "#3fb950" if density > 1.0 else "#4f98a3" if density > 0.5 else "#30363d"
                    kw_html += f"""
                    <div class="kw-bar-wrap">
                        <div class="kw-label">{word}</div>
                        <div class="kw-bar"><div class="kw-fill" style="width:{bar_pct}%;background:{bar_color};"></div></div>
                        <div class="kw-count">{count}</div>
                        <div style="font-size:0.72rem;color:#8b949e;width:50px;">{density}%</div>
                    </div>
                    """
                st.markdown(kw_html, unsafe_allow_html=True)
                st.caption(f"Total content words: {total_kw:,}")
            else:
                st.info("No content available for keyword analysis.")

        with col_kd2:
            st.markdown("**🎯 Content Gap Analysis**")
            st.markdown("""
            <div class="info-box" style="margin-bottom:12px;">
            <strong>Enter your target keywords</strong> (one per line) to check coverage, density, and gaps in your content.
            </div>
            """, unsafe_allow_html=True)
            target_kws = st.text_area("Target Keywords (one per line)", placeholder="AI citation\nGoogle TurboQuant\ncontent optimization\nKV cache", height=120, key="kw_gap_input")

            if target_kws.strip():
                kw_list = [k.strip() for k in target_kws.strip().splitlines() if k.strip()]
                gap_results = content_gap_analysis(content_text, kw_list)
                for r in gap_results:
                    if r["status"] == "missing":
                        badge_cls = "badge-missing"
                        badge_lbl = "❌ Missing"
                        icon = "🔴"
                    elif r["status"] == "low":
                        badge_cls = "badge-partial"
                        badge_lbl = "🟡 Low"
                        icon = "🟡"
                    elif r["status"] == "over":
                        badge_cls = "badge-partial"
                        badge_lbl = "⚠️ Overused"
                        icon = "🟠"
                    else:
                        badge_cls = "badge-found"
                        badge_lbl = "✅ Optimal"
                        icon = "🟢"

                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;align-items:center;background:var(--surface-2);border:1px solid var(--border);border-radius:8px;padding:10px 14px;margin-bottom:6px;">
                        <div>
                            <span style="font-weight:600;color:var(--text);font-size:0.88rem;">{icon} {r["keyword"]}</span>
                            <span style="color:var(--muted);font-size:0.75rem;margin-left:10px;">{r["count"]} mentions · {r["density"]}% density</span>
                        </div>
                        <span class="signal-badge {badge_cls}">{badge_lbl}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="text-align:center;padding:40px;color:#8b949e;">
                    <div style="font-size:2rem;margin-bottom:8px;">🎯</div>
                    <div>Enter target keywords above to run gap analysis</div>
                </div>
                """, unsafe_allow_html=True)

        st.divider()
        st.markdown('<div class="section-header">📖 Readability & Sentence Variety</div>', unsafe_allow_html=True)
        col_r1, col_r2, col_r3 = st.columns([1, 1, 2])

        flesch_score, flesch_grade = calculate_readability(content_text)
        sv = sentence_variety(content_text)

        with col_r1:
            flesch_color = "#3fb950" if flesch_score >= 60 else "#d29922" if flesch_score >= 40 else "#f85149"
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;">
                <div style="font-family:'Space Grotesk',sans-serif;font-size:3rem;font-weight:700;color:{flesch_color};">{flesch_score}</div>
                <div class="metric-label">Flesch Reading Ease</div>
                <div style="margin-top:8px;"><span class="signal-badge" style="background:rgba(1,105,111,0.12);color:#4f98a3;border:1px solid rgba(1,105,111,0.3);">{flesch_grade}</span></div>
                <div style="font-size:0.75rem;color:#8b949e;margin-top:8px;">AI prefers 50–70 for citations</div>
            </div>
            """, unsafe_allow_html=True)

        with col_r2:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:0.8rem;color:#8b949e;margin-bottom:10px;">Sentence Length Mix</div>
                <div style="font-size:0.82rem;margin-bottom:4px;">⚡ Short (&lt;10w): <strong style="color:#e6edf3;">{sv["short"]}</strong></div>
                <div style="font-size:0.82rem;margin-bottom:4px;">✅ Medium (11-20w): <strong style="color:#3fb950;">{sv["medium"]}</strong></div>
                <div style="font-size:0.82rem;margin-bottom:4px;">📝 Long (21-35w): <strong style="color:#d29922;">{sv["long"]}</strong></div>
                <div style="font-size:0.82rem;margin-bottom:4px;">⚠️ Very Long (&gt;35w): <strong style="color:#f85149;">{sv["very_long"]}</strong></div>
                <div style="font-size:0.75rem;color:#8b949e;margin-top:8px;">Avg: {sv["avg_len"]} words/sentence</div>
            </div>
            """, unsafe_allow_html=True)

        with col_r3:
            if sv["total"] > 0:
                labels = ["Short (<10w)", "Medium (11-20w)", "Long (21-35w)", "Very Long (>35w)"]
                values = [sv["short"], sv["medium"], sv["long"], sv["very_long"]]
                colors_pie = ["#4f98a3", "#3fb950", "#d29922", "#f85149"]
                fig_pie = go.Figure(go.Pie(
                    labels=labels, values=values,
                    marker=dict(colors=colors_pie, line=dict(color="#161b22", width=2)),
                    hole=0.5, textfont=dict(color="#e6edf3", size=11)
                ))
                fig_pie.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    showlegend=True,
                    legend=dict(font=dict(color="#e6edf3"), bgcolor="#161b22"),
                    height=220, margin=dict(l=0, r=0, t=10, b=0)
                )
                st.plotly_chart(fig_pie, width='stretch', config={"displayModeBar": False})

        st.divider()
        st.markdown('<div class="section-header">🏷️ Detected Entities</div>', unsafe_allow_html=True)
        entities = extract_entities(content_text)

        ent_col1, ent_col2, ent_col3, ent_col4 = st.columns(4)
        with ent_col1:
            st.markdown("**🏢 Organizations**")
            if entities["orgs"]:
                chips = "".join([f'<span class="entity-chip entity-covered">{e}</span>' for e in entities["orgs"]])
                st.markdown(chips, unsafe_allow_html=True)
            else:
                st.markdown('<span class="entity-chip entity-missing">None detected</span>', unsafe_allow_html=True)
        with ent_col2:
            st.markdown("**📅 Years Referenced**")
            if entities["years"]:
                chips = "".join([f'<span class="entity-chip entity-partial">{y}</span>' for y in sorted(entities["years"], reverse=True)])
                st.markdown(chips, unsafe_allow_html=True)
            else:
                st.markdown('<span class="entity-chip entity-missing">None detected</span>', unsafe_allow_html=True)
        with ent_col3:
            st.markdown("**📊 Statistics Found**")
            if entities["percentages"]:
                chips = "".join([f'<span class="entity-chip entity-covered">{p}</span>' for p in entities["percentages"]])
                st.markdown(chips, unsafe_allow_html=True)
            else:
                st.markdown('<span class="entity-chip entity-missing">None detected</span>', unsafe_allow_html=True)
        with ent_col4:
            st.markdown("**👤 People Mentioned**")
            if entities["people"]:
                chips = "".join([f'<span class="entity-chip entity-partial">{p}</span>' for p in entities["people"]])
                st.markdown(chips, unsafe_allow_html=True)
            else:
                st.markdown('<span class="entity-chip entity-missing">None detected</span>', unsafe_allow_html=True)


    # ── TAB 7: URL COMPARATOR (v2 NEW) ─────────────────────────────────────
    with tab7:
        st.markdown('<div class="section-header">🔎 Multi-URL Comparator <span class="badge-pill badge-new" style="font-size:0.7rem;vertical-align:middle;">NEW v2</span></div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-box" style="margin-bottom:16px;">
        <strong>Competitive Citation Analysis:</strong> Enter up to 5 URLs to compare their TurboQuant scores side-by-side.
        Identify which competitor pages are best optimised for AI citation and find gaps in your own content.
        </div>
        """, unsafe_allow_html=True)

        urls_input = st.text_area(
            "Enter URLs to compare (one per line, max 5)",
            placeholder="https://example.com/page-1\nhttps://competitor.com/page-2\nhttps://yoursite.com/target-page",
            height=130, key="comparator_urls"
        )

        run_compare = st.button("⚡ Run Comparison", key="run_compare_btn")

        if run_compare and urls_input.strip():
            st.session_state["comp_results"] = None
            url_list = [u.strip() for u in urls_input.strip().splitlines() if u.strip()][:5]
            if len(url_list) < 2:
                st.warning("Please enter at least 2 URLs to compare.")
            else:
                with st.spinner(f"Fetching and scoring {len(url_list)} URLs…"):
                    comp_results = score_multiple_urls(url_list)

                st.session_state["comp_results"] = comp_results
                if comp_results:
                    st.markdown("**📊 Score Overview**")
                    # Summary table
                    table_html = """
                    <table class="compare-table">
                    <thead><tr>
                        <th>#</th><th>URL</th><th>Title</th>
                        <th>Overall</th><th>Citation</th><th>Words</th><th>Freshness</th>
                    </tr></thead><tbody>
                    """
                    for i, r in enumerate(comp_results):
                        rank_color = "#3fb950" if r["overall"] >= 70 else "#d29922" if r["overall"] >= 50 else "#f85149"
                        table_html += f"""
                        <tr>
                            <td>{i+1}</td>
                            <td style="font-size:0.75rem;color:#4f98a3;max-width:220px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{r["url"]}</td>
                            <td style="font-size:0.8rem;max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{r["title"]}</td>
                            <td><strong style="color:{rank_color};">{r["overall"]}</strong></td>
                            <td>{r["citation_potential"]}</td>
                            <td>{r["word_count"]:,}</td>
                            <td>{r["freshness"]}%</td>
                        </tr>
                        """
                    table_html += "</tbody></table>"
                    st.markdown(table_html, unsafe_allow_html=True)

                    st.write("")

                    # Bar chart comparison
                    if len(comp_results) >= 2 and any(r["overall"] > 0 for r in comp_results):
                        labels = [r["url"][:40] + "..." if len(r["url"]) > 40 else r["url"] for r in comp_results]
                        overalls = [r["overall"] for r in comp_results]
                        citations = [r["citation_potential"] for r in comp_results]
                        bar_colors = ["#3fb950" if v >= 70 else "#d29922" if v >= 50 else "#f85149" for v in overalls]

                        fig_comp = go.Figure()
                        fig_comp.add_trace(go.Bar(
                            name="Overall Score", x=labels, y=overalls,
                            marker_color=bar_colors, text=[f"{v}" for v in overalls],
                            textposition="outside", textfont=dict(color="#e6edf3")
                        ))
                        fig_comp.add_trace(go.Bar(
                            name="Citation Potential", x=labels, y=citations,
                            marker_color=["rgba(79,152,163,0.5)"]*len(citations),
                            text=[f"{v}" for v in citations],
                            textposition="outside", textfont=dict(color="#8b949e")
                        ))
                        fig_comp.update_layout(
                            barmode="group",
                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#161b22",
                            xaxis=dict(tickfont=dict(color="#8b949e", size=10), gridcolor="#30363d"),
                            yaxis=dict(range=[0, 120], gridcolor="#30363d", tickfont=dict(color="#8b949e"), title="Score"),
                            legend=dict(font=dict(color="#e6edf3"), bgcolor="#161b22", bordercolor="#30363d", borderwidth=1),
                            height=320, margin=dict(l=20, r=20, t=20, b=80)
                        )
                        st.plotly_chart(fig_comp, width='stretch', config={"displayModeBar": False})

                    # Component heatmap
                    valid = [r for r in comp_results if r["components"]]
                    if len(valid) >= 2:
                        st.markdown("**🔥 Component Score Heatmap**")
                        all_components = list(valid[0]["components"].keys())
                        z_vals = [[r["components"].get(c, 0) for c in all_components] for r in valid]
                        y_labels = [r["url"][:35] + "…" if len(r["url"]) > 35 else r["url"] for r in valid]
                        fig_heat = go.Figure(go.Heatmap(
                            z=z_vals,
                            x=[c.split("(")[0].strip()[:15] for c in all_components],
                            y=y_labels,
                            colorscale=[[0, "#1c1026"], [0.4, "#f85149"], [0.7, "#d29922"], [1.0, "#3fb950"]],
                            text=[[str(v) for v in row] for row in z_vals],
                            texttemplate="%{text}",
                            textfont=dict(size=10, color="white"),
                            zmin=0, zmax=100
                        ))
                        fig_heat.update_layout(
                            paper_bgcolor="rgba(0,0,0,0)",
                            xaxis=dict(tickfont=dict(color="#8b949e", size=10), side="bottom"),
                            yaxis=dict(tickfont=dict(color="#e6edf3", size=10)),
                            height=max(200, len(valid) * 80),
                            margin=dict(l=20, r=20, t=20, b=60)
                        )
                        st.plotly_chart(fig_heat, width='stretch', config={"displayModeBar": False})
        else:
            if not run_compare:
                st.markdown("""
                <div style="text-align:center;padding:60px;color:#8b949e;">
                    <div style="font-size:2.5rem;margin-bottom:10px;">🔎</div>
                    <div style="font-size:1rem;">Enter URLs above and click <strong style="color:#4f98a3;">Run Comparison</strong></div>
                    <div style="font-size:0.82rem;margin-top:6px;">Compares TurboQuant scores, citation potential, and component breakdowns side by side</div>
                </div>
                """, unsafe_allow_html=True)


    # ── TAB 8: SERP INTELLIGENCE + DataForSEO (v2 NEW) ──────────────────
    with tab8:
        st.markdown('''
        <div class="hero-header" style="padding:12px 0 8px;">
            <div style="font-family:'Space Grotesk',sans-serif;font-size:1.4rem;font-weight:700;background:linear-gradient(135deg,#01696f,#4f98a3,#0ea5e9);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                🌐 SERP Intelligence — Powered by DataForSEO
            </div>
            <div style="color:#8b949e;font-size:0.85rem;margin-top:4px;">
                Enter a keyword → scrape top Google results → run TurboQuant on each page → compare AI citation readiness
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div class="info-box" style="margin-bottom:16px;">
        <strong>How it works:</strong> Uses the <strong>DataForSEO SERP API</strong> to fetch live Google top-10 results for your keyword.
        Each result URL is then fetched and scored using the full TurboQuant engine — giving you a complete competitive
        citation readiness map for any keyword in seconds.
        </div>
        ''', unsafe_allow_html=True)

        # ── DataForSEO Credentials (set in sidebar API Keys) ───────────────
        dfs_login = st.session_state.get("dfs_login", "")
        dfs_pass  = st.session_state.get("dfs_pass", "")
        if not dfs_login or not dfs_pass:
            st.info("ℹ️ Set your **DataForSEO** credentials in the **🔑 API Keys** panel in the sidebar to enable SERP analysis.")

        st.divider()

        # ── SERP Query Input ─────────────────────────────────────────────
        col_si1, col_si2, col_si3 = st.columns([3, 1, 1])
        with col_si1:
            serp_keyword = st.text_input(
                "🔍 Target Keyword",
                placeholder="e.g. car detailing Toronto, best SEO tools 2026",
                key="serp_keyword_input"
            )
        with col_si2:
            serp_location = st.selectbox(
                "Location",
                ["United States", "United Kingdom", "Canada", "Australia", "Pakistan", "India", "Global"],
                key="serp_location"
            )
        with col_si3:
            serp_results_n = st.selectbox("Results", [5, 10], index=1, key="serp_results_n")

        location_code_map = {
            "United States": 2840,
            "United Kingdom": 2826,
            "Canada": 2124,
            "Australia": 2036,
            "Pakistan": 2586,
            "India": 2356,
            "Global": 2840
        }

        run_serp = st.button("🚀 Run SERP + TurboQuant Analysis", key="run_serp_btn", width='stretch')

        if run_serp:
            if not serp_keyword.strip():
                st.warning("⚠️ Please enter a keyword.")
            elif not dfs_login or not dfs_pass:
                st.warning("⚠️ Please enter your DataForSEO credentials in the panel above.")
            else:
                # ── Step 1: Fetch SERP via DataForSEO ───────────────────
                serp_status = st.empty()
                serp_status.markdown('''
                <div style="background:rgba(1,105,111,0.08);border:1px solid rgba(1,105,111,0.3);border-radius:8px;padding:12px 16px;font-size:0.85rem;color:#4f98a3;">
                ⏳ <strong>Step 1/3:</strong> Fetching live SERP data from DataForSEO…
                </div>''', unsafe_allow_html=True)

                _serp_error = False
                try:
                    import base64
                    loc_code = location_code_map.get(serp_location, 2840)
                    dfs_payload = [{"keyword": serp_keyword, "location_code": loc_code, "language_code": "en", "device": "desktop", "os": "windows", "depth": serp_results_n}]
                    creds = base64.b64encode(f"{dfs_login}:{dfs_pass}".encode()).decode()
                    dfs_resp = requests.post(
                        "https://api.dataforseo.com/v3/serp/google/organic/live/advanced",
                        headers={"Authorization": f"Basic {creds}", "Content-Type": "application/json"},
                        json=dfs_payload,
                        timeout=30
                    )
                    # Guard: check HTTP status first
                    if dfs_resp.status_code == 401:
                        st.error("❌ DataForSEO authentication failed. Check your login/password in the API Keys panel.")
                        _serp_error = True
                    elif dfs_resp.status_code != 200:
                        st.error(f"❌ DataForSEO returned HTTP {dfs_resp.status_code}. Response: {dfs_resp.text[:300]}")
                        _serp_error = True
                    else:
                        try:
                            dfs_data = dfs_resp.json()
                        except Exception:
                            st.error(f"❌ DataForSEO returned invalid JSON. Raw response: {dfs_resp.text[:300]}")
                            _serp_error = True
                            dfs_data = None

                        if not _serp_error and dfs_data is None:
                            st.error("❌ DataForSEO returned an empty response.")
                            _serp_error = True

                        if not _serp_error:
                            top_status = dfs_data.get("status_code") if isinstance(dfs_data, dict) else None
                            if top_status != 20000:
                                msg = dfs_data.get("status_message", "Unknown error") if isinstance(dfs_data, dict) else "Malformed response"
                                st.error(f"❌ DataForSEO API error ({top_status}): {msg}")
                                _serp_error = True

                        if not _serp_error:
                            tasks = dfs_data.get("tasks") or []
                            if not tasks:
                                st.error("❌ DataForSEO returned no tasks. Try again.")
                                _serp_error = True
                            else:
                                task = tasks[0]
                                if task is None:
                                    st.error("❌ DataForSEO task is null. The API may be temporarily unavailable.")
                                    _serp_error = True
                                else:
                                    task_status = task.get("status_code")
                                    if task_status != 20000:
                                        task_msg = task.get("status_message", "Unknown task error")
                                        st.error(f"❌ DataForSEO task error ({task_status}): {task_msg}")
                                        _serp_error = True

                        if not _serp_error:
                            result_items = []
                            for res in (task.get("result") or []):
                                if res is None:
                                    continue
                                for item in (res.get("items") or []):
                                    if item is None:
                                        continue
                                    if item.get("type") == "organic":
                                        result_items.append({
                                            "rank": item.get("rank_absolute", 0),
                                            "title": (item.get("title") or "No title")[:80],
                                            "url": item.get("url") or "",
                                            "description": (item.get("description") or "")[:200],
                                            "domain": item.get("domain") or "",
                                        })

                            if not result_items:
                                st.error("❌ No organic results found. Try a different keyword or location.")
                                _serp_error = True
                            else:
                                result_items = result_items[:serp_results_n]
                                st.session_state["serp_results"] = result_items
                                st.session_state["serp_keyword_last"] = serp_keyword
                                st.session_state["scored_serp"] = []

                except requests.exceptions.ConnectionError:
                    st.error("❌ Could not reach DataForSEO. Check your internet connection.")
                    _serp_error = True
                except requests.exceptions.Timeout:
                    st.error("❌ DataForSEO request timed out (30s). Try again.")
                    _serp_error = True
                except Exception as e:
                    st.error(f"❌ Unexpected error contacting DataForSEO: {type(e).__name__}: {str(e)}")
                    _serp_error = True

                if not _serp_error:
                  # ── Step 2: Score each URL with TurboQuant ───────────────
                  serp_status.markdown('''
                  <div style="background:rgba(1,105,111,0.08);border:1px solid rgba(1,105,111,0.3);border-radius:8px;padding:12px 16px;font-size:0.85rem;color:#4f98a3;">
                  ⏳ <strong>Step 2/3:</strong> Running TurboQuant scoring on each result page…
                  </div>''', unsafe_allow_html=True)

                  scored_serp = []
                  prog_bar = st.progress(0, text="Fetching pages…")
                  _result_items = st.session_state.get("serp_results", [])
                  for _idx, item in enumerate(_result_items):
                      prog_bar.progress((_idx + 1) / max(len(_result_items), 1), text=f"Scoring {item.get('domain','')} ({_idx+1}/{len(_result_items)})…")
                      page_data = extract_content_from_url(item["url"])
                      if page_data["success"] and page_data["text"]:
                          s = calculate_seo_score(page_data["text"], page_data.get("headings", []))
                          r_score, r_grade = calculate_readability(page_data["text"])
                          ents = extract_entities(page_data["text"])
                          kws, _ = keyword_density(page_data["text"], top_n=5)
                          scored_serp.append({
                              **item,
                              "tq_overall": s["overall"],
                              "tq_citation": s["citation_potential"],
                              "word_count": s["word_count"],
                              "freshness": s["freshness"],
                              "stat_count": s["stat_count"],
                              "quote_count": s["quote_count"],
                              "components": s["components"],
                              "readability": r_score,
                              "readability_grade": r_grade,
                              "entities": ents,
                              "top_keywords": kws,
                              "fetched": True,
                          })
                      else:
                          scored_serp.append({
                              **item,
                              "tq_overall": 0, "tq_citation": 0, "word_count": 0,
                              "freshness": 0, "stat_count": 0, "quote_count": 0,
                              "components": {}, "readability": 0, "readability_grade": "N/A",
                              "entities": {}, "top_keywords": [], "fetched": False,
                          })
                  prog_bar.empty()
                  st.session_state["scored_serp"] = scored_serp
                  serp_status.empty()

        # ── Display SERP Results ─────────────────────────────────────────
        scored_serp = st.session_state.get("scored_serp", [])
        serp_kw = st.session_state.get("serp_keyword_last", "")

        if scored_serp:
            st.markdown(f'''
            <div style="margin-bottom:16px;">
                <span style="font-family:'Space Grotesk',sans-serif;font-size:1rem;font-weight:600;color:#e6edf3;">
                    Results for: </span>
                <span style="background:rgba(1,105,111,0.15);border:1px solid rgba(1,105,111,0.4);border-radius:6px;padding:3px 12px;color:#4f98a3;font-weight:700;font-family:monospace;">
                    {serp_kw}
                </span>
                <span style="color:#8b949e;font-size:0.8rem;margin-left:10px;">{len(scored_serp)} pages analysed</span>
            </div>
            ''', unsafe_allow_html=True)

            # ── Summary metrics ──────────────────────────────────────────
            fetched = [r for r in scored_serp if r["fetched"]]
            if fetched:
                avg_tq = round(sum(r["tq_overall"] for r in fetched) / len(fetched), 1)
                avg_cp = round(sum(r["tq_citation"] for r in fetched) / len(fetched), 1)
                avg_wc = round(sum(r["word_count"] for r in fetched) / len(fetched))
                top_page = max(fetched, key=lambda x: x["tq_overall"])

                sm1, sm2, sm3, sm4 = st.columns(4)
                sm1.metric("⚡ Avg TQ Score", f"{avg_tq}/100", help="Average TurboQuant overall score across all SERP results")
                sm2.metric("📌 Avg Citation Potential", f"{avg_cp}/100", help="Average citation potential score")
                sm3.metric("📝 Avg Word Count", f"{avg_wc:,}", help="Average word count of top results")
                sm4.metric("🥇 Top Scoring Page", f"#{top_page['rank']}", delta=f"Score: {top_page['tq_overall']}")

                st.write("")

            # ── Score comparison chart ───────────────────────────────────
            st.markdown('<div class="section-header">📊 TurboQuant Score — All SERP Results</div>', unsafe_allow_html=True)
            chart_labels = [f"#{r['rank']} {r['domain'][:20]}" for r in scored_serp]
            chart_tq = [r["tq_overall"] for r in scored_serp]
            chart_cp = [r["tq_citation"] for r in scored_serp]
            bar_colors_serp = ["#3fb950" if v >= 70 else "#d29922" if v >= 50 else "#f85149" for v in chart_tq]

            fig_serp_bar = go.Figure()
            fig_serp_bar.add_trace(go.Bar(
                name="Overall TQ Score", x=chart_labels, y=chart_tq,
                marker_color=bar_colors_serp,
                text=[str(v) for v in chart_tq], textposition="outside",
                textfont=dict(color="#e6edf3", size=11)
            ))
            fig_serp_bar.add_trace(go.Bar(
                name="Citation Potential", x=chart_labels, y=chart_cp,
                marker_color=["rgba(79,152,163,0.45)"]*len(chart_cp),
                text=[str(v) for v in chart_cp], textposition="outside",
                textfont=dict(color="#8b949e", size=10)
            ))
            fig_serp_bar.update_layout(
                barmode="group",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#161b22",
                xaxis=dict(tickfont=dict(color="#8b949e", size=10), gridcolor="#30363d"),
                yaxis=dict(range=[0, 120], gridcolor="#30363d", tickfont=dict(color="#8b949e"), title="Score /100", title_font=dict(color="#8b949e")),
                legend=dict(font=dict(color="#e6edf3"), bgcolor="#161b22", bordercolor="#30363d", borderwidth=1),
                height=320, margin=dict(l=20, r=20, t=20, b=80)
            )
            st.plotly_chart(fig_serp_bar, width='stretch', config={"displayModeBar": False})

            # ── Component heatmap ────────────────────────────────────────
            valid_s = [r for r in scored_serp if r["components"]]
            if valid_s:
                st.markdown('<div class="section-header">🔥 Component Heatmap — All Pages</div>', unsafe_allow_html=True)
                comp_keys = list(valid_s[0]["components"].keys())
                z_heat = [[r["components"].get(k, 0) for k in comp_keys] for r in valid_s]
                y_heat = [f"#{r['rank']} {r['domain'][:18]}" for r in valid_s]

                fig_heat_serp = go.Figure(go.Heatmap(
                    z=z_heat,
                    x=[c.split("(")[0].strip()[:14] for c in comp_keys],
                    y=y_heat,
                    colorscale=[[0,"#1c1026"],[0.4,"#f85149"],[0.7,"#d29922"],[1.0,"#3fb950"]],
                    text=[[str(v) for v in row] for row in z_heat],
                    texttemplate="%{text}",
                    textfont=dict(size=10, color="white"),
                    zmin=0, zmax=100
                ))
                fig_heat_serp.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(tickfont=dict(color="#8b949e", size=10), side="bottom"),
                    yaxis=dict(tickfont=dict(color="#e6edf3", size=10)),
                    height=max(240, len(valid_s) * 60),
                    margin=dict(l=20, r=20, t=20, b=60)
                )
                st.plotly_chart(fig_heat_serp, width='stretch', config={"displayModeBar": False})

            # ── Individual result cards ──────────────────────────────────
            st.markdown('<div class="section-header" style="margin-top:8px;">📋 Detailed Result Cards</div>', unsafe_allow_html=True)
            for r in scored_serp:
                rank_cls = "top3" if r["rank"] <= 3 else ""
                tq_color = "#3fb950" if r["tq_overall"] >= 70 else "#d29922" if r["tq_overall"] >= 50 else "#f85149" if r["fetched"] else "#8b949e"
                fetch_status = "" if r["fetched"] else " <span style='color:#f85149;font-size:0.72rem;'>(Could not fetch)</span>"

                with st.expander(f"#{r['rank']} {r['title'][:70]} — TQ: {r['tq_overall']}/100", expanded=(r["rank"] <= 3)):
                    ec1, ec2, ec3, ec4, ec5 = st.columns(5)
                    ec1.metric("TQ Score", f"{r['tq_overall']}/100" if r["fetched"] else "N/A")
                    ec2.metric("Citation", f"{r['tq_citation']}/100" if r["fetched"] else "N/A")
                    ec3.metric("Words", f"{r['word_count']:,}" if r["fetched"] else "N/A")
                    ec4.metric("Freshness", f"{r['freshness']}%" if r["fetched"] else "N/A")
                    ec5.metric("Readability", r["readability_grade"] if r["fetched"] else "N/A")

                    st.markdown(f'''
                    <div style="font-size:0.75rem;color:#4f98a3;margin:6px 0 4px;">{r["url"]}{fetch_status}</div>
                    <div style="font-size:0.8rem;color:#8b949e;">{r["description"]}</div>
                    ''', unsafe_allow_html=True)

                    if r["fetched"] and r["entities"]:
                        ent = r["entities"]
                        ent_parts = []
                        if ent.get("orgs"):
                            ent_parts.append("🏢 " + ", ".join(ent["orgs"][:4]))
                        if ent.get("years"):
                            ent_parts.append("📅 " + ", ".join(sorted(ent["years"], reverse=True)[:3]))
                        if ent.get("percentages"):
                            ent_parts.append("📊 " + ", ".join(ent["percentages"][:3]))
                        if ent_parts:
                            st.markdown(f'<div style="font-size:0.75rem;color:#8b949e;margin-top:6px;">{" · ".join(ent_parts)}</div>', unsafe_allow_html=True)

                    if r["fetched"] and r["top_keywords"]:
                        kw_chips = "".join([f'<span class="token-chip">{k[0]}</span>' for k in r["top_keywords"]])
                        st.markdown(f'<div style="margin-top:6px;">{kw_chips}</div>', unsafe_allow_html=True)

            # ── Opportunity finder ───────────────────────────────────────
            st.divider()
            st.markdown('<div class="section-header">🎯 Citation Opportunity Finder</div>', unsafe_allow_html=True)
            st.markdown('''
            <div class="info-box" style="margin-bottom:14px;">
            Pages with <strong>high SERP rank but low TurboQuant score</strong> are the easiest citation opportunities —
            they rank well but are not well-optimised for AI. Target them with better-structured content.
            </div>
            ''', unsafe_allow_html=True)

            opp_data = [(r["rank"], r["domain"], r["tq_overall"], r["tq_citation"], r["word_count"])
                        for r in scored_serp if r["fetched"]]
            if opp_data:
                opp_df = pd.DataFrame(opp_data, columns=["Rank", "Domain", "TQ Score", "Citation Potential", "Words"])
                opp_df["Opportunity"] = opp_df.apply(
                    lambda row: "🔥 High" if row["Rank"] <= 5 and row["TQ Score"] < 55
                    else ("🟡 Medium" if row["Rank"] <= 7 and row["TQ Score"] < 70 else "✅ Low"),
                    axis=1
                )
                opp_df_sorted = opp_df.sort_values("TQ Score")

                # Scatter: rank vs TQ score
                fig_opp = go.Figure()
                colors_opp = ["#f85149" if row["Opportunity"] == "🔥 High" else "#d29922" if "Medium" in row["Opportunity"] else "#3fb950"
                              for _, row in opp_df_sorted.iterrows()]
                fig_opp.add_trace(go.Scatter(
                    x=opp_df_sorted["Rank"],
                    y=opp_df_sorted["TQ Score"],
                    mode="markers+text",
                    marker=dict(size=16, color=colors_opp, line=dict(color="#161b22", width=2)),
                    text=opp_df_sorted["Domain"].str[:12],
                    textposition="top center",
                    textfont=dict(color="#e6edf3", size=9),
                    customdata=opp_df_sorted[["Citation Potential","Words"]].values,
                    hovertemplate="<b>%{text}</b><br>Rank: #%{x}<br>TQ Score: %{y}<br>Citation: %{customdata[0]}<extra></extra>"
                ))
                fig_opp.add_hline(y=60, line_dash="dash", line_color="#d29922", annotation_text="Opportunity threshold (60)", annotation_font_color="#d29922")
                fig_opp.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#161b22",
                    xaxis=dict(title="SERP Rank", gridcolor="#30363d", tickfont=dict(color="#8b949e"), title_font=dict(color="#8b949e"), autorange="reversed"),
                    yaxis=dict(title="TQ Score /100", range=[0, 105], gridcolor="#30363d", tickfont=dict(color="#8b949e"), title_font=dict(color="#8b949e")),
                    height=300, margin=dict(l=20, r=20, t=20, b=40),
                    annotations=[dict(x=1, y=105, text="← Better SERP position", font=dict(color="#8b949e", size=10), showarrow=False, xanchor="left")]
                )
                st.plotly_chart(fig_opp, width='stretch', config={"displayModeBar": False})

                # Opportunity table
                st.dataframe(
                    opp_df_sorted[["Rank","Domain","TQ Score","Citation Potential","Words","Opportunity"]],
                    width='stretch', hide_index=True
                )

        elif not run_serp:
            st.markdown('''
            <div style="text-align:center;padding:60px 20px;color:#8b949e;">
                <div style="font-size:3rem;margin-bottom:12px;">🌐</div>
                <div style="font-size:1.1rem;font-weight:600;color:#e6edf3;margin-bottom:8px;">SERP Intelligence Engine</div>
                <div style="font-size:0.88rem;max-width:480px;margin:0 auto;line-height:1.7;">
                    Enter your DataForSEO credentials above, type a keyword, and click
                    <strong style="color:#4f98a3;">Run SERP + TurboQuant Analysis</strong> to get a full
                    competitive citation readiness report for any keyword.
                </div>
                <div style="margin-top:20px;display:flex;justify-content:center;gap:20px;flex-wrap:wrap;">
                    <div style="background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:12px 20px;font-size:0.82rem;">
                        🔍 Live Google SERP data
                    </div>
                    <div style="background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:12px 20px;font-size:0.82rem;">
                        ⚡ TurboQuant scoring per page
                    </div>
                    <div style="background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:12px 20px;font-size:0.82rem;">
                        🎯 Citation opportunity finder
                    </div>
                    <div style="background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:12px 20px;font-size:0.82rem;">
                        🔥 Component heatmap
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)


    # ── TAB 9: ENTITY GRAPH (v3 NEW) ─────────────────────────────────────
    with tab9:
        st.markdown('<div class="section-header">🕸️ Entity Graph — Visual Knowledge Map</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-box" style="margin-bottom:16px;">
        <strong>Entity Intelligence:</strong> Extract all named entities from your content, visualise co-occurrence relationships,
        and identify which entity categories are well covered vs. missing. Compare entity density vs. SERP competitors.
        </div>
        """, unsafe_allow_html=True)

        # Build entity data
        if "entity_graph_data" not in st.session_state or st.session_state["entity_graph_data"] is None:
            with st.spinner("🔍 Extracting entities..."):
                adv_ents = extract_entities_advanced(content_text)
                cooccur = build_entity_cooccurrence(content_text, adv_ents)
                st.session_state["entity_graph_data"] = {"entities": adv_ents, "cooccurrence": cooccur}

        adv_ents = st.session_state["entity_graph_data"]["entities"]
        cooccur  = st.session_state["entity_graph_data"]["cooccurrence"]

        # ── Entity KPI Row ──────────────────────────────────────────────
        total_ents = sum(len(v) for k, v in adv_ents.items() if k not in ("Years","Statistics"))
        total_orgs = len(adv_ents.get("Organizations", {}))
        total_tech = len(adv_ents.get("Technologies", {}))
        total_concepts = len(adv_ents.get("Concepts", {}))
        total_people = len(adv_ents.get("People", {}))

        eg1, eg2, eg3, eg4, eg5 = st.columns(5)
        eg1.metric("🕸️ Total Entities", total_ents)
        eg2.metric("🏢 Organizations", total_orgs)
        eg3.metric("⚙️ Technologies", total_tech)
        eg4.metric("💡 Concepts", total_concepts)
        eg5.metric("👤 People", total_people)

        st.write("")

        # ── Entity Graph Visualization ──────────────────────────────────
        graph_fig = make_entity_graph_chart(adv_ents, cooccur, title=f"Entity Network — {page_title[:50]}")
        if graph_fig:
            st.plotly_chart(graph_fig, width='stretch', config={"displayModeBar": False})
        else:
            st.info("Not enough entities detected to build a graph. Try longer content.")

        # ── Entity Coverage Table ───────────────────────────────────────
        st.markdown('<div class="section-header" style="margin-top:16px;">📋 Entity Inventory</div>', unsafe_allow_html=True)
        for cat, ent_dict in adv_ents.items():
            if not ent_dict:
                continue
            with st.expander(f"{cat} ({len(ent_dict)} unique)", expanded=(cat in ("Organizations","Technologies"))):
                chips_html = ""
                for ent, freq in sorted(ent_dict.items(), key=lambda x: -x[1]):
                    size = "1rem" if freq >= 3 else "0.85rem"
                    opacity = min(0.5 + freq * 0.1, 1.0)
                    chips_html += f'<span class="entity-chip" style="font-size:{size};opacity:{opacity};">{ent} <span style="color:#8b949e;font-size:0.75rem;">×{freq}</span></span> '
                st.markdown(chips_html, unsafe_allow_html=True)

        # ── Missing Entity Analysis ─────────────────────────────────────
        st.markdown('<div class="section-header" style="margin-top:16px;">🔍 Coverage Gap Analysis</div>', unsafe_allow_html=True)

        # Use scored_serp data if available for comparison
        serp_data = st.session_state.get("scored_serp", [])
        if serp_data:
            fetched_serp = [r for r in serp_data if r.get("fetched") and r.get("entities")]
            if fetched_serp:
                serp_ents_list = [extract_entities_advanced(r.get("domain","")) for r in fetched_serp[:5]]
                # Collect all competitor entities
                competitor_orgs = set()
                competitor_techs = set()
                for r in fetched_serp[:5]:
                    ents = r.get("entities", {})
                    competitor_orgs.update(ents.get("orgs", []))
                    competitor_techs.update(ents.get("years", []))

                my_orgs = set(adv_ents.get("Organizations", {}).keys())
                my_techs = set(adv_ents.get("Technologies", {}).keys())
                missing_orgs = competitor_orgs - my_orgs
                if missing_orgs:
                    st.markdown(f"**🏢 Organizations in top SERP results but missing from your content:**")
                    st.markdown(" ".join([f'<span class="entity-chip entity-missing">{e}</span>' for e in list(missing_orgs)[:12]]), unsafe_allow_html=True)
                else:
                    st.success("✅ Your organization entities match or exceed SERP competitors.")
            else:
                st.info("ℹ️ Run SERP Intelligence first to enable competitor entity gap analysis.")
        else:
            # Suggest common missing entities based on topic
            st.markdown("""
            <div class="info-box">
            💡 <strong>Tip:</strong> Run the <strong>🌐 SERP Intelligence</strong> tab first to auto-compare entity coverage
            against your top Google competitors. Entity gap analysis will appear here.
            </div>
            """, unsafe_allow_html=True)

        # ── Co-occurrence Heatmap ───────────────────────────────────────
        if cooccur:
            st.markdown('<div class="section-header" style="margin-top:16px;">🔥 Entity Co-occurrence</div>', unsafe_allow_html=True)
            pairs = sorted(cooccur.items(), key=lambda x: -x[1])[:20]
            pair_labels = [f"{e1} ↔ {e2}" for (e1, e2), _ in pairs]
            pair_vals = [v for _, v in pairs]
            fig_cooc = go.Figure(go.Bar(
                x=pair_vals, y=pair_labels, orientation="h",
                marker_color="#4f98a3",
                text=pair_vals, textposition="outside",
                textfont=dict(color="#e6edf3", size=10)
            ))
            fig_cooc.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#161b22",
                xaxis=dict(gridcolor="#30363d", tickfont=dict(color="#8b949e"), title="Co-occurrence Count"),
                yaxis=dict(tickfont=dict(color="#e6edf3", size=10)),
                height=max(280, len(pairs) * 22 + 60),
                margin=dict(l=20, r=60, t=20, b=30)
            )
            st.plotly_chart(fig_cooc, width='stretch', config={"displayModeBar": False})

    # ── TAB 10: WIKIDATA INTELLIGENCE (v3 NEW) ──────────────────────────
    with tab10:
        st.markdown('<div class="section-header">🌍 Wikidata Intelligence — Off-Page Entity Layer</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-box" style="margin-bottom:16px;">
        <strong>3-Layer Entity Model:</strong> Wikidata is the <em>off-page entity layer</em>.
        Entities with strong Wikidata records signal topical authority to AI systems.
        This tool checks how many of your page entities exist on Wikidata, how aligned they
        are to your topic, and identifies gaps vs competitors.
        </div>
        """, unsafe_allow_html=True)

        # Get entities from session
        entity_data = st.session_state.get("entity_graph_data")
        if entity_data is None:
            with st.spinner("Extracting entities..."):
                adv_ents_wd = extract_entities_advanced(content_text)
                st.session_state["entity_graph_data"] = {"entities": adv_ents_wd, "cooccurrence": {}}
        adv_ents_wd = st.session_state["entity_graph_data"]["entities"]

        # Flatten entities for lookup
        lookup_ents = []
        for cat in ("Organizations", "Technologies", "People"):
            lookup_ents.extend(list(adv_ents_wd.get(cat, {}).keys())[:5])

        col_wd1, col_wd2 = st.columns([3, 1])
        with col_wd1:
            st.markdown(f"**Entities queued for Wikidata lookup** ({len(lookup_ents[:12])} entities):")
            chips = " ".join([f'<span class="entity-chip">{e}</span>' for e in lookup_ents[:12]])
            st.markdown(chips if chips else "<em style='color:#8b949e;'>No entities detected yet. Analyze content first.</em>", unsafe_allow_html=True)
        with col_wd2:
            run_wikidata = st.button("🌍 Fetch Wikidata", key="run_wikidata_btn", help="Queries Wikidata for each entity (free, no API key needed)")

        if run_wikidata and lookup_ents:
            with st.spinner(f"🌐 Querying Wikidata for {min(len(lookup_ents), 12)} entities..."):
                wd_results = batch_wikidata_lookup(lookup_ents[:12])
                st.session_state["wikidata_results"] = wd_results

        wd_results = st.session_state.get("wikidata_results", {})

        if wd_results:
            found_n, total_n, coverage_pct = wikidata_coverage_score(adv_ents_wd, wd_results)

            # KPI Row
            wd1, wd2, wd3 = st.columns(3)
            wd1.metric("🌍 Wikidata Coverage", f"{coverage_pct}%", help="% of page entities found on Wikidata")
            wd2.metric("✅ Entities Found", f"{found_n}/{total_n}")
            wd3.metric("📊 Coverage Rating", "Strong" if coverage_pct >= 70 else "Moderate" if coverage_pct >= 40 else "Weak")

            st.write("")
            st.markdown('<div class="section-header">📋 Entity Wikidata Records</div>', unsafe_allow_html=True)

            for ent, result in wd_results.items():
                if result and result.get("found"):
                    st.markdown(f"""
                    <div style="background:#161b22;border:1px solid #30363d;border-radius:8px;padding:12px 16px;margin-bottom:8px;">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <span style="font-weight:600;color:#e6edf3;">{ent}</span>
                            <span class="signal-badge badge-found">✅ Found on Wikidata</span>
                        </div>
                        <div style="font-size:0.8rem;color:#4f98a3;margin-top:4px;">
                            <strong>{result.get("label","")}</strong>
                            {(" — " + result.get("description","")[:120]) if result.get("description") else ""}
                        </div>
                        <div style="font-size:0.72rem;color:#8b949e;margin-top:4px;">
                            🔗 <a href="{result.get("url","")}" target="_blank" style="color:#4f98a3;">{result.get("id","")}</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background:#161b22;border:1px solid rgba(248,81,73,0.2);border-radius:8px;padding:10px 16px;margin-bottom:6px;">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <span style="color:#8b949e;">{ent}</span>
                            <span class="signal-badge badge-missing">❌ Not Found</span>
                        </div>
                        <div style="font-size:0.75rem;color:#8b949e;margin-top:3px;">
                            Consider creating/updating a Wikidata entry for this entity to strengthen off-page authority.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # Gap recommendations
            not_found = [e for e, r in wd_results.items() if not r or not r.get("found")]
            if not_found:
                st.markdown('<div class="section-header" style="margin-top:16px;">🎯 Off-Page Entity Gap Recommendations</div>', unsafe_allow_html=True)
                recs_html = ""
                for ent in not_found[:6]:
                    recs_html += f"""
                    <div class="rec-card medium">
                        <div class="rec-title">🔴 {ent} — No Wikidata Record</div>
                        <div class="rec-desc">
                            This entity has no Wikidata entry. AI systems use Wikidata to verify entity authority.
                            Create a Wikidata item for <strong>{ent}</strong> with accurate descriptions, claims, and
                            external ID links (LinkedIn, Crunchbase, official website) to build off-page entity authority.
                        </div>
                    </div>
                    """
                st.markdown(recs_html, unsafe_allow_html=True)

            # Three-layer model visualization
            st.markdown('<div class="section-header" style="margin-top:16px;">🏗️ 3-Layer Entity Architecture</div>', unsafe_allow_html=True)
            layer_data = {
                "Layer": ["On-Page Entities", "Wikidata Entities", "Structured Layer (Schema)"],
                "Description": [
                    "Entities mentioned in your content text",
                    "Entities with Wikidata knowledge graph records",
                    "Entities marked up via JSON-LD / Schema.org"
                ],
                "Your Status": [
                    f"✅ {sum(len(v) for k,v in adv_ents_wd.items() if k not in ('Years','Statistics'))} entities detected",
                    f"{'✅' if coverage_pct >= 60 else '⚠️'} {coverage_pct}% Wikidata coverage",
                    "⚠️ Analyse HTML source for schema markup"
                ],
                "Priority": ["Baseline", "High Impact", "High Impact"]
            }
            df_layers = pd.DataFrame(layer_data)
            st.dataframe(df_layers, width='stretch', hide_index=True)

        else:
            st.markdown("""
            <div style="text-align:center;padding:60px;color:#8b949e;">
                <div style="font-size:2.5rem;margin-bottom:10px;">🌍</div>
                <div style="font-size:1rem;">Click <strong style="color:#4f98a3;">Fetch Wikidata</strong> to check entity authority</div>
                <div style="font-size:0.82rem;margin-top:6px;">Free — queries the Wikidata public API, no API key required</div>
            </div>
            """, unsafe_allow_html=True)

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
