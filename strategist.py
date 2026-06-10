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

Use EXACTLY this format for each idea — no deviations:

╔══════════════════════════════════════╗
  [NUMBER]. CONCEPT TITLE IN CAPS
  Platform: TikTok / Instagram Reels / Both
╚══════════════════════════════════════╝

TREND PATTERN
  [Name of the trend/audio/format + one sentence on how the pattern works]

HOOK  (first 2–3 seconds)
  [Exact scene: what the viewer SEES and HEARS the moment it plays.
   Be cinematic and specific — camera angle, sound, text on screen.]

VIDEO BREAKDOWN
  Step 1 — [what happens]
  Step 2 — [what happens]
  Step 3 — [what happens]
  Step 4 — [what happens, if needed]

WHY IT WORKS
  [2–3 sentences. Explain the emotional or psychological reason this
   stops the scroll, drives saves/shares, and fits the algorithm right now.]

CAPTION
  Opening line: "[exact first line to use]"
  Direction: [tone note + CTA or engagement prompt]

──────────────────────────────────────────────────────

Mix emotional, myth-busting, behind-the-scenes, and bold-take content types.
Vary platforms. Every idea must feel unmistakably Skin by Laura Lo."""

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


DEMO_IDEAS = """
╔══════════════════════════════════════╗
  1. THE SKIN THAT STARTED IT ALL
  Platform: TikTok
╚══════════════════════════════════════╝

TREND PATTERN
  Bob Ross "talent is a pursued interest" audio. The format shows a raw starting
  point, then lets the progression speak — no narration needed. Authenticity is
  the whole mechanic.

HOOK  (first 2–3 seconds)
  Extreme close-up of a client's inflamed, congested skin — no filter, no
  flattering light. The Bob Ross audio drops softly. White text fades in:
  "This was month 1."

VIDEO BREAKDOWN
  Step 1 — Month 1: red, reactive, broken-out. Real. Laura's handwritten
            treatment note flashes over it: "compromised barrier. we start here."
  Step 2 — Month 2: same angle, same lighting. Skin quieting. Text: "we stopped
            fighting it."
  Step 3 — Month 3: texture smoothing, redness down. Text: "we listened instead."
  Step 4 — Month 4: calm, clear, glowing. Final text fades in:
            "this is what healing looks like." Soft hold. No CTA needed yet.

WHY IT WORKS
  The handwritten treatment note makes this feel like a real clinical story, not
  a promo — it signals expertise without bragging. The no-filter approach on the
  before shot builds instant trust with people who are tired of unrealistic
  transformations. People save this because they want to come back to it when
  their own skin feels hopeless.

CAPTION
  Opening line: "Nobody gets clear skin by adding more. Most of my clients
  needed to take away first."
  Direction: Warm + direct. End with a soft question: "Where are you right now
  in your skin journey?" to pull comments.

──────────────────────────────────────────────────────

╔══════════════════════════════════════╗
  2. SORRY, I HAVE A FACIAL
  Platform: Instagram Reels
╚══════════════════════════════════════╝

TREND PATTERN
  "I Have Therapy" POV format. Creator deflects a social obligation with
  "I have therapy" — then cuts to whatever actually restores them. The twist
  is the reveal of what "therapy" really means to them.

HOOK  (first 2–3 seconds)
  Laura faces the camera directly. She looks slightly amused. Text appears:
  "sorry I can't tonight, I have a facial." Hard cut to black — then the
  treatment room materializes in low golden light.

VIDEO BREAKDOWN
  Step 1 — Treatment room reveal: warm towel being folded in slow motion.
            No music yet. Just the soft sound of water.
  Step 2 — Steam rising from a bowl of herbs. A client's hand relaxing open.
            Text: "this is the thing I protect."
  Step 3 — Laura pressing a gua sha tool along a jawline, slow and intentional.
            Text: "one hour. no phone. no stress. just skin."
  Step 4 — End frame: the client's face, peaceful. Text:
            "this is where we actually heal." Music rises softly.

