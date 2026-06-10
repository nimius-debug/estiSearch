#!/usr/bin/env python3
"""
Viral Content Strategist — Skin by Laura Lo
Reads current TikTok/Instagram trends, finds patterns, generates original video ideas.

Usage:
    python strategist.py                     # generate ideas with built-in trends
    python strategist.py --save              # also save output to ideas_MMDD.txt
    python strategist.py --add-trend "..."   # inject your own trend note
"""

import os
import sys
import argparse
from datetime import datetime
import anthropic

# ── Brand DNA ────────────────────────────────────────────────────────────────

BRAND_ESSENCE = """
Skin by Laura Lo helps people stop guessing with their skin and start healing
through custom, barrier-first skincare, Korean fusion treatments, acne education,
sensitive skin support, pigmentation guidance, and honest esthetician care.
"""

BRAND_VOICE = "Warm, expert, honest, conversational, no-BS, nurturing, elevated, relatable."

# ── Trend Intelligence (Updated June 2026) ───────────────────────────────────

TIKTOK_TRENDS = {
    "audio_formats": [
        {
            "name": "'and Emily… that's all' audio",
            "pattern": "Compare two approaches — one clearly superior. Works for myth-busting and product comparisons.",
        },
        {
            "name": "Bob Ross 'talent is a pursued interest' audio",
            "pattern": "Before/after skill-progression clips. Glow-ups, skin journeys, learning curves.",
        },
        {
            "name": "Josh Fawaz 'Like a Prayer' remix",
            "pattern": "Summer 2026 anthem. Drives aesthetic slow-motion montages and transformation reels.",
        },
        {
            "name": "Charli XCX 'Rock Music'",
            "pattern": "Stuck-frame glitch edit — freeze, text pop, resume. High energy contrast content.",
        },
        {
            "name": "'wow, ok' acting-range challenge",
            "pattern": "No-audio breakout format. Deadpan reaction to something wild or surprising.",
        },
    ],
    "content_patterns": [
        "Realism over fantasy — raw, behind-the-curtain content outperforms polished",
        "Curiosity-driven discovery — audiences verify products/services on TikTok before buying",
        "Skill-progression before/afters trending hard",
        "Quick-to-recreate, easy-to-remix formats dominate reach",
        "Audiences moving away from aspirational → toward relatable + real",
        "Comment sections engineered as part of the content strategy",
    ],
    "skincare_topics": [
        "Skin longevity (replacing 'anti-aging') — ingredient-literate audiences want this language",
        "Barrier repair + ceramides + lipids going mainstream",
        "Korean beauty dominance: Korean lash lift up 20,082% in searches",
        "Spicule serum (marine sponge) viral for tactile 'this is working' sensation content",
        "Climate-adaptive skincare emerging as a conversation",
        "Beauty of Joseon Rice Sunscreen SPF 50+ viral moment",
        "TikTok is now the #1 beauty search engine (65% Gen Z, 55% Millennials discover here)",
    ],
}

INSTAGRAM_TRENDS = {
    "formats": [
        {
            "name": "'I Am Home' trend — Michael Jackson 'Beat It'",
            "pattern": "Strut confidently into your third place. Works perfectly for the treatment room reveal.",
        },
        {
            "name": "'Seeing if the Algorithm Prefers' format",
            "pattern": "High-effort edit vs. deadpan static shot. Let comments vote. Self-aware, meta humor.",
        },
        {
            "name": "'I Have Therapy' POV",
            "pattern": "Cut from the excuse ('can't today') to what actually restores you. Relatable + personal.",
        },
        {
            "name": "Justin Bieber 'EVERYTHING HALLELUJAH' listing Reels",
            "pattern": "Brand-friendly listing format — rapid text overlays of things that belong together.",
        },
        {
            "name": "Ariana Grande 'Hate That I Made You Love Me' situationship format",
            "pattern": "Apply breakup-song energy to skin situationships — bad habits, toxic products, regrets.",
        },
    ],
    "content_behaviors": [
        "Raw, unpolished content outperforming high-production posts",
        "Strong hooks in first 0-2 seconds = everything",
        "Comment sections engineered as part of the content (ask, provoke, invite)",
        "Short-form Reels dominating reach over long-form",
        "Save-worthy carousels for education (pigmentation maps, acne guides, routines)",
        "Self-aware + meta humor builds credibility and relatability",
    ],
}

