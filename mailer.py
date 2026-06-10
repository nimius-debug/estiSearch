#!/usr/bin/env python3
"""
Weekly HTML email report for Skin by Laura Lo.

Calls generate_ideas(), parses the structured output, renders a clean
HTML email, and sends it via SMTP.

Required environment variables:
  ANTHROPIC_API_KEY  — Anthropic API key
  EMAIL_RECIPIENT    — destination address
  EMAIL_SENDER       — from address
  SMTP_PASS          — SMTP password / Gmail app password

Optional environment variables (defaults to Gmail):
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


# ── Brand palette ─────────────────────────────────────────────────────────────

C = {
    "bg":           "#faf7f5",
    "card":         "#ffffff",
    "header":       "#1a1a1a",
    "accent":       "#c4846c",
    "accent_light": "#f5ede8",
    "text":         "#1a1a1a",
    "muted":        "#6b7280",
    "border":       "#e5e7eb",
    # section colors
    "trend_bg":     "#f0f9f5",  "trend_b":  "#34a37e",
    "hook_bg":      "#fff8ec",  "hook_b":   "#f59e0b",
    "break_bg":     "#f4f4ff",  "break_b":  "#6366f1",
    "why_bg":       "#fdf4ff",  "why_b":    "#9333ea",
    "cap_bg":       "#fff5f0",  "cap_b":    "#c4846c",
}

PLATFORM_COLORS = {
    "TikTok":                   ("#010101", "#ffffff"),
    "Instagram Reels":          ("#e1306c", "#ffffff"),
    "Both":                     ("#7c3aed", "#ffffff"),
    "TikTok + Instagram Reels": ("#7c3aed", "#ffffff"),
}

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
    """Convert plain section text to inline HTML with Step highlights."""
    html = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        m = re.match(r"^(Step \d+ —)\s*(.*)", s)
        if m:
            html.append(
                f'<div style="margin:5px 0;padding:6px 10px;background:#fff;'
                f'border-left:3px solid {C["border"]};border-radius:0 4px 4px 0;">'
                f'<strong style="color:{C["text"]};">{esc(m.group(1))}</strong> '
                f'{esc(m.group(2))}</div>'
            )
        else:
            html.append(f'<p style="margin:5px 0;line-height:1.65;">{esc(s)}</p>')
    return "\n".join(html)


def section_html(key: str, content: str, bg: str, border: str, label: str = "") -> str:
    title = label or key
    return f"""
    <div style="margin:10px 0;border-radius:6px;overflow:hidden;
                border-left:4px solid {border};background:{bg};">
      <div style="padding:7px 14px 3px;font-size:10px;font-weight:700;
                  letter-spacing:0.09em;text-transform:uppercase;color:{border};">
        {title}
      </div>
      <div style="padding:3px 14px 11px;font-size:13.5px;color:#374151;">
        {render_body(content)}
      </div>
    </div>"""


def idea_card_html(idea: dict, n: int) -> str:
    pb_bg, pb_fg = PLATFORM_COLORS.get(idea["platform"], ("#6b7280", "#fff"))
    s = idea.get("sections", {})

    body = ""
    if s.get("TREND PATTERN"):
        body += section_html("TREND PATTERN", s["TREND PATTERN"],
                             C["trend_bg"], C["trend_b"])
    if s.get("HOOK"):
        body += section_html("HOOK", s["HOOK"],
                             C["hook_bg"], C["hook_b"], label="HOOK — first 2–3 seconds")
    if s.get("VIDEO BREAKDOWN"):
        body += section_html("VIDEO BREAKDOWN", s["VIDEO BREAKDOWN"],
                             C["break_bg"], C["break_b"])
    if s.get("WHY IT WORKS"):
        body += section_html("WHY IT WORKS", s["WHY IT WORKS"],
                             C["why_bg"], C["why_b"])
    if s.get("CAPTION"):
        body += section_html("CAPTION", s["CAPTION"],
                             C["cap_bg"], C["cap_b"])

    return f"""
  <div style="background:{C['card']};border-radius:10px;margin:18px 0;
              border:1px solid {C['border']};overflow:hidden;">
    <table width="100%" cellpadding="0" cellspacing="0">
      <tr>
        <td style="background:{C['header']};padding:14px 18px;">
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td width="32" valign="middle">
                <div style="background:{C['accent']};color:#fff;font-size:12px;font-weight:700;
                            width:26px;height:26px;border-radius:50%;text-align:center;
                            line-height:26px;">{n}</div>
              </td>
              <td valign="middle" style="padding-left:10px;">
                <span style="color:#fff;font-size:15px;font-weight:700;">
                  {esc(idea['title'])}
                </span>
              </td>
              <td align="right" valign="middle" style="white-space:nowrap;padding-left:12px;">
                <span style="background:{pb_bg};color:{pb_fg};font-size:10px;font-weight:700;
                             padding:3px 10px;border-radius:20px;letter-spacing:0.04em;">
                  {esc(idea['platform'])}
                </span>
              </td>
            </tr>
          </table>
        </td>
      </tr>
      <tr>
        <td style="padding:14px 18px 18px;">{body}</td>
      </tr>
    </table>
  </div>"""


def trend_pulse_section_html(title: str, color: str, items: list) -> str:
    rows = "".join(
        f'<tr><td style="padding:3px 0;font-size:12.5px;color:#374151;'
        f'border-bottom:1px solid {C["border"]};">'
        f'<strong>{esc(item if isinstance(item, str) else item["name"])}</strong>'
        + (f' <span style="color:{C["muted"]};">— {esc(item["pattern"])}</span>'
           if isinstance(item, dict) else "")
        + "</td></tr>"
        for item in items
    )
    return f"""
  <td width="50%" valign="top" style="padding:6px;">
    <div style="background:#f9fafb;border-radius:8px;border-top:3px solid {color};
                padding:12px 14px;">
      <div style="font-size:10px;font-weight:700;letter-spacing:0.09em;
                  text-transform:uppercase;color:{color};margin-bottom:8px;">{esc(title)}</div>
      <table width="100%" cellpadding="0" cellspacing="0">{rows}</table>
    </div>
  </td>"""


def trend_pulse_html() -> str:
    month = datetime.now().strftime("%B %Y").upper()

    col_a = trend_pulse_section_html("TikTok — Audio", "#010101",
                                     TIKTOK_TRENDS["audio_formats"])
    col_b = trend_pulse_section_html("TikTok — Viral Formats", "#2563eb",
                                     TIKTOK_TRENDS["viral_formats"])
    col_c = trend_pulse_section_html("Instagram — Audio", "#e1306c",
                                     INSTAGRAM_TRENDS["formats"])
    col_d = trend_pulse_section_html("Instagram — Viral Formats", "#9333ea",
                                     INSTAGRAM_TRENDS["viral_formats"])
    col_e_inner = trend_pulse_section_html("Hot Skincare Topics", C["accent"],
                                           TIKTOK_TRENDS["skincare_topics"])
    col_e = col_e_inner.replace('width="50%"', 'width="100%"')

    return f"""
  <div style="background:{C['card']};border-radius:10px;margin:18px 0;
              border:1px solid {C['border']};overflow:hidden;">
    <div style="background:{C['accent']};padding:12px 18px;">
      <span style="color:#fff;font-size:13px;font-weight:700;letter-spacing:0.05em;">
        TREND PULSE — {month}
      </span>
    </div>
    <div style="padding:12px 12px 14px;">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>{col_a}{col_b}</tr>
        <tr>{col_c}{col_d}</tr>
        <tr><td colspan="2">{col_e}</td></tr>
      </table>
    </div>
  </div>"""


# ── Full email builder ────────────────────────────────────────────────────────

def build_html(ideas_raw: str) -> str:
    ideas    = parse_ideas(ideas_raw)
    date_str = datetime.now().strftime("%B %d, %Y")
    week_num = datetime.now().isocalendar()[1]
    cards    = "\n".join(idea_card_html(idea, i + 1) for i, idea in enumerate(ideas))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Content Ideas — Skin by Laura Lo</title>
</head>
<body style="margin:0;padding:0;background:{C['bg']};
             font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;">
<div style="max-width:620px;margin:0 auto;padding:24px 16px;">

  <!-- Header -->
  <div style="background:{C['header']};border-radius:10px;padding:30px 24px;
              text-align:center;margin-bottom:16px;">
    <div style="font-size:10px;letter-spacing:0.14em;color:{C['accent']};
                text-transform:uppercase;margin-bottom:8px;">Weekly Content Strategy</div>
    <h1 style="margin:0 0 8px;font-size:26px;font-weight:700;color:#fff;letter-spacing:0.02em;">
      Skin by Laura Lo
    </h1>
    <p style="margin:0;font-size:12px;color:#9ca3af;">
      Week {week_num} &nbsp;·&nbsp; {date_str} &nbsp;·&nbsp; 6 original ideas
    </p>
  </div>

  <!-- Intro strip -->
  <div style="background:{C['accent_light']};border-radius:8px;padding:13px 18px;
              border-left:4px solid {C['accent']};font-size:13.5px;
              color:#374151;line-height:1.6;margin-bottom:4px;">
    Fresh ideas generated from this week's TikTok + Instagram trend intelligence.
    Each idea is ready to film — hook, breakdown, and caption included.
  </div>

  <!-- Trend Pulse -->
  {trend_pulse_html()}

  <!-- Ideas header -->
  <div style="font-size:10px;font-weight:700;letter-spacing:0.1em;color:{C['muted']};
              text-transform:uppercase;margin:20px 0 4px;">
    This Week's Content Ideas
  </div>

  <!-- Idea cards -->
  {cards}

  <!-- Footer -->
  <div style="text-align:center;padding:22px 0 8px;font-size:11px;
              color:{C['muted']};line-height:1.9;border-top:1px solid {C['border']};
              margin-top:16px;">
    Delivered every Monday. Run
    <code style="background:#e5e7eb;padding:1px 6px;border-radius:3px;font-size:11px;">
      python strategist.py
    </code>
    anytime for a fresh batch.<br>
    <span style="color:{C['accent']};font-weight:600;">Skin by Laura Lo</span>
    &nbsp;·&nbsp; Barrier-first. Always.
  </div>

</div>
</body>
</html>"""


# ── Sender ────────────────────────────────────────────────────────────────────

SENDER    = "jorgegil9706@gmail.com"
RECIPIENT = "skinbylauralo@gmail.com"


def send(html: str, subject: str) -> None:
    sender    = os.environ.get("EMAIL_SENDER", SENDER)
    recipient = os.environ.get("EMAIL_RECIPIENT", RECIPIENT)
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
