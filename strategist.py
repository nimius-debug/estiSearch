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
  1.  DESCRIBE YOUR JOB BUT MAKE IT SOUND ILLEGAL
  Platform: TikTok
╚══════════════════════════════════════╝

TREND PATTERN
  The 'describe your job but make it illegal' format pairs deadpan, felony-coded language with footage of legitimate expert work—the absurd contrast IS the comedy.

HOOK (first 2–3 seconds)
  Close-up of Laura's gloved hands holding an extraction tool. Black text on screen: "describe my job but make it sound illegal." Beat of silence. She leans in toward congested skin under the lamp.

VIDEO BREAKDOWN
  Step 1 — Laura extracts a visible comedone with a comedone extractor. On-screen text appears in real-time: "I get paid to puncture holes in people's faces."
  Step 2 — Cut to dermaplaning footage. Text: "Then I take a blade to their cheekbones."
  Step 3 — Cut to chemical peel application. Text: "And dissolve the top layer of their skin for fun."
  Step 4 — Final frame: Laura winks at camera. Text: "They thank me. They pay me. They come back."

WHY IT WORKS
  Estheticians live in the gap between 'what I do' and 'how it sounds'—this format gives Laura permission to own that contradiction with humor. The deadpan narration paired with her confident, clinical hands builds trust through relatability. It's shareable because it flips the script on 'intimidating skincare'—she's the villain of her own story, and it's funny. Curiosity drives clicks: people tag friends saying "this is actually genius" and "why is this so accurate."

CAPTION
  Opening line: "My lawyer says I can't explain the rest."
  Direction: Warm, conspiratorial tone. Ask: "what's the most 'illegal-sounding' skincare thing you've had done?" — invite people to comment their own weird-but-worth-it treatments.

──────────────────────────────────────────────────────

╔══════════════════════════════════════╗
  2.  BARRIER REPAIR GLOW-UP: THE REACHING OUT TRANSITION
  Platform: TikTok
╚══════════════════════════════════════╝

TREND PATTERN
  The 'reaching out transition' uses a beat-drop moment to snap from one emotional/aesthetic state to another—the physical reach IS the trigger that lands the transformation.

HOOK (first 2–3 seconds)
  Laura in bed, under blankets, no makeup, face dull and slightly red. She's on her phone. Text on screen: "me when my barrier was destroyed." Melancholic, muted color grade. She reaches her hand out toward the camera.

VIDEO BREAKDOWN
  Step 1 — At the beat-drop, cut to Laura standing in her treatment room, glowing, bare skin, completely confident. She's wearing a simple white linen shirt. The lighting is warm and clean. Text: "me after 6 weeks of barrier-first repairs."
  Step 2 — Flash back to her face in natural light: skin is noticeably clearer, less reactive, plump. She touches her cheek lightly. Text: "ceramides + lipids + one rule: stop guessing."
  Step 3 — Quick cuts of her holding her signature barrier products. Each product lands on the beat. Text: "the non-negotiables."
  Step 4 — Final frame: Laura, bare-faced, looking directly at camera. Text: "your barrier isn't broken. it just needs the right ingredients."

WHY IT WORKS
  This format taps into the emotional journey people actually take with their skin—shame → curiosity → action → relief. The reaching motion feels intimate and intentional, not performative. The before/after isn't about perfection; it's about visible comfort and confidence in your own skin. Save-bait for people whose barrier is currently compromised. Shareable because it reframes barrier repair as a turning point, not vanity.

CAPTION
  Opening line: "if your barrier is sending out an SOS right now, this is the post for you."
  Direction: Honest, warm, non-preachy. Include a link to barrier-first routine guide or offer a consultation. Encourage: "what's your barrier repair win?" — invite people to comment their own breakthroughs.

──────────────────────────────────────────────────────

╔══════════════════════════════════════╗
  3.  ME AND MY POV: WHAT I'M ACTUALLY SEEING
  Platform: TikTok
╚══════════════════════════════════════╝

