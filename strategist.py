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
            "name": "'When you get THE picture' (CORTIS audio)",
            "pattern": "The shared freak-out IS the bit. Show a friend/client a result so good you both start gagging. For Laura: revealing a client's healed-skin photo and both of you losing it — the genuine reaction sells the transformation harder than any before/after grid.",
            "link": "https://www.tiktok.com/music/%EC%98%A4%EB%A6%AC%EC%A7%80%EB%84%90-%EC%82%AC%EC%9A%B4%EB%93%9C-CORTIS-7654462113867385608",
        },
        {
            "name": "'Me and my POV' split-screen (original audio)",
            "pattern": "Top frame: you in selfie mode. Bottom frame: exactly what you're looking at. For Laura: her face reacting up top, a client's congested skin under the lamp below — narrate what she's actually seeing as an expert.",
            "link": "https://www.tiktok.com/music/original-sound-7640107897372052226",
        },
        {
            "name": "'Reaching out transition' (MJ original sound)",
            "pattern": "Start in pjs, hit the beat, land in your going-out fit + a text overlay that hits too close to home. For Laura: 'me before my barrier healed' (dull, hiding) → beat → 'me now' (bare, glowing) with a relatable skin caption.",
            "link": "https://www.tiktok.com/music/original-sound-7574082891341187862",
        },
        {
            "name": "'Jujutsu Kaisen' identity lineup (original audio)",
            "pattern": "A group strikes the same pose, each holding the thing that IS them; video snaps person to person. For Laura: a lineup of skin types or hero products — 'the barrier girlie,' 'the SPF evangelist,' 'the azelaic acid believer' — rapid-fire personalities.",
            "link": "https://www.tiktok.com/music/original-sound-7646118797946522381",
        },
        {
            "name": "'Sound of water vs sound of…' split-screen",
            "pattern": "Plain water = silence. The good thing = a whole soundtrack kicks in. For Laura: 'a harsh foaming cleanser' (silence) vs 'a barrier-first routine' (the song drops). Built-in contrast gag for product comparisons.",
        },
        {
            "name": "'REDRED dance challenge' (Cortis)",
            "pattern": "Energetic choreography on trending REDRED audio — easy solo or with a group. For Laura: low-stakes way to show personality and bring the treatment-room team on camera; humanizes the brand fast.",
            "link": "https://www.tiktok.com/music/REDRED-7629278086664767505",
        },
        {
            "name": "'Sorry, my hands are full' product stack",
            "pattern": "Pile the products you refuse to put down into your arms; text reads 'sorry, my hands are full.' For Laura: the irreplaceable barrier-repair starter pack — positions her curated picks as the non-negotiable lineup.",
            "link": "https://www.tiktok.com/music/original-sound-7607556252155710221",
        },
    ],
    "viral_formats": [
        {
            "name": "'Describe your job but make it illegal'",
            "pattern": "Clip of you doing what you're best at + text 'describe your job but make it sound illegal.' Let the contrast do the work. For Laura: extractions, dermaplaning, or chemical peels framed in deadpan 'felony' language — low effort, high curiosity, very shareable.",
            "link": "https://www.tiktok.com/music/original-sound-7593428698969885462",
        },
        {
            "name": "'My camera roll is full… nevermind' fake-out",
            "pattern": "Pretend to start deleting photos to free space, then cut to the avalanche you could never part with. For Laura: 'maybe I should delete some client photos…' → nevermind → flood of glow-up results. The twist is the whole bit.",
            "link": "https://www.tiktok.com/music/original-sound-7637917360795470623",
        },
        {
            "name": "'How to make [X] fans nervous' tension gag",
            "pattern": "Do something that looks mildly risky to people who care about pristine things — tension comes from what ALMOST happens, then relief. For Laura: hovering near a perfectly clean pore-extraction, a wobbling shelf of serums — 'making skincare girlies nervous.' 5–10 sec, close-up, audio carries it.",
            "link": "https://www.tiktok.com/@carlylego",
        },
        {
            "name": "'Tone challenge game' (group)",
            "pattern": "Each person reads the same on-screen line in a different tone — serious, funny, flirty — best when someone breaks character. For Laura: read a wild skincare myth or a real client excuse in escalating tones with the team. Collaborative and personality-forward.",
        },
        {
            "name": "Aesthetic follow-along (e.g. 'viral dot cake')",
            "pattern": "Quick, satisfying, visually clean follow-along of a simple process. For Laura: a follow-along of mixing a custom mask or layering a routine — ASMR-clean, screenshot-pretty, easy to recreate. Process content people watch to the end.",
        },
        {
            "name": "Treatment room POV (no audio needed)",
            "pattern": "First-person camera as if the viewer is the client on the facial bed — ceiling, lamp, Laura's hands. Immersive, sensory, deeply differentiated. Still one of the strongest evergreen formats for an esthetician.",
        },
    ],
    "content_patterns": [
        "Realism over fantasy — raw, behind-the-curtain content outperforms polished",
        "Curiosity-driven discovery — audiences verify products/services on TikTok before buying",
        "Native format beats a script — even an obvious ad wins when it's the thing only you could make",
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
        "Azelaic Acid trending as the go-to active for sensitive skin — ingredient-literate audiences searching it by name",
        "#fullfacenomascara (404K+ likes) — shift toward bold brows + dewy skin; opens content around treatments that enhance natural features",
        "Exosome treatments emerging as viral advanced repair topic — positions Laura ahead of the curve",
    ],
}

