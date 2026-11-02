#!/usr/bin/env python3
"""Generate the README's design-system SVGs into assets/.

Run:  python scripts/build_assets.py
Palette follows GitHub dark: one blue accent, restrained secondary colours.
"""
import os
import textwrap
from xml.sax.saxutils import escape

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
os.makedirs(OUT, exist_ok=True)

BG, CARD, LINE = "#0d1117", "#161b22", "#30363d"
TXT, MUTED, DIM = "#e6edf3", "#8b949e", "#6e7681"
BLUE, GREEN, PURPLE, AMBER = "#58a6ff", "#3fb950", "#a371f7", "#d29922"
SANS = "'Segoe UI', -apple-system, 'Helvetica Neue', Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Consolas, Menlo, monospace"


def save(name, w, h, body, defs=""):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
           f'font-family="{SANS}"><defs>{defs}</defs>{body}</svg>')
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(svg)


def text(x, y, s, size=14, fill=TXT, weight=400, mono=False, anchor="start", spacing=0, extra=""):
    fam = f' font-family="{MONO}"' if mono else ""
    sp = f' letter-spacing="{spacing}"' if spacing else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}"'
            f' text-anchor="{anchor}"{fam}{sp} {extra}>{escape(s)}</text>')


def wrapped(x, y, s, chars, size=13, fill=MUTED, lh=20):
    out = []
    for i, line in enumerate(textwrap.wrap(s, chars)):
        out.append(text(x, y + i * lh, line, size, fill))
    return "".join(out)


def pills(x, y, tags, color=MUTED):
    out, cx = [], x
    for t in tags:
        w = len(t) * 6.6 + 18
        out.append(f'<rect x="{cx}" y="{y}" width="{w}" height="22" rx="11" fill="{BG}" stroke="{LINE}"/>')
        out.append(text(cx + w / 2, y + 15, t, 11, color, mono=True, anchor="middle"))
        cx += w + 8
    return "".join(out)


# ---------------------------------------------------------------- hero
def hero():
    W, H = 1000, 320
    nodes = [(700, 70), (790, 120), (880, 60), (940, 150), (850, 200), (740, 190), (660, 140), (800, 40), (920, 230)]
    edges = [(0, 1), (1, 2), (2, 3), (1, 4), (4, 3), (4, 5), (5, 6), (6, 0), (0, 7), (7, 2), (3, 8), (4, 8), (1, 5)]
    g = ""
    for a, b in edges:
        g += (f'<line x1="{nodes[a][0]}" y1="{nodes[a][1]}" x2="{nodes[b][0]}" y2="{nodes[b][1]}" '
              f'stroke="{BLUE}" stroke-opacity="0.22"/>')
    for i, (x, y) in enumerate(nodes):
        g += f'<circle cx="{x}" cy="{y}" r="4" fill="{BG}" stroke="{BLUE}" stroke-opacity="0.8"/>'
        g += (f'<circle cx="{x}" cy="{y}" r="4" fill="none" stroke="{BLUE}" stroke-opacity="0.6">'
              f'<animate attributeName="r" values="4;16;4" dur="{3 + i % 3}s" begin="{i * 0.4}s" repeatCount="indefinite"/>'
              f'<animate attributeName="stroke-opacity" values="0.6;0;0.6" dur="{3 + i % 3}s" begin="{i * 0.4}s" repeatCount="indefinite"/>'
              f'</circle>')
    stats = [("2×", "National hackathon\n1st prize"), ("4", "Peer-reviewed\npublications"),
             ("8", "Systems designed\nand shipped"), ("2", "ML engineering\ninternships")]
    s = ""
    for i, (n, l) in enumerate(stats):
        x = 48 + i * 170
        if i:
            s += f'<line x1="{x - 24}" y1="244" x2="{x - 24}" y2="288" stroke="{LINE}"/>'
        s += text(x, 268, n, 30, TXT, 700)
        for j, ln in enumerate(l.split("\n")):
            s += text(x + (46 if len(n) > 1 else 28), 258 + j * 16, ln, 11.5, MUTED)
    body = (
        '<rect x=".5" y=".5" width="999" height="319" rx="16" fill="url(#bg)" stroke="#30363d"/>'
        '<rect x=".5" y=".5" width="999" height="319" rx="16" fill="url(#dots)"/>'
        + g
        + text(48, 74, "AI  &  SECURITY ENGINEER", 12, BLUE, 600, mono=True, spacing=3)
        + text(48, 138, "Satyam Shrivastav", 58, TXT, 700, extra='letter-spacing="-1.5"')
        + text(48, 178, "I build intelligent systems that perceive, reason, and prove they work.", 18, MUTED)
        + text(48, 204, "Edge AI  ·  Computer Vision  ·  Cybersecurity  ·  Robotics", 13, DIM, mono=True)
        + f'<line x1="48" y1="226" x2="620" y2="226" stroke="{LINE}"/>'
        + s)
    defs = (f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d1117"/>'
            f'<stop offset="1" stop-color="#14233a"/></linearGradient>'
            f'<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">'
            f'<circle cx="2" cy="2" r="1" fill="#ffffff" fill-opacity="0.05"/></pattern>')
    save("hero.svg", W, H, body, defs)