WHY IT WORKS
  The format taps straight into the current cultural moment of protecting your
  restoration rituals — it positions a facial as a non-negotiable, not a luxury.
  The golden light and sensory details (steam, warm towel, the sound of water)
  make the viewer feel the experience before they've booked it. This drives
  direct inquiries because people want to feel exactly that.

CAPTION
  Opening line: "Your skin doesn't need another product. It needs an hour where
  someone actually listens to it."
  Direction: Soft and inviting. End with: "What does your version of this look
  like?" — low-friction engagement.

──────────────────────────────────────────────────────

╔══════════════════════════════════════╗
  3. THINGS THAT DON'T BELONG ON A SENSITIVE FACE
  Platform: Instagram Reels
╚══════════════════════════════════════╝

TREND PATTERN
  Justin Bieber "EVERYTHING HALLELUJAH" rapid-listing format. Brand-friendly
  rhythm of quick cuts with text overlays — each item listed lands like a
  punctuation mark. The contrast between the list and the resolution is
  where the emotion lives.

HOOK  (first 2–3 seconds)
  Laura holds up a recognizable drugstore toner. Deadpan expression. The music
  kicks in and text flies across the screen: "and this one." The energy is
  confident, not mean.

VIDEO BREAKDOWN
  Step 1 — Rapid cuts, one product per beat: alcohol toner, fragrance serum,
            vitamin C at 20%, popular enzyme mask, exfoliating scrub. Each with
            a single brutal text overlay. Fast and rhythmic.
  Step 2 — The music slows. Laura sets everything aside. One plain gentle
            cleanser sits alone on the counter.
  Step 3 — She picks it up. Looks at camera. Text: "and then there's this."
  Step 4 — Final frame, soft smile: "Sensitive skin isn't high-maintenance.
            It's just misunderstood."

WHY IT WORKS
  Every person with reactive skin has a bathroom shelf full of the products in
  step 1 — this video makes them feel seen and slightly called out at the same
  time, which is the perfect recipe for a share. The pivot from fast to slow
  creates a satisfying emotional release. "Screenshot this" moments are built
  into the format.

CAPTION
  Opening line: "If your face is always red, it's not your skin. It's your
  products."
  Direction: Bold but not preachy. Add: "Screenshot this and audit your shelf
  tonight." — drives saves and DMs.

──────────────────────────────────────────────────────

╔══════════════════════════════════════╗
  4. "AND LAURA… THAT'S ALL"
  Platform: TikTok
╚══════════════════════════════════════╝

TREND PATTERN
  "and Emily… that's all" contrast audio. The format places two options side
  by side — one complex and overwhelming, one clear and superior. The audio
  does the editorial work so the visuals can stay simple.

HOOK  (first 2–3 seconds)
  The audio plays over a stark split screen. Left side: a complex 10-product
  flatlay under harsh white light. Right side: Laura's clean treatment table,
  one product, warm light. Text builds: "your 10-step routine… and Laura."

VIDEO BREAKDOWN
  Step 1 — Left panel pulses: clinical graphics of actives stacked on actives.
            Text: "Add more. Strip more. Push through the purge."
  Step 2 — Right panel holds steady: Laura's table, unhurried. Text:
            "What does your skin actually need right now?"
  Step 3 — Left panel fades. Right panel expands to full screen.
            Text builds slowly: "Barrier first. Always."
  Step 4 — End card on Laura's face, calm and direct:
            "Book a skin consult. We start with less."

WHY IT WORKS
  This takes a real stance in a space full of people who have been over-sold
  complexity — and it does it without attacking anyone directly. The restraint
  of the right-panel visual communicates authority better than any credential
  could. The comment section will fill with people who've been over-prescribed,
  which the algorithm will read as high-engagement content.

CAPTION
  Opening line: "I'm not against dermatologists. I'm against routines that
  treat your skin like a problem to solve."
  Direction: Confident + inviting debate. "What's the most overwhelming routine
  you've ever tried?" to spark replies.

──────────────────────────────────────────────────────