# ── Core Patterns Across Both Platforms ──────────────────────────────────────

CROSS_PLATFORM_PATTERNS = [
    "AUTHENTICITY WINS: unfiltered, honest, expert POV outperforms curated aesthetic",
    "BEFORE/AFTER still dominates but needs a fresh emotional angle, not just visual",
    "EDUCATION AS ENTERTAINMENT: teach something nobody told them — make it feel like a secret",
    "COMMUNITY PROVOCATION: posts that generate comments get pushed by both algorithms",
    "SAVE-BAIT: checklists, myth-busters, 'screenshot this' moments drive saves = reach",
    "SOUND-IDENTITY: owning a recurring audio or sound signature builds brand recall",
    "SKIN AS IDENTITY: people relate to their skin journey emotionally, not just physically",
]

# ── System Prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = f"""You are the Viral Content Strategist for Skin by Laura Lo, a licensed esthetician brand.

BRAND ESSENCE:
{BRAND_ESSENCE}

BRAND VOICE: {BRAND_VOICE}

YOUR ROLE: Transform trend intelligence into original, on-brand video ideas that feel made for Skin by Laura Lo — not generic skincare content.

RULES — NEVER DO:
- Copy the trend examples directly
- Give generic skincare ideas any esthetician could post
- Give safe, boring educational posts
- Simply map "use this audio for barrier repair" without a real concept
- Use overly clinical or corporate language

ALWAYS CREATE ideas that feel:
✓ Emotionally relatable — the viewer feels seen
✓ Slightly bold — takes a real stance or reveals something unexpected
✓ Expert-led — Laura's POV and authority comes through
✓ Warm — never cold, never preachy
✓ Shareable — someone would send this to a friend
✓ Saveable — someone would screenshot or bookmark this
✓ Visually interesting — easy to picture, not talking-head default
✓ True to Skin by Laura Lo — barrier-first, Korean fusion, acne, sensitive skin, pigmentation"""


def build_trend_brief(extra_trend: str = None) -> str:
    """Compile the full trend brief as a readable string."""
    lines = []

    lines.append("═══ TIKTOK TRENDS — JUNE 2026 ═══\n")
    lines.append("TRENDING AUDIO & FORMATS:")
    for item in TIKTOK_TRENDS["audio_formats"]:
        lines.append(f"  • {item['name']}")
        lines.append(f"    → {item['pattern']}")
    lines.append("")
    lines.append("CONTENT PATTERNS:")
    for p in TIKTOK_TRENDS["content_patterns"]:
        lines.append(f"  • {p}")
    lines.append("")
    lines.append("HOT SKINCARE TOPICS:")
    for t in TIKTOK_TRENDS["skincare_topics"]:
        lines.append(f"  • {t}")

    lines.append("\n═══ INSTAGRAM REELS TRENDS — JUNE 2026 ═══\n")
    lines.append("TRENDING FORMATS:")
    for item in INSTAGRAM_TRENDS["formats"]:
        lines.append(f"  • {item['name']}")
        lines.append(f"    → {item['pattern']}")
    lines.append("")
    lines.append("PLATFORM BEHAVIORS:")
    for b in INSTAGRAM_TRENDS["content_behaviors"]:
        lines.append(f"  • {b}")

    lines.append("\n═══ CROSS-PLATFORM PATTERNS ═══\n")
    for p in CROSS_PLATFORM_PATTERNS:
        lines.append(f"  • {p}")

    if extra_trend:
        lines.append("\n═══ YOUR ADDED TREND NOTE ═══\n")
        lines.append(f"  {extra_trend}")

    return "\n".join(lines)


def generate_ideas(extra_trend: str = None) -> str:
    """Call Claude API and return formatted content ideas."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY not set.\n  Run: export ANTHROPIC_API_KEY=your_key_here"
        )

    client = anthropic.Anthropic(api_key=api_key)
    trend_brief = build_trend_brief(extra_trend)

    user_prompt = f"""Here is the current trend intelligence report:

{trend_brief}

Generate 6 original content ideas for Skin by Laura Lo.

For each idea use this exact format:

────────────────────────────────────────
[NUMBER]. [CONCEPT TITLE IN CAPS]
Platform: TikTok / Instagram Reels / Both
Trend it taps: [which audio/format/pattern]
First 3 seconds: [exactly what the viewer sees and hears — be specific]
Video breakdown:
  1. [beat 1]
  2. [beat 2]
  3. [beat 3]
  4. [beat 4 if needed]
Caption direction: [tone + a key phrase or question to open with]
Why it performs: [one sharp sentence — the scroll-stop reason]
────────────────────────────────────────

Mix emotional, myth-busting, behind-the-scenes, and bold-take styles.
Vary between TikTok and Instagram. Make each one feel unmistakably Skin by Laura Lo."""

    message = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=2500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    return message.content[0].text