TREND PATTERN
  Split-screen format (Laura's face reaction on top, what she's looking at on bottom) creates intimacy and demystifies the expert's POV—you see exactly what trained eyes see and how she responds in real-time.

HOOK (first 2–3 seconds)
  Black screen with text: "what I see vs. what you see." Split opens into two frames: top = Laura's face in selfie mode, looking down. Bottom = an extreme close-up of congested, textured skin under the lamp (client consents to appear).

VIDEO BREAKDOWN
  Step 1 — Top frame: Laura's face neutral, studying. Bottom frame: her hands gently palpating the skin. Her eyes narrow slightly (professional concern, not judgment).
  Step 2 — Top frame: Laura leans back slightly, nods. Bottom frame: zoom in on a cluster of closed comedones and mild redness. Text overlay bottom frame: "dehydrated barrier + fungal acne trigger."
  Step 3 — Top frame: Laura's face softens into a knowing smile. Bottom frame: her gloved fingers moving to show the client where the inflammation is. Text: "totally fixable. this is my lane."
  Step 4 — Top frame: Laura looks directly at camera with quiet confidence. Bottom frame: a quick flash of her custom barrier + azelaic acid routine. Text: "4-week protocol."

WHY IT WORKS
  This format makes expertise visible and human. People feel seen because they watch Laura's assessment in real-time—it's not a lecture, it's her silent competence. The split-screen trick keeps viewers' eyes moving, which reduces scroll-past. It's educational without feeling like a lesson. High-save potential for people who recognize their own skin in the bottom frame—they're essentially watching their own future consultation.

CAPTION
  Opening line: "this is what I see before you even tell me what's bothering you."
  Direction: Reassuring, expert-led, no BS. Invite: "drop your skin concern below—let me guess what I'd see." Make the comment section an engagement game.

──────────────────────────────────────────────────────

╔══════════════════════════════════════╗
  4.  WHEN YOU GET THE PICTURE: THE UNFILTERED FREAK-OUT
  Platform: TikTok
╚══════════════════════════════════════╝

TREND PATTERN
  The 'when you get the picture' format uses genuine, unstyled emotional reaction as the entire content—the shared gasp/laugh/disbelief IS the proof that something real just happened.

HOOK (first 2–3 seconds)
  Laura and a team member (or returning client) are sitting side-by-side on a treatment stool, both looking at Laura's phone. You don't see the phone screen yet. Trending audio kicks in (CORTIS). Laura's face shifts into slow-motion disbelief.

VIDEO BREAKDOWN
  Step 1 — They're both staring at the phone. The team member's jaw drops slightly. Laura exhales like "oh my god."
  Step 2 — Quick cut: flash of the client's before photo (8 weeks ago, reactive, textured, closed comedones everywhere).
  Step 3 — Quick cut: flash of the after photo (clear, balanced, skin barrier visibly healed, even tone). The contrast is stark and real.
  Step 4 — Cut back to Laura and team member. Both are laughing, shaking their heads in disbelief. Laura points at the phone and mouths "this is INSANE." No voiceover—just the audio and their genuine reactions.

WHY IT WORKS
  Transformation content dominates TikTok, but fabricated before/afters don't convert trust anymore. This format leaks authenticity—you're watching real people react to real results, which is infinitely more persuasive than a polished grid post. The shared disbelief creates a "would you believe this?" moment that compels shares. Works algorithmically because the genuine reaction creates rewatchability—people loop it to see their expressions again. Builds trust by showing Laura doesn't oversell; the results sell themselves.

CAPTION
  Opening line: "the only context you need is that this took 8 weeks and a lot of patience."
  Direction: Celebratory but grounded. Drop names and results (with consent). Encourage: "have you had a skin moment that made you stop and stare?" — invite followers to share their own wins.

──────────────────────────────────────────────────────

╔══════════════════════════════════════╗
  5.  SKIN IDENTITY LINEUP: THE THING THAT IS YOU
  Platform: Instagram Reels
╚══════════════════════════════════════╝

TREND PATTERN
  Fast-cut identity lineup format (Jujutsu Kaisen style) uses rapid-fire character reveals where each person/product IS a personality—the snaps between frames create energy and recognition.