# ---------------------------------------------------------------- section headers
def section(slug, num, title, sub=""):
    W, H = 1000, 64
    tw = len(title) * 13.5
    body = (text(0, 40, num, 13, BLUE, 600, mono=True)
            + text(34, 40, title, 24, TXT, 700, extra='letter-spacing="-0.4"')
            + (text(34 + tw + 18, 39, sub, 13, DIM) if sub else "")
            + f'<line x1="0" y1="58" x2="1000" y2="58" stroke="{LINE}"/>'
            + f'<line x1="0" y1="58" x2="64" y2="58" stroke="{BLUE}" stroke-width="2"/>')
    save(f"sec-{slug}.svg", W, H, body)


# ---------------------------------------------------------------- project cards
def card(slug, cat, color, title, desc, tags):
    W, H = 490, 210
    body = (f'<rect x=".5" y=".5" width="489" height="209" rx="12" fill="{CARD}" stroke="{LINE}"/>'
            f'<rect x="1" y="24" width="3" height="22" rx="1.5" fill="{color}"/>'
            + f'<circle cx="26" cy="35" r="4" fill="{color}"/>'
            + text(38, 39, cat, 11, color, 600, mono=True, spacing=1.5)
            + text(466, 39, "↗", 16, DIM, anchor="end")
            + text(24, 76, title, 21, TXT, 700, extra='letter-spacing="-0.3"')
            + wrapped(24, 104, desc, 66)
            + pills(24, 168, tags))
    save(f"card-{slug}.svg", W, H, body)


# ---------------------------------------------------------------- ARGUS flagship
def argus():
    W, H = 1000, 340
    stages = [("CAMERA FEED", "RTSP · USB · file", BLUE), ("PERCEIVE", "YOLO · ByteTrack · Pose", BLUE),
              ("REASON", "Quantized Qwen2.5-VL", PURPLE), ("ALERT", "Offline · Bitchat link", GREEN)]
    s = ""
    for i, (a, b, c) in enumerate(stages):
        x = 40 + i * 240
        s += (f'<rect x="{x}" y="236" width="200" height="64" rx="10" fill="{BG}" stroke="{LINE}"/>'
              f'<rect x="{x}" y="236" width="200" height="3" rx="1.5" fill="{c}"/>'
              + text(x + 16, 264, a, 11, c, 600, mono=True, spacing=1.5)
              + text(x + 16, 284, b, 12.5, MUTED))
        if i < 3:
            ax = x + 208
            s += (f'<line x1="{ax}" y1="268" x2="{ax + 24}" y2="268" stroke="{BLUE}" stroke-width="1.5" '
                  f'stroke-dasharray="4 4"><animate attributeName="stroke-dashoffset" from="16" to="0" '
                  f'dur="1.2s" repeatCount="indefinite"/></line>'
                  f'<path d="M{ax + 24} 263 l7 5 l-7 5" fill="none" stroke="{BLUE}" stroke-width="1.5"/>')
    body = (f'<rect x=".5" y=".5" width="999" height="339" rx="16" fill="url(#g)" stroke="{LINE}"/>'
            + text(40, 54, "FLAGSHIP BUILD  ·  IN ACTIVE DEVELOPMENT", 11.5, BLUE, 600, mono=True, spacing=2)
            + text(40, 104, "ARGUS", 46, TXT, 700, extra='letter-spacing="-1"')
            + text(40, 134, "Offline AI video intelligence", 17, MUTED)
            + wrapped(40, 168, "See the scene. Understand the event. Deliver the alert. ARGUS turns camera feeds "
                      "into structured observations and event-driven alerts, running entirely on constrained "
                      "local hardware instead of the cloud.", 105, 14, MUTED, 22)
            + s)
    defs = ('<linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d1117"/>'
            '<stop offset="1" stop-color="#152238"/></linearGradient>')
    save("argus.svg", W, H, body, defs)


