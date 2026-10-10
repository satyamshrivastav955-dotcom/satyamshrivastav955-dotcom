#!/usr/bin/env python3
"""Render the profile's curated engineering quote as Markdown and SVG.

The workflow runs this script once per day.  Keeping the quote data and the
renderer in the repository makes the README independent of quote-widget
availability and gives the card the same visual language as the rest of the
profile.
"""

from __future__ import annotations

import argparse
import html
import random
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profile"
QUOTE_MD = PROFILE / "QUOTE.md"
QUOTE_SVG = PROFILE / "quote.svg"
HEARTBEAT = PROFILE / "HEARTBEAT.log"

QUOTES = (
    "The system is only as good as the evidence behind its decision.",
    "Detect the signal. Explain the risk. Help someone respond.",
    "A model that cannot be inspected is a model that cannot be trusted.",
    "Latency is a feature — especially when the camera is live.",
    "Verify the physical result. Do not trust the plan's description of success.",
    "Perception without reasoning is noise. Reasoning without perception is fiction.",
    "Build the pipeline, then measure the pipeline, then trust the pipeline.",
    "Explainability is not a dashboard. It is a responsibility.",
    "Offline-first means the system still works when the network does not.",
    "Code is like humor. When you have to explain it, it's bad. — Cory House",
    "First, solve the problem. Then, write the code. — John Johnson",
    "Make it work, make it right, make it fast. — Kent Beck",
    "Talk is cheap. Show me the code. — Linus Torvalds",
    "Premature optimization is the root of all evil. — Donald Knuth",
    "Programs must be written for people to read. — Harold Abelson",
    "The graph stays green when discipline stays daily.",
    "Ship small. Ship often. Ship verified.",
)


def parse_timestamp(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S UTC").replace(tzinfo=timezone.utc)


def quote_lines(quote: str) -> tuple[list[str], str]:
    body, separator, author = quote.partition(" — ")
    lines = textwrap.wrap(body, width=56, break_long_words=False, break_on_hyphens=False)
    return lines or [body], f"— {author}" if separator else ""


def render_svg(quote: str, updated: datetime) -> str:
    lines, author = quote_lines(quote)
    escaped_lines = [html.escape(line) for line in lines]
    quote_text = []
    start_y = 96 - (len(escaped_lines) - 1) * 10
    for index, line in enumerate(escaped_lines):
        quote_text.append(
            f'<tspan x="92" y="{start_y + index * 31}">{line}</tspan>'
        )
    author_svg = (
        f'<text x="92" y="168" class="author">{html.escape(author)}</text>'
        if author
        else ""
    )
    updated_label = updated.strftime("%d %b %Y · %H:%M UTC")

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="920" height="210" viewBox="0 0 920 210" role="img" aria-labelledby="title desc">
  <title id="title">Daily engineering note</title>
  <desc id="desc">{html.escape(quote)}</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#07111f"/>
      <stop offset="1" stop-color="#0b1d2b"/>
    </linearGradient>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#22d3ee"/>
      <stop offset="1" stop-color="#2dd4bf"/>
    </linearGradient>
    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <style>
    .sans {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; }}
    .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
    .label {{ font-size: 11px; font-weight: 700; letter-spacing: 2px; fill: #67e8f9; }}
    .quote {{ font-size: 22px; font-weight: 600; fill: #e2e8f0; }}
    .author {{ font-size: 13px; fill: #67e8f9; }}
    .date {{ font-size: 10px; fill: #64748b; letter-spacing: 1px; }}
  </style>
  <rect width="920" height="210" rx="14" fill="url(#bg)" stroke="#164e63"/>
  <rect x="0" y="0" width="6" height="210" rx="3" fill="url(#accent)"/>
  <text x="92" y="36" class="mono label">ENGINEERING NOTE / DAILY ROTATION</text>
  <line x1="92" y1="50" x2="828" y2="50" stroke="#17324a"/>
  <text class="sans quote">{''.join(quote_text)}</text>
  {author_svg}
  <text x="92" y="193" class="mono date">{updated_label}</text>
  <g transform="translate(760 83)" opacity="0.8">
    <circle cx="0" cy="0" r="34" fill="none" stroke="#164e63"/>
    <circle cx="0" cy="0" r="22" fill="none" stroke="#0e7490" stroke-dasharray="3 7"/>
    <circle cx="0" cy="0" r="4" fill="#67e8f9" filter="url(#glow)"/>
    <path d="M-54 0H54M0-54V54" stroke="#164e63"/>
  </g>
</svg>
'''


def write_outputs(quote: str, updated: datetime, append_heartbeat: bool) -> None:
    PROFILE.mkdir(parents=True, exist_ok=True)
    utc_label = updated.strftime("%Y-%m-%d %H:%M:%S UTC")
    ist_label = updated.astimezone(ZoneInfo("Asia/Kolkata")).strftime(
        "%Y-%m-%d %H:%M:%S IST"
    )
    QUOTE_MD.write_text(
        "# 💡 Dev Quote (daily rotation)\n\n"
        f"> {quote}\n\n"
        f"_Last updated: {utc_label} ({ist_label})_\n",
        encoding="utf-8",
    )
    QUOTE_SVG.write_text(render_svg(quote, updated), encoding="utf-8")

    if append_heartbeat:
        existing = HEARTBEAT.read_text(encoding="utf-8").splitlines() if HEARTBEAT.exists() else []
        existing.append(f"{utc_label} | {quote}")
        HEARTBEAT.write_text("\n".join(existing[-240:]) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quote", help="Use a specific quote instead of selecting one")
    parser.add_argument(
        "--updated-utc",
        help="Timestamp in YYYY-MM-DD HH:MM:SS UTC format (useful for deterministic previews)",
    )
    parser.add_argument(
        "--no-heartbeat",
        action="store_true",
        help="Render the quote without appending to HEARTBEAT.log",
    )
    args = parser.parse_args()

    quote = args.quote or random.SystemRandom().choice(QUOTES)
    updated = parse_timestamp(args.updated_utc)
    write_outputs(quote, updated, append_heartbeat=not args.no_heartbeat)
    print(f"wrote {QUOTE_MD} and {QUOTE_SVG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
