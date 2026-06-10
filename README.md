# Viral Content Strategist — Skin by Laura Lo

Reads current TikTok + Instagram trend patterns and generates original, on-brand video ideas for **Skin by Laura Lo**.

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here
```

## Usage

```bash
# Generate 6 fresh video ideas
python strategist.py

# Save ideas to a dated file
python strategist.py --save

# Add your own trend or competitor note
python strategist.py --add-trend "competitor just posted a 'skin confession' reel that got 500k views"

# Combine flags
python strategist.py --save --add-trend "lash lift is trending hard this week"
```

## What it does

1. Displays the current trend pulse (TikTok + Instagram Reels, updated June 2026)
2. Calls Claude with the full trend brief + brand essence
3. Returns 6 original, platform-specific video ideas formatted with:
   - First 3 seconds hook
   - Step-by-step video breakdown
   - Caption direction
   - Why it'll perform

## Trend sources tracked

- TikTok trending audio & formats (May–June 2026)
- Instagram Reels viral formats & behaviors
- Skincare-specific viral topics (barrier repair, skin longevity, Korean beauty)
- Cross-platform content patterns

## Update trends

Edit the `TIKTOK_TRENDS` and `INSTAGRAM_TRENDS` dictionaries in `strategist.py` monthly as trends shift.