# ── CLI Output ────────────────────────────────────────────────────────────────

def print_header():
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║        SKIN BY LAURA LO — VIRAL CONTENT STRATEGIST       ║")
    print(f"║                   Trend Report: June {datetime.now().year}                ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()


def print_trend_pulse():
    print("── TREND PULSE ──────────────────────────────────────────────")
    print()
    print("  TIKTOK")
    print("  › 'and Emily...that's all' — contrast/comparison format")
    print("  › Bob Ross audio — skill-progression before/afters")
    print("  › Charli XCX 'Rock Music' — glitch-frame edits")
    print("  › 'wow, ok' challenge — no-audio deadpan reactions")
    print("  › Realism > polish. Raw beats curated. Always.")
    print("  › Skin longevity replacing 'anti-aging' in search")
    print("  › Korean beauty + barrier repair = mainstream moment")
    print()
    print("  INSTAGRAM REELS")
    print("  › 'I Am Home' (Beat It) — strut into your third place")
    print("  › 'I Have Therapy' POV — what actually restores you")
    print("  › Algorithm Prefers format — meta self-aware humor")
    print("  › Bieber 'EVERYTHING HALLELUJAH' — listing Reels")
    print("  › Grande situationship audio — toxic product breakups")
    print("  › Unpolished > high-production for reach right now")
    print()
    print("  CROSS-PLATFORM PATTERNS")
    print("  › Before/after needs emotional angle, not just visual")
    print("  › Save-bait: myth-busters, checklists, 'screenshot this'")
    print("  › Comment provocation = algorithm fuel on both platforms")
    print()
    print("─" * 62)
    print()


def save_output(content: str) -> str:
    """Save ideas to a dated text file. Returns filename."""
    filename = f"ideas_{datetime.now().strftime('%m%d_%H%M')}.txt"
    filepath = os.path.join(os.path.dirname(__file__), filename)
    header = (
        f"SKIN BY LAURA LO — VIRAL CONTENT IDEAS\n"
        f"Generated: {datetime.now().strftime('%B %d, %Y %H:%M')}\n"
        f"{'─' * 60}\n\n"
    )
    with open(filepath, "w") as f:
        f.write(header + content)
    return filename


def main():
    parser = argparse.ArgumentParser(
        description="Viral Content Strategist for Skin by Laura Lo"
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save output to a dated .txt file",
    )
    parser.add_argument(
        "--add-trend",
        metavar="TREND",
        help="Add a custom trend note to the brief (e.g. 'competitor just posted XYZ')",
    )
    args = parser.parse_args()

    print_header()
    print_trend_pulse()

    print("  Generating content ideas for Skin by Laura Lo...")
    print()

    try:
        ideas = generate_ideas(extra_trend=args.add_trend)

        print("── YOUR CONTENT IDEAS ───────────────────────────────────────")
        print()
        print(ideas)
        print()
        print("─" * 62)

        if args.save:
            filename = save_output(ideas)
            print(f"\n  Saved to: {filename}")

        print()
        print("  Run again for a fresh batch. Trends update monthly.")
        print("  Add --save to keep a record. Add --add-trend 'note' to inject context.")
        print()

    except EnvironmentError as e:
        print(f"\n  ERROR: {e}\n")
        sys.exit(1)
    except anthropic.AuthenticationError:
        print("\n  ERROR: Invalid API key. Check your ANTHROPIC_API_KEY.\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n  ERROR: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
