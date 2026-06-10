#!/usr/bin/env python3
"""
Weekly HTML email report for Skin by Laura Lo.

Calls generate_ideas(), parses the structured output, renders a simple
mobile-first HTML report, and sends it via SMTP.

Required environment variables:
  ANTHROPIC_API_KEY  — Anthropic API key
  SMTP_PASS          — SMTP password / Gmail app password

Optional environment variables:
  EMAIL_SENDER       — default: jorgegil9706@gmail.com
  EMAIL_RECIPIENT    — default: skinbylauralo@gmail.com
  SMTP_HOST          — default: smtp.gmail.com
  SMTP_PORT          — default: 587
  SMTP_USER          — default: EMAIL_SENDER
"""

import os
import re
import smtplib
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from strategist import generate_ideas, TIKTOK_TRENDS, INSTAGRAM_TRENDS


ACCENT = "#b5705a"   # terracotta brand color
DARK   = "#1a1a1a"
TEXT   = "#333333"
MUTED  = "#777777"
LINE   = "#e2e2e2"

SECTION_KEYS = ["TREND PATTERN", "HOOK", "VIDEO BREAKDOWN", "WHY IT WORKS", "CAPTION"]
DIVIDER_RE   = re.compile(r"─{10,}")


# ── Parser ────────────────────────────────────────────────────────────────────

def parse_ideas(raw: str) -> list[dict]:
    """Split the model's structured text into a list of idea dicts."""
    ideas = []

    for block in DIVIDER_RE.split(raw):
        lines = block.strip().splitlines()
        if not lines:
            continue

        idea = {"title": "", "platform": "", "sections": {}}
        current_key  = None
        current_lines: list[str] = []

        for line in lines:
            stripped = line.strip()

            # Skip box-drawing characters
            if any(ch in stripped for ch in ("╔", "╗", "╚", "╝", "═")):
                continue

            # Title:  "  1. CONCEPT TITLE"
            if not idea["title"]:
                m = re.match(r"^\s+\d+\.\s*(.+)$", line)
                if m:
                    idea["title"] = m.group(1).strip()
                    continue

            # Platform line
            if stripped.startswith("Platform:"):
                idea["platform"] = stripped.split("Platform:", 1)[1].strip()
                continue

            # Section header (startswith handles "HOOK  (first 2–3 seconds)" etc.)
            matched = next((k for k in SECTION_KEYS if stripped.startswith(k)), None)
            if matched:
                if current_key and current_lines:
                    idea["sections"][current_key] = "\n".join(current_lines).strip()
                current_key   = matched
                current_lines = []
            elif current_key is not None:
                current_lines.append(line)

        if current_key and current_lines:
            idea["sections"][current_key] = "\n".join(current_lines).strip()

        if idea["title"]:
            ideas.append(idea)

    return ideas


# ── HTML helpers ──────────────────────────────────────────────────────────────

def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_body(text: str) -> str:
    """Section text → simple paragraphs. Step lines get a bold prefix."""
    out = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        m = re.match(r"^(Step \d+) —\s*(.*)", s)
        if m:
            out.append(
                f'<p style="margin:4px 0;font-size:13px;line-height:1.6;color:{TEXT};">'
                f'<strong>{esc(m.group(1))}.</strong> {esc(m.group(2))}</p>'
            )
        else:
            out.append(
                f'<p style="margin:4px 0;font-size:13px;line-height:1.6;color:{TEXT};">'
                f'{esc(s)}</p>'
            )
    return "\n".join(out)


def section_html(label: str, content: str) -> str:
    return f"""
      <div style="margin:14px 0 0;">
        <div style="font-size:11px;font-weight:700;letter-spacing:0.08em;
                    color:{ACCENT};margin-bottom:2px;">{label}</div>
        {render_body(content)}
      </div>"""


def idea_html(idea: dict, n: int) -> str:
    s = idea.get("sections", {})
    body = ""
    if s.get("TREND PATTERN"):
        body += section_html("TREND PATTERN", s["TREND PATTERN"])
    if s.get("HOOK"):
        body += section_html("HOOK — FIRST 2–3 SECONDS", s["HOOK"])
    if s.get("VIDEO BREAKDOWN"):
        body += section_html("VIDEO BREAKDOWN", s["VIDEO BREAKDOWN"])
    if s.get("WHY IT WORKS"):
        body += section_html("WHY IT WORKS", s["WHY IT WORKS"])
    if s.get("CAPTION"):
        body += section_html("CAPTION", s["CAPTION"])

    return f"""
  <div style="padding:18px 0;border-top:2px solid {DARK};">
    <div style="font-size:11px;font-weight:600;letter-spacing:0.08em;
                color:{MUTED};text-transform:uppercase;">
      Idea {n} &nbsp;·&nbsp; {esc(idea['platform'])}
    </div>
    <div style="font-size:16px;font-weight:700;color:{DARK};
                line-height:1.35;margin-top:3px;">{esc(idea['title'])}</div>
    {body}
  </div>"""