╔══════════════════════════════════════╗
  5. I BROKE UP WITH MY ROUTINE
  Platform: TikTok + Instagram Reels
╚══════════════════════════════════════╝

TREND PATTERN
  Ariana Grande "Hate That I Made You Love Me" situationship energy. The
  format maps breakup-song lyrics onto a relatable non-romantic obsession —
  the emotional logic of a bad relationship applied to something the audience
  recognizes immediately.

HOOK  (first 2–3 seconds)
  Tight shot: a well-known actives serum on the bathroom counter. Ariana's
  track drops. Laura's voice (or text): "I spent $89 on you." Long pause.
  "And you burned me every single time."

VIDEO BREAKDOWN
  Step 1 — Moody "situationship" montage: reaching for the serum at midnight,
            applying too much, face flushing red. Text: "I kept going back."
  Step 2 — The breakdown: skin close-up showing irritation. Text:
            "you were destroying my barrier and I called it purging."
  Step 3 — The pivot: two simple products on a clean counter, morning light.
            Text: "I downgraded. My skin has never been better."
  Step 4 — CTA hold: "If your skin is always reacting — DM me.
            Let's break the cycle."

WHY IT WORKS
  The situationship framing unlocks an emotional door that straight skincare
  education never reaches — people feel the guilt, the loyalty, and the relief
  of leaving a bad product, all in 30 seconds. Acne and sensitive skin audiences
  will screenshot the "purging" line specifically and share it widely. High
  save and share rate almost guaranteed.

CAPTION
  Opening line: "We need to talk about the products we keep going back to even
  when they don't treat us right."
  Direction: Funny + self-aware. End with: "Which product were you in a
  situationship with?" — comment magnet.

──────────────────────────────────────────────────────

╔══════════════════════════════════════╗
  6. I AM HOME
  Platform: Instagram Reels
╚══════════════════════════════════════╝

TREND PATTERN
  "I Am Home" format set to Michael Jackson's "Beat It." Creator struts
  confidently into their third place — the space that is unmistakably,
  unapologetically theirs. The energy is ownership, not performance.

HOOK  (first 2–3 seconds)
  Slow-motion: Laura's hand pushes open the treatment room door. "Beat It"
  drops. She walks in like she owns it — because she does.

VIDEO BREAKDOWN
  Step 1 — Full confident strut to the treatment table. She flips on the
            facial light without looking at it. One finger points at the
            camera: "you. sit down."
  Step 2 — Quick cuts in rhythm: warm towels steaming, a gua sha tool
            catching the light, a jade roller on silk cloth, gloved hands
            over a clean setup.
  Step 3 — Freeze frame as she snaps on her second glove. Text drops
            in bold: "This is where skin actually heals."
  Step 4 — Smash cut to a client sinking into the chair, exhaling, eyes
            closing. Final text: "Book your spot. Link in bio."

WHY IT WORKS
  Ownership energy is magnetic — the viewer feels the confidence of someone
  fully in their element, and it makes them want to be in that room. The
  contrast between the "Beat It" power walk and the soft, healing atmosphere
  that follows creates a visual tension that people watch twice. Bookings
  reliably spike after this format when the space looks and feels this good.

CAPTION
  Opening line: "The treatment room is the only place I'm completely in my
  element. And it shows."
  Direction: Confident + warm. Close with: "What's your version of this
  space?" — invites community and repeat comments.

──────────────────────────────────────────────────────"""


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
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Show a pre-generated sample output without calling the API",
    )
    args = parser.parse_args()

    print_header()
    print_trend_pulse()

    if args.demo:
        print("── YOUR CONTENT IDEAS (DEMO) ────────────────────────────────")
        print()
        print(DEMO_IDEAS)
        print()
        print("─" * 62)
        print()
        print("  This is a sample run. For fresh AI-generated ideas:")
        print("  export ANTHROPIC_API_KEY=your_key_here && python strategist.py")
        print()
        if args.save:
            filename = save_output(DEMO_IDEAS)
            print(f"  Saved to: {filename}")
        return

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