# ---------------------------------------------------------------- achievements
def achievements():
    W, H = 1000, 250
    panels = [
        (BLUE, "HACKATHONS", "2×", "National 1st prize", ["CIH '26", "Ikigai '26"],
         "Also: ISRO, Vicodathon, ET AI, StudAI, InnovaHack"),
        (PURPLE, "RESEARCH", "4", "Peer-reviewed papers", ["NASA journal", "GraphQL AI security"],
         "Also: MediSmart, Finance OCR"),
        (GREEN, "EXPERIENCE", "2", "ML engineering internships", ["Softron Kolhapur", "SkillOrbit"],
         "Also: AWS and Fintech consultant credentials"),
    ]
    body = ""
    for i, (c, lab, big, cap, items, more) in enumerate(panels):
        x = i * 340
        body += (f'<rect x="{x + .5}" y=".5" width="319" height="249" rx="12" fill="{CARD}" stroke="{LINE}"/>'
                 f'<rect x="{x + 1}" y="24" width="3" height="22" rx="1.5" fill="{c}"/>'
                 + text(x + 26, 40, lab, 11, c, 600, mono=True, spacing=2)
                 + text(x + 24, 106, big, 54, TXT, 700, extra='letter-spacing="-2"')
                 + text(x + 24 + len(big) * 33 + 14, 100, cap, 13, MUTED)
                 + f'<line x1="{x + 24}" y1="130" x2="{x + 296}" y2="130" stroke="{LINE}"/>')
        for j, it in enumerate(items):
            body += (f'<circle cx="{x + 30}" cy="{157 + j * 26 - 4}" r="3" fill="{c}"/>'
                     + text(x + 44, 157 + j * 26, it, 14, TXT, 500))
        body += text(x + 24, 226, more, 11.5, DIM)
    save("achievements.svg", W, H, body)


def main():
    hero()
    for slug, num, title, sub in [
        ("about", "01", "About", ""),
        ("glance", "02", "GitHub at a Glance", ""),
        ("snake", "03", "Contribution Activity", "the snake is hungry"),
        ("breakdown", "04", "Detailed Profile Breakdown", ""),
        ("trophies", "05", "Trophies", ""),
        ("stack", "06", "Tech Stack", ""),
        ("work", "07", "Selected Work", "systems with evidence behind them"),
        ("achievements", "08", "Achievements", ""),
        ("quote", "09", "Dev Quote of the Day", ""),
    ]:
        section(slug, num, title, sub)
    argus()
    card("callshield", "SECURITY  ·  MULTIMODAL", PURPLE, "CallShield",
         "Scam and impersonation defense. Fuses synthetic-voice, speaker and scam-language signals through a "
         "LangGraph workflow into an explainable risk summary.", ["LangGraph", "PyTorch", "Android"])
    card("graphql", "SECURITY  ·  API", PURPLE, "GraphQL-Sentinel",
         "Runtime GraphQL security gateway. Analyses each operation against configurable policies and explains "
         "exactly why a request was blocked. Backed by a published paper.", ["React", "Policy engine", "Paper"])
    card("nids", "SECURITY  ·  ML", PURPLE, "Hybrid AI NIDS",
         "Network intrusion detection from four fused models (RF, autoencoder, Isolation Forest, LSTM) with PSI "
         "drift monitoring and a SOC dashboard on CICIDS2017.", ["FastAPI", "React", "CICIDS2017"])
    card("robot", "ROBOTICS  ·  AGENTS", AMBER, "Language-to-Action Robot Agent",
         "A local LLM plans a 6-DOF arm task in MuJoCo, then a ground-truth verifier checks the real outcome and "
         "retries from measured error.", ["MuJoCo", "Local LLM", "IK control"])
    card("face", "PROVENANCE  ·  WEB3", GREEN, "Face Blockchain Verification",
         "Tamper-evident image provenance. Similarity evidence is canonicalized into a SHA-256 digest anchored "
         "by a Solidity registry on Base Sepolia.", ["Solidity", "SFace", "Base Sepolia"])
    card("taskorbit", "PRODUCT  ·  FULL-STACK", BLUE, "TaskOrbit",
         "Role-aware delivery workspace: kanban with submission and revision cycles, deadline conflict detection "
         "and versioned deliverables.", ["React", "TypeScript", "Firebase"])
    card("student", "ML  ·  EXPLAINABLE", GREEN, "Student Performance Intelligence",
         "Explainable academic risk prediction with TreeSHAP, DiCE counterfactuals and Fairlearn auditing, "
         "backed by a model card and tests.", ["scikit-learn", "SHAP", "Streamlit"])
    card("more", "ALSO BUILDING", BLUE, "More on GitHub",
         "bias-aware-360-review-system (n8n + LLM agents), retailiq-inventory-system and VoiceShield. "
         "Browse every repository on my profile.", ["n8n", "LLM agents", "Inventory"])
    achievements()


if __name__ == "__main__":
    main()