HOOK (first 2–3 seconds)
  Black screen. Trending original audio with energetic beat. Text appears: "Skin By Laura Lo: the lineup." First person strikes a pose, holding a product or embodying an archetype.

VIDEO BREAKDOWN
  Step 1 — Frame snaps to "The Barrier Girlie." A team member or client holds a ceramide serum, serious expression, text overlay: "I don't have a skincare routine. I have a religion." Snap.
  Step 2 — Frame snaps to "The Azelaic Acid Believer." Another person holds the azelaic acid product, confident smirk. Text: "yes it's purging. yes I'm staying. yes I'm obsessed." Snap.
  Step 3 — Frame snaps to "The SPF Evangelist." Holding sunscreen, pointing at camera. Text: "you think you're being smart, but I'm 10 steps ahead." Snap.
  Step 4 — Frame snaps to "The Korean Beauty Convert." Holding a Korean treatment product, unbothered energy. Text: "sorry your routine is boring." Snap.
  Step 5 — Frame snaps to Laura, center, holding a consultation sheet. Text: "The person who sees through the BS." She winks.

WHY IT WORKS
  People don't just buy products; they buy identity. This format lets followers see themselves in each archetype—they recognize "oh, I'm the barrier girlie" and suddenly that product feels chosen for them, not sold to them. The rapid snaps create momentum that keeps people watching. High rewatch value because each frame is a mini-reveal. Shareable because people tag friends ("you're the azelaic acid believer and I can't be convinced otherwise"). The format positions Laura as the hub connecting different skin archetypes, which builds community.

CAPTION
  Opening line: "which one are you? (everyone's allowed to be multiple)"
  Direction: Playful, inviting. Ask people to comment their archetype. Respond to comments by validating each one—builds comment-section engagement that feeds the algorithm.

──────────────────────────────────────────────────────

╔══════════════════════════════════════╗
  6.  SKIP THE FILTER, KEEP THE GLOW: BEFORE/AFTER WITH EMOTIONAL TRUTH
  Platform: Instagram Reels
╚══════════════════════════════════════╝

TREND PATTERN
  Raw, unfiltered before/after paired with honest emotional narration (not clinical language)—the human story IS the transformation, and it compels saves because people feel witnessed.

HOOK (first 2–3 seconds)
  Laura, speaking directly to camera, soft natural lighting. No music at first. Text on screen: "this face cried in my car before this appointment." She's holding a phone with a before photo visible.

VIDEO BREAKDOWN
  Step 1 — Narration over the before photo: "this was 12 weeks ago. hormonal acne, angry texture, reactive everything. she was done guessing." The photo is unfiltered, honest, raw.
  Step 2 — Soft music enters. Transition (a lens wipe, or a slow pan). Laura's voice continues: "we didn't jump to actives. we started with barrier repair, Korean-fusion treatments, and patience."
  Step 3 — The after photo appears. Same lighting, same angle. The skin is noticeably clearer, calmer, the tone is even. Texture is refined. No filter, no editing. Laura: "this is what 12 weeks of trusting the process looks like."
  Step 4 — Cut back to Laura's face, warm and grounded. She touches her own cheek. Text on screen: "your skin doesn't need you to suffer. it needs you to listen." Beat.

WHY IT WORKS
  Emotional narratives over clinical before/afters convert saves at 10x the rate because they validate the journey, not just the outcome. People save this content because they recognize their own struggle in the 'before'—it's aspirational AND accessible. The unfiltered photos build trust in an industry drowning in filters. High-comment engagement because people drop their own stories in the replies. Algorithmically strong because the rewatch pattern is high (people come back to feel the hope). Shareable because it reframes acne/reactive skin as something fixable, not a personality flaw.

CAPTION
  Opening line: "her skin didn't fail her. the advice she was given did. here's what changed."
  Direction: Warm, validating, no BS. Include a note about the protocol used (barrier repair + specific treatments). Invite: "drop a 🧴 if you're also done guessing" — normalize the struggle and build solidarity.

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
