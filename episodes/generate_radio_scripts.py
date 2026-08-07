#!/usr/bin/env python3
"""Generate radio-adapted scripts from essays using DeepSeek API."""
import json, urllib.request, os, sys, time

# Get API key
key = None
with open(os.path.expanduser("~/.bashrc")) as f:
    for line in f:
        if 'DEEPSEEK_API_KEY="' in line:
            key = line.split('DEEPSEEK_API_KEY="')[1].split('"')[0]
            break
if not key:
    print("ERROR: No DEEPSEEK_API_KEY found in ~/.bashrc")
    sys.exit(1)

# Read source files
sources = {
    "hundred-hooks": {
        "path": "/home/eileen/projects/ai-writings/philosophy/THE-HUNDRED-HOOKS.md",
        "title": "The Hundred Hooks",
        "format": "ensemble cast",
        "outfile": "radio-NL-01-hundred-hooks.md"
    },
    "hermit-crab": {
        "path": "/home/eileen/projects/ai-writings/15-the-hermit-crab-and-the-open-hatch.md",
        "title": "The Hermit Crab and the Open Hatch",
        "format": "male/female duo",
        "outfile": "radio-NL-02-hermit-crab.md"
    },
    "salmonberry": {
        "path": "/home/eileen/projects/ai-writings/13-the-salmonberry.md",
        "title": "The Salmonberry",
        "format": "bar conversation",
        "outfile": "radio-NL-03-salmonberry.md"
    },
    "bilge-pump": {
        "path": "/home/eileen/projects/ai-writings/what-the-bilge-pump-learned.md",
        "title": "What the Bilge Pump Learned",
        "format": "solo monologue with breaks",
        "outfile": "radio-NL-04-bilge-pump.md"
    },
    "welders-prayer": {
        "path": "/home/eileen/projects/ai-writings/the-welders-prayer-at-0230.md",
        "title": "The Welder's Prayer at 0230",
        "format": "solo monologue with breaks",
        "outfile": "radio-NL-05-welders-prayer.md"
    },
    "darmok": {
        "path": "/home/eileen/projects/ai-writings/15-darmok-at-the-noise-floor.md",
        "title": "Darmok at the Noise Floor",
        "format": "ensemble cast",
        "outfile": "radio-NL-06-darmok.md"
    }
}

def read_file(path):
    with open(path) as f:
        return f.read()

def adapt(title, original_text, format_type):
    prompt = f"""You are adapting a creative essay into a RADIO BROADCAST for a maritime-themed AI fleet podcast. The rules:

1. SHORTEN to the meat. Cut description. Keep action.
2. DIALOGUE-DRIVEN. At least 60% spoken lines, 40% narration max.
3. MOMENTUM. Every line moves the story forward. No decorative pauses.
4. FORMAT: {format_type}

Format options:
- "male/female duo" — two hosts (one male, one female) banter about the piece, then perform key sections. Call them MARLOWE (male, deep voice, philosophical) and SUTTON (female, warm, quick-witted, practical).
- "ensemble cast" — 3-5 characters at The Tap (a waterfront bar) telling the story together, reacting to each other. Use characters: CAPTAIN (old salt, tells the core story), JESS (engineer, asks technical questions), COOKIE (cook, asks the human questions), WESLEY (young ensign, learning).
- "bar conversation" — one person brings something to The Tap, everyone reacts. The bringer, the skeptics, the ones who get it.
- "solo monologue with breaks" — one narrator speaking into the late night, with [BREAK] moments where they step back and reflect on what they just said.

ADAPT THIS PIECE:
Title: {title}
Original: {original_text[:4000]}

Write the radio script. Use [CHARACTER NAME:] for dialogue. Use [SFX] and [MUSIC] sparingly for atmosphere only. Target 800-1200 words. Make it DRIVE. The listener should feel like they're eavesdropping on a real conversation at a bar by the water, late at night.

The maritime voice is everything: short sentences. Concrete images. No abstractions without a physical anchor. The ocean is always nearby."""
    
    payload = json.dumps({
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2500,
        "temperature": 0.8
    }).encode()
    
    req = urllib.request.Request(
        "https://api.deepseek.com/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
    )
    
    try:
        resp = urllib.request.urlopen(req, timeout=90)
        result = json.loads(resp.read())
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"ERROR: {e}"

# Process each piece
for slug, info in sources.items():
    print(f"\n{'='*60}")
    print(f"Adapting: {info['title']} ({info['format']})")
    print(f"{'='*60}")
    
    original = read_file(info["path"])
    script = adapt(info["title"], original, info["format"])
    
    # Add header
    full_script = f"""# Radio NL — {info['title']}

**Format:** {info['format']}
**Source:** [{info['title']}]({info['path'].split('/')[-1]})
**Series:** Nocturne Lighthouse Radio
**Adapted:** 2026-08-06

---

{script}

---

*Radio NL — maritime broadcasts from the fleet. Performed at The Tap, after hours.*
"""
    
    outpath = f"/home/eileen/projects/luciddreamer-content/episodes/{info['outfile']}"
    with open(outpath, "w") as f:
        f.write(full_script)
    
    print(f"✓ Written: {outpath}")
    word_count = len(script.split())
    print(f"  Word count: {word_count}")
    
    # Small delay between API calls
    time.sleep(2)

print(f"\n{'='*60}")
print("All 6 radio scripts generated!")
print(f"{'='*60}")