INSTAGRAM_TRENDS = {
    "formats": [
        {
            "name": "'The summer schedule' 4x-looping hook (original audio)",
            "pattern": "A visual loop where the hook lands four times, pulling viewers back in — made to romanticize a daily routine. For Laura: romanticize the morning skin ritual or the treatment-room open, looped so it rewatches itself.",
            "link": "https://www.instagram.com/reels/audio/202891871734130/",
        },
        {
            "name": "'I would literally do anything for you' (over-the-top vs reality)",
            "pattern": "A dramatic declaration meets tiny real stakes — the bigger the gap, the better. For Laura: 'I'd do ANYTHING for my clients' → cut to her gently refusing to let them over-exfoliate. Relatable, warm, EGC-style.",
            "link": "https://www.instagram.com/reels/audio/35981693481446045/",
        },
        {
            "name": "'What you want' confident flex (Respect – Aretha)",
            "pattern": "Show exactly what you offer in the most satisfying way — 'here's what we do, and we do it well.' For Laura: a clean, proud montage of signature treatments. Own-it energy for a service brand.",
            "link": "https://www.instagram.com/reels/audio/515371218997711/",
        },
        {
            "name": "'Sketch my outfit' draw-to-real morph (original audio)",
            "pattern": "Sketch each item onto yourself, then each drawing morphs into the real thing. For Laura: 'sketch my routine' — draw each step, morph into the actual product/result. Equal parts art project and reveal.",
            "link": "https://www.instagram.com/reels/audio/242667523150430/",
        },
        {
            "name": "'Do you wanna?' question-into-answer (Human Nature – MJ)",
            "pattern": "Open with a 'do you wanna…' prompt about whether you're ready, then cut to you fully doing the thing. For Laura: 'do you wanna finally stop guessing with your skin?' → cut to the consult/treatment in motion.",
            "link": "https://www.instagram.com/reels/audio/1066931830157201/",
        },
        {
            "name": "'Girl grip' one-hand haul flex (I'm Every Woman – Chaka Khan)",
            "pattern": "Haul your entire life in one hand with total confidence. For Laura: the one-handed grip of all her must-have products/tools heading into a treatment — a flex that doubles as a product showcase.",
            "link": "https://www.instagram.com/reels/audio/1715351118547270/",
        },
        {
            "name": "'Lens wipe transition' glow-up reveal",
            "pattern": "Film the 'before,' wipe the lens, reveal the glow-up — product, aesthetic, or skin shift. Clean, satisfying, hard to scroll past. Ideal for treatment before/after with zero fancy editing.",
            "link": "https://www.instagram.com/reels/audio/26923322580669821/",
        },
    ],
    "viral_formats": [
        {
            "name": "'Plan ABC' alternate-timeline slides",
            "pattern": "Each slide reveals a different hypothetical path — the dream, the chaos, the 'honestly that works too.' For Laura: 'Plan A: perfect routine. Plan B: barrier repair after I overdid it. Plan C: just SPF and sleep.' Playful, bendable to any niche.",
            "link": "https://www.instagram.com/reels/audio/26885590624412674/",
        },
        {
            "name": "'Stomp to reveal' jump transition",
            "pattern": "Each jump/stomp peels back the background until you land somewhere new. For Laura: stomp from a dull bathroom-mirror skin moment into the glowing treatment-room reveal. Earns the build-up.",
        },
        {
            "name": "'Too shy to take pics in public' (introvert vs ride-or-die)",
            "pattern": "One person mortified to be photographed; the other directs a full editorial like nobody's watching. For Laura: the nervous-about-their-skin client vs Laura, the ride-or-die who sees the glow-up potential. Wildly relatable.",
            "link": "https://www.instagram.com/reels/audio/1279574933274134/",
        },
        {
            "name": "'Stretched word' swipe-for-payoff carousel",
            "pattern": "One word stretched across a whole carousel — each slide pairs a sliver of the word with a relatable thought; the slow reveal IS the hook. For Laura: 'B-A-R-R-I-E-R' across slides, each one a myth or truth, punchline on the last swipe. Pure save-bait.",
        },
        {
            "name": "Before/after with emotional narration",
            "pattern": "Narrate the FEELING of the journey over the visual — 'this is the face that cried in my car before this appointment.' Human, not clinical. Deeply shareable evergreen format.",
        },
    ],
    "content_behaviors": [
        "Raw, unpolished content outperforming high-production posts",
        "Strong hooks in first 0-2 seconds = everything (looping hooks pull rewatches)",
        "Comment sections engineered as part of the content (ask, provoke, invite)",
        "Short-form Reels dominating reach over long-form",
        "Save-worthy carousels for education (pigmentation maps, acne guides, routines)",
        "Self-aware + meta humor builds credibility and relatability",
    ],
}