def trend_list_html(title: str, items: list) -> str:
    rows = []
    for item in items:
        if isinstance(item, dict):
            rows.append(
                f'<p style="margin:3px 0;font-size:12px;line-height:1.55;color:{TEXT};">'
                f'&bull; <strong>{esc(item["name"])}</strong> — '
                f'<span style="color:{MUTED};">{esc(item["pattern"])}</span></p>'
            )
        else:
            rows.append(
                f'<p style="margin:3px 0;font-size:12px;line-height:1.55;color:{TEXT};">'
                f'&bull; {esc(item)}</p>'
            )
    return f"""
    <div style="margin:14px 0 0;">
      <div style="font-size:11px;font-weight:700;letter-spacing:0.08em;
                  color:{DARK};margin-bottom:3px;">{esc(title)}</div>
      {"".join(rows)}
    </div>"""


def trend_pulse_html() -> str:
    month = datetime.now().strftime("%B %Y")
    return f"""
  <div style="padding:18px 0;border-top:2px solid {DARK};">
    <div style="font-size:16px;font-weight:700;color:{DARK};">
      Trend Pulse — {month}
    </div>
    {trend_list_html("TIKTOK — AUDIO", TIKTOK_TRENDS["audio_formats"])}
    {trend_list_html("TIKTOK — VIRAL FORMATS (NO AUDIO)", TIKTOK_TRENDS["viral_formats"])}
    {trend_list_html("HOT SKINCARE TOPICS", TIKTOK_TRENDS["skincare_topics"])}
    {trend_list_html("INSTAGRAM — AUDIO", INSTAGRAM_TRENDS["formats"])}
    {trend_list_html("INSTAGRAM — VIRAL FORMATS (NO AUDIO)", INSTAGRAM_TRENDS["viral_formats"])}
  </div>"""


# ── Full email builder ────────────────────────────────────────────────────────

def build_html(ideas_raw: str) -> str:
    ideas    = parse_ideas(ideas_raw)
    date_str = datetime.now().strftime("%B %d, %Y")
    week_num = datetime.now().isocalendar()[1]
    blocks   = "\n".join(idea_html(idea, i + 1) for i, idea in enumerate(ideas))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Content Ideas — Skin by Laura Lo</title>
</head>
<body style="margin:0;padding:0;background:#ffffff;word-wrap:break-word;
             -webkit-text-size-adjust:100%;
             font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;">
<div style="max-width:600px;margin:0 auto;padding:20px 16px;">

  <!-- Header -->
  <div style="padding-bottom:16px;">
    <div style="font-size:11px;letter-spacing:0.12em;color:{ACCENT};
                text-transform:uppercase;font-weight:700;">Weekly Content Report</div>
    <div style="font-size:22px;font-weight:700;color:{DARK};margin-top:4px;">
      Skin by Laura Lo
    </div>
    <div style="font-size:12px;color:{MUTED};margin-top:3px;">
      Week {week_num} &nbsp;·&nbsp; {date_str} &nbsp;·&nbsp; 6 ideas
    </div>
  </div>

  <!-- Trend Pulse -->
  {trend_pulse_html()}

  <!-- Idea blocks -->
  {blocks}

  <!-- Footer -->
  <div style="padding:16px 0;border-top:1px solid {LINE};font-size:11px;
              color:{MUTED};line-height:1.7;">
    Delivered every Monday. Run <code>python strategist.py</code> anytime for a fresh batch.<br>
    <span style="color:{ACCENT};font-weight:600;">Skin by Laura Lo</span>
    &nbsp;·&nbsp; Barrier-first. Always.
  </div>

</div>
</body>
</html>"""


# ── Sender ────────────────────────────────────────────────────────────────────

def send(html: str, subject: str) -> None:
    sender    = os.environ.get("EMAIL_SENDER", "jorgegil9706@gmail.com")
    recipient = os.environ.get("EMAIL_RECIPIENT", "skinbylauralo@gmail.com")
    host      = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    port      = int(os.environ.get("SMTP_PORT", 587))
    user      = os.environ.get("SMTP_USER", sender)
    password  = os.environ["SMTP_PASS"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"Skin by Laura Lo Strategy <{sender}>"
    msg["To"]      = recipient
    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP(host, port) as server:
        server.ehlo()
        server.starttls()
        server.login(user, password)
        server.sendmail(sender, [recipient], msg.as_string())
        print(f"  Sent to {recipient}")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    print("Generating content ideas...")
    try:
        raw = generate_ideas()
    except EnvironmentError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    print("Building email...")
    html = build_html(raw)

    week_num = datetime.now().isocalendar()[1]
    date_str = datetime.now().strftime("%B %d")
    subject  = f"Week {week_num} Content Ideas — Skin by Laura Lo ({date_str})"

    print("Sending...")
    try:
        send(html, subject)
    except KeyError as e:
        print(f"ERROR: missing env var {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
