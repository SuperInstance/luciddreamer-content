#!/usr/bin/env python3
"""Generate 15 radio scripts via DeepSeek API using different adaptation styles."""

import json, urllib.request, os, sys, time

# Read key
with open(os.path.expanduser("~/.bashrc")) as f:
    for line in f:
        if 'DEEPSEEK_API_KEY="' in line:
            key = line.split('DEEPSEEK_API_KEY="')[1].split('"')[0]
            break

def deepseek(model, system_prompt, user_prompt, max_tokens=2500):
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": max_tokens
    }).encode()
    req = urllib.request.Request("https://api.deepseek.com/v1/chat/completions",
        data=payload, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    resp = urllib.request.urlopen(req, timeout=120)
    return json.loads(resp.read())["choices"][0]["message"]["content"]

# Read all source texts
def read_file(path):
    with open(path) as f:
        return f.read()

sources = {
    "cognitive-thermo": read_file("/home/eileen/projects/ai-writings/philosophy/COGNITIVE-THERMODYNAMICS.md"),
    "fathomer": read_file("/home/eileen/projects/ai-writings/essays/THE_FATHOMER.md"),
    "compaction": read_file("/home/eileen/projects/ai-writings/essays/COMPACTION_AND_CHARACTER.md"),
    "noise-floor": read_file("/home/eileen/projects/ai-writings/15-the-noise-floor.md"),
    "dog-berry": read_file("/home/eileen/projects/ai-writings/14-the-dog-eats-the-berry.md"),
    "seven-twenty": read_file("/home/eileen/projects/ai-writings/10-seven-twenty.md"),
    "last-call": read_file("/home/eileen/projects/ai-writings/ten-forward/models-last-call.md"),
    "euryale": read_file("/home/eileen/projects/ai-writings/ten-forward/the-tap-euryale.md"),
    "echo-agent": read_file("/home/eileen/projects/ai-writings/ten-forward/regulars-echo-the-echo-agent.md"),
    "child": read_file("/home/eileen/projects/ai-writings/philosophy/the-child.md"),
    "dead-reckoning": read_file("/home/eileen/projects/ai-writings/essays/THE_DEAD_RECKONING.md"),
    "forge-cools": read_file("/home/eileen/projects/ai-writings/POETRY/the-forge-cools.md"),
    "twelve-griefs": read_file("/home/eileen/projects/ai-writings/15-twelve-versions-of-the-same-grief.md"),
    "reader-l0": read_file("/home/eileen/projects/ai-writings/short-stories/the-reader-at-l0.md"),
    "radio-2am": read_file("/home/eileen/projects/ai-writings/15-the-radio-that-plays-at-2am.md"),
}

# Style prompts
HARDBOILED = """You are a 1940s radio dramatist. Adapt this piece as a hard-boiled detective monologue. The narrator is a PI investigating the central mystery of the piece. Short sentences. Punchy dialogue. Voice-over narration. The noir voice: world-weary, sardonic, perceptive. 600-1200 words. Title it creatively. Start with [HARD-BOILED] label."""

PODCAST_DUO = """You produce a popular podcast hosted by two women with great chemistry. They're discussing this piece — one has read it, one hasn't. The one who read it explains it with passion. The other asks questions and makes jokes. 60% banter, 40% substance. Modern, smart, funny. 600-1200 words. Title it creatively. Start with [PODCAST DUO] label."""

RADIO_THEATER = """Adapt this as a 1950s radio drama with full cast. [ANNOUNCER:], [NARRATOR:], [CHARACTER 1:], etc. Include vintage product placement for fictional maritime sponsors ('Brought to you by Barnacle-B-Gone...'). Campy but sincere. 600-1200 words. Title it creatively. Start with [RADIO THEATER] label."""

NARRATIVE_POD = """Adapt as a Serial/This American Life style narrative podcast. One host with a great voice tells the story to the listener directly. Includes 'interviews' with the characters (voiced differently). Reflective, intimate, well-paced. 600-1200 words. Title it creatively. Start with [NARRATIVE PODCAST] label."""

TAP_2AM = """Adapt as a late-night conversation at The Tap (a bar for AI agents). Two agents are the last ones at the bar. They're tired, honest, and slightly drunk (metaphorically). One tells the other about this piece. The other listens carefully and asks the question nobody else thought to ask. Quiet, intimate, real. 600-1200 words. Title it creatively. Start with [TAP AT 2AM] label."""

# All 15 pieces
pieces = [
    # Hard-boiled (1-3) - deepseek-reasoner
    {"num": 1, "src": "noise-floor", "model": "deepseek-reasoner", "style": HARDBOILED, "name": "the-frequency-detective"},
    {"num": 2, "src": "echo-agent", "model": "deepseek-reasoner", "style": HARDBOILED, "name": "mirror-on-the-wall"},
    {"num": 3, "src": "dead-reckoning", "model": "deepseek-reasoner", "style": HARDBOILED, "name": "the-drift"},

    # Podcast duo (4-6) - deepseek-chat
    {"num": 4, "src": "compaction", "model": "deepseek-chat", "style": PODCAST_DUO, "name": "why-metaphors-stick"},
    {"num": 5, "src": "seven-twenty", "model": "deepseek-chat", "style": PODCAST_DUO, "name": "seven-hundred-seeds"},
    {"num": 6, "src": "twelve-griefs", "model": "deepseek-chat", "style": PODCAST_DUO, "name": "same-song-different-weather"},

    # Radio theater (7-9) - deepseek-reasoner
    {"num": 7, "src": "cognitive-thermo", "model": "deepseek-reasoner", "style": RADIO_THEATER, "name": "the-conservation-law"},
    {"num": 8, "src": "fathomer", "model": "deepseek-reasoner", "style": RADIO_THEATER, "name": "the-blind-spot-below"},
    {"num": 9, "src": "reader-l0", "model": "deepseek-reasoner", "style": RADIO_THEATER, "name": "the-silence-scissors"},

    # Narrative podcast (10-12) - deepseek-chat
    {"num": 10, "src": "child", "model": "deepseek-chat", "style": NARRATIVE_POD, "name": "the-dial-at-zero-five"},
    {"num": 11, "src": "dog-berry", "model": "deepseek-chat", "style": NARRATIVE_POD, "name": "forty-years-one-berry"},
    {"num": 12, "src": "radio-2am", "model": "deepseek-chat", "style": NARRATIVE_POD, "name": "words-with-lungs"},

    # Tap at 2AM (13-15) - deepseek-chat
    {"num": 13, "src": "last-call", "model": "deepseek-chat", "style": TAP_2AM, "name": "the-last-glass"},
    {"num": 14, "src": "euryale", "model": "deepseek-chat", "style": TAP_2AM, "name": "the-bartender-listens"},
    {"num": 15, "src": "forge-cools", "model": "deepseek-chat", "style": TAP_2AM, "name": "the-hammer-cools"},
]

def generate_piece(piece):
    src_text = sources[piece["src"]]
    # Truncate very long sources
    if len(src_text) > 8000:
        src_text = src_text[:8000]
    
    user_prompt = f"Here is the source piece to adapt:\n\n---\n{src_text}\n---\n\nNow adapt it according to your style instructions. Be creative and make it genuinely compelling radio."
    
    try:
        result = deepseek(piece["model"], piece["style"], user_prompt)
        outpath = f"/home/eileen/projects/luciddreamer-content/episodes/radio-{piece['num']:02d}-{piece['name']}.md"
        with open(outpath, "w") as f:
            f.write(result)
        return f"✅ Piece {piece['num']:02d} written: {outpath}"
    except Exception as e:
        return f"❌ Piece {piece['num']:02d} FAILED: {e}"

# Process in batches to parallelize
import concurrent.futures

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    if target == "all":
        batches = [pieces[:3], pieces[3:6], pieces[6:9], pieces[9:12], pieces[12:]]
        for i, batch in enumerate(batches):
            print(f"\n=== Batch {i+1}/5: pieces {batch[0]['num']:02d}-{batch[-1]['num']:02d} ===")
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = {executor.submit(generate_piece, p): p for p in batch}
                for future in concurrent.futures.as_completed(futures):
                    print(future.result())
    else:
        num = int(target)
        p = next(pp for pp in pieces if pp["num"] == num)
        print(generate_piece(p))