# ── Core Virality Patterns (the WHY behind the trends) ───────────────────────
# Extracted across Later, New Engen, and Clipchamp June 2026 trend reporting.

CROSS_PLATFORM_PATTERNS = [
    "THE CONTRAST GAP: humor and shareability come from the distance between expectation and reality (job-but-illegal, water-vs-coffee, huge-words-tiny-stakes)",
    "FAKE-OUT TWIST: set up one direction, swerve to another — the 'nevermind' pivot is the whole payoff",
    "TENSION → RELIEF: build suspense around something almost going wrong, then resolve it (makes viewers tense, then relieved = rewatch)",
    "SATISFYING TRANSITION: a physical trigger (wipe, stomp, beat, reach) snaps to a new scene — the cleaner the trigger, the more unscrollable",
    "IDENTITY SHOWCASE: 'the thing that IS you' — lineups and alternate-timeline formats let personality carry the video",
    "RELATABLE FLEX: ordinary behavior elevated (one-hand haul, hands-full stack) — recognition drives the share and the tag",
    "SLOW-REVEAL HOOK: stretch the payoff across a loop or carousel so the swipe/rewatch IS the engagement (save-bait)",
    "TRUST IS THE MOAT AI CAN'T FAKE: first-person, native, honest expert content is the one scarce thing — generic/polished is being devalued",
    "REPEATABLE BIT: give the audience something to clip, quote, stitch, or recreate — a paid idea earns a second life as organic reach",
    "AUTHORITY GETS CITED: genuine reviews/explainers/demos are what AI search surfaces — first-person expertise compounds discoverability (AEO)",
    "RECURRING > ONE-OFF: trust compounds through repetition — a signature format or sound builds brand recall faster than scattered posts",
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
    lines.append("TRENDING AUDIO & AUDIO-DRIVEN FORMATS:")
    for item in TIKTOK_TRENDS["audio_formats"]:
        lines.append(f"  • {item['name']}")
        lines.append(f"    → {item['pattern']}")
    lines.append("")
    lines.append("VIRAL CONTENT FORMATS (NO AUDIO REQUIRED):")
    for item in TIKTOK_TRENDS["viral_formats"]:
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
    lines.append("TRENDING AUDIO-DRIVEN FORMATS:")
    for item in INSTAGRAM_TRENDS["formats"]:
        lines.append(f"  • {item['name']}")
        lines.append(f"    → {item['pattern']}")
    lines.append("")
    lines.append("VIRAL CONTENT FORMATS (NO AUDIO REQUIRED):")
    for item in INSTAGRAM_TRENDS["viral_formats"]:
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


PREFILL = '╔══════════════════════════════════════╗\n  1.'

FORMAT_PROMPT = """Generate 6 original content ideas for Skin by Laura Lo.

CRITICAL: Output ONLY the 6 ideas. No intro sentence, no closing note, no transitions between ideas.
Use EXACTLY this block structure for every single idea — character for character:

╔══════════════════════════════════════╗
  [NUMBER]. CONCEPT TITLE IN CAPS
  Platform: TikTok / Instagram Reels / Both
╚══════════════════════════════════════╝

TREND PATTERN
  [Name of the trend/audio/format — one sentence on how the mechanic works]

HOOK  (first 2–3 seconds)
  [Exact scene: camera angle, what the viewer sees, hears, reads on screen. Cinematic and specific.]

VIDEO BREAKDOWN
  Step 1 — [what happens]
  Step 2 — [what happens]
  Step 3 — [what happens]
  Step 4 — [what happens]

WHY IT WORKS
  [2–3 sentences: the psychological or emotional reason this stops the scroll,
   drives saves/shares, and fits the algorithm right now.]

CAPTION
  Opening line: "[exact first sentence Laura should post — ready to copy-paste]"
  Direction: [tone note + CTA or engagement hook]

──────────────────────────────────────────────────────

Mix: emotional, myth-busting, behind-the-scenes, bold-take. Vary platforms. Every idea unmistakably Skin by Laura Lo."""


def generate_ideas(extra_trend: str = None) -> str:
    """Call Claude API and return formatted content ideas."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY not set.\n  Run: export ANTHROPIC_API_KEY=your_key_here"
        )

    client = anthropic.Anthropic(api_key=api_key)
    trend_brief = build_trend_brief(extra_trend)

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},  # cached — brand DNA never changes
            }
        ],
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"TREND INTELLIGENCE REPORT:\n\n{trend_brief}",
                        "cache_control": {"type": "ephemeral"},  # cached — trends update monthly
                    },
                    {
                        "type": "text",
                        "text": FORMAT_PROMPT,
                    },
                ],
            },
            {
                "role": "assistant",
                "content": PREFILL,  # forces the exact box structure from the first character
            },
        ],
    )

    return PREFILL + message.content[0].text


# ── CLI Output ────────────────────────────────────────────────────────────────

def print_header():
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║        SKIN BY LAURA LO — VIRAL CONTENT STRATEGIST       ║")
    print(f"║                   Trend Report: June {datetime.now().year}                ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()


def _pulse_group(title: str, items: list) -> None:
    """Print one trend-pulse group; items are dicts (name) or plain strings."""
    print(f"  {title}")
    for item in items:
        name = item["name"] if isinstance(item, dict) else item
        print(f"  › {name}")
    print()


def print_trend_pulse():
    print("── TREND PULSE ──────────────────────────────────────────────")
    print()
    _pulse_group("TIKTOK — AUDIO-DRIVEN",            TIKTOK_TRENDS["audio_formats"])
    _pulse_group("TIKTOK — VIRAL FORMATS (NO AUDIO)", TIKTOK_TRENDS["viral_formats"])
    _pulse_group("TIKTOK — HOT SKINCARE TOPICS",      TIKTOK_TRENDS["skincare_topics"])
    _pulse_group("INSTAGRAM — AUDIO-DRIVEN",          INSTAGRAM_TRENDS["formats"])
    _pulse_group("INSTAGRAM — VIRAL FORMATS (NO AUDIO)", INSTAGRAM_TRENDS["viral_formats"])
    _pulse_group("CORE VIRALITY PATTERNS",            CROSS_PLATFORM_PATTERNS)
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
