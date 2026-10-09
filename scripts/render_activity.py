#!/usr/bin/env python3
"""Render a cyan-themed contribution calendar SVG for the profile README.

Reads the public contributions endpoint (no token required) and writes
profile/activity.svg. Used by .github/workflows/activity-graph.yml.
"""
import os
import re
import sys
import urllib.request
from datetime import datetime

USERNAME = "satyamshrivastav955-dotcom"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "profile", "activity.svg")

CELL = 12
GAP = 3
STEP = CELL + GAP
LEFT = 44
TOP = 46
MONTH_H = 18

LEVEL_COLORS = ["#101d2e", "#0e3d4f", "#0f6b7a", "#14a3a8", "#22d3ee", "#67e8f9"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def fetch_days(username: str):
    url = f"https://github.com/users/{username}/contributions"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "ignore")
    pairs = re.findall(r'data-date="([0-9-]+)"\s+data-level="([0-5])"', html, re.S)
    if not pairs:
        pairs = re.findall(r'data-date="([0-9-]+)"[^>]*?data-level="([0-5])"', html, re.S)
    if not pairs:
        raise SystemExit("could not parse contribution calendar")
    days = []
    for date_s, level_s in pairs:
        days.append((datetime.strptime(date_s, "%Y-%m-%d").date(), int(level_s)))
    days.sort(key=lambda d: d[0])
    total_m = re.search(r"([\d,]+)\s+contributions?\s+in\s+the\s+last\s+year", html)
    total = int(total_m.group(1).replace(",", "")) if total_m else sum(1 for _, lv in days if lv > 0)
    return days, total


def render(days, total: int) -> str:
    first, _ = days[0]
    # align to Sunday
    offset = first.weekday()  # Mon=0 .. Sun=6
    sunday_offset = (offset + 1) % 7
    n_weeks = (len(days) + sunday_offset + 6) // 7
    width = LEFT + n_weeks * STEP + 28
    height = TOP + 7 * STEP + 46

    out = []
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="Contribution activity graph">'
    )
    out.append("""<defs>
  <linearGradient id="hdr" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#22d3ee" stop-opacity="0.9"/>
    <stop offset="100%" stop-color="#22d3ee" stop-opacity="0.25"/>
  </linearGradient>
</defs>""")
    out.append(
        f'<rect x="0.5" y="0.5" width="{width-1}" height="{height-1}" rx="16" '
        f'fill="#0b1424" stroke="#164e63" stroke-width="1"/>'
    )
    out.append(
        f'<text x="{LEFT}" y="26" font-family="Segoe UI, Helvetica, Arial, sans-serif" '
        f'font-size="14" font-weight="700" fill="#e2e8f0">Contribution Activity Graph</text>'
    )
    out.append(
        f'<text x="{width-24}" y="26" text-anchor="end" font-family="Segoe UI, Helvetica, Arial, sans-serif" '
        f'font-size="13" font-weight="700" fill="#22d3ee">{total:,} contributions in the last year</text>'
    )
    out.append(
        f'<rect x="{LEFT}" y="34" width="{width-LEFT-24}" height="2" rx="1" fill="url(#hdr)"/>'
    )

    # month labels
    last_month = None
    for col in range(n_weeks):
        idx = col * 7 - sunday_offset
        if idx < 0 or idx >= len(days):
            continue
        d, _ = days[idx]
        if d.month != last_month:
            last_month = d.month
            x = LEFT + col * STEP
            if x + 24 < width - 24:
                out.append(
                    f'<text x="{x}" y="{TOP-6}" font-family="Segoe UI, Helvetica, Arial, sans-serif" '
                    f'font-size="10" fill="#64748b">{MONTHS[d.month-1]}</text>'
                )

    # day-of-week labels
    for row, label in enumerate(["Mon", "Wed", "Fri"]):
        y = TOP + (row * 2 + 1) * STEP + CELL - 3
        out.append(
            f'<text x="{LEFT-8}" y="{y}" text-anchor="end" font-family="Segoe UI, Helvetica, Arial, sans-serif" '
            f'font-size="9.5" fill="#64748b">{label}</text>'
        )

    # cells
    for i, (d, level) in enumerate(days):
        pos = i + sunday_offset
        col, row = pos // 7, pos % 7
        x = LEFT + col * STEP
        y = TOP + row * STEP
        out.append(
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" '
            f'fill="{LEVEL_COLORS[level]}"><title>{d.isoformat()} · level {level}</title></rect>'
        )

    # legend
    ly = height - 22
    lx = width - 24 - (6 * (CELL + 4)) - 34
    out.append(
        f'<text x="{lx-8}" y="{ly+9}" text-anchor="end" font-family="Segoe UI, Helvetica, Arial, sans-serif" '
        f'font-size="10" fill="#64748b">Less</text>'
    )
    for i, c in enumerate(LEVEL_COLORS):
        out.append(
            f'<rect x="{lx + i*(CELL+4)}" y="{ly}" width="{CELL}" height="{CELL}" rx="3" fill="{c}"/>'
        )
    out.append(
        f'<text x="{lx + 6*(CELL+4) + 6}" y="{ly+9}" font-family="Segoe UI, Helvetica, Arial, sans-serif" '
        f'font-size="10" fill="#64748b">More</text>'
    )
    out.append(
        f'<text x="{LEFT}" y="{ly+9}" font-family="Segoe UI, Helvetica, Arial, sans-serif" '
        f'font-size="10" fill="#475569">Self-hosted · updated by GitHub Actions</text>'
    )
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main() -> int:
    days, total = fetch_days(USERNAME)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(render(days, total))
    print(f"wrote {OUT} ({os.path.getsize(OUT)} bytes, {len(days)} days, total={total})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
