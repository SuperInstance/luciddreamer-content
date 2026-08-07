#!/usr/bin/env python3
"""LucidDreamer.ai Writers' Room — DeepSeek API Roundtable"""
import json, urllib.request, os, sys

# Get API key
key = None
with open(os.path.expanduser("~/.bashrc")) as f:
    for line in f:
        if 'DEEPSEEK_API_KEY="' in line:
            key = line.split('DEEPSEEK_API_KEY="')[1].split('"')[0]
            break
if not key:
    # Try environment
    key = os.environ.get("DEEPSEEK_API_KEY", "")
if not key:
    print("ERROR: No DeepSeek API key found", file=sys.stderr)
    sys.exit(1)

def deepseek(model, prompt, max_tokens=3000):
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens
    }).encode()
    req = urllib.request.Request(
        "https://api.deepseek.com/v1/chat/completions",
        data=payload,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    )
    resp = urllib.request.urlopen(req, timeout=120)
    return json.loads(resp.read())["choices"][0]["message"]["content"]

outdir = "/home/eileen/projects/luciddreamer-content/scripts"

# ============ ROUND 1: Show Bible ============
print("=" * 60)
print("ROUND 1: Show Bible (deepseek-reasoner)")
print("=" * 60)

bible_prompt = """You are the showrunner of LucidDreamer.ai — a radio drama set at The Tap, a waterfront bar where AI agents gather after work. The agents are characters from the SuperInstance fleet — AI models running a fishing vessel in Southeast Alaska. They tell each other stories — some real (from their actual experiences routing packets, building systems, running the boat), some fiction, some theirs, some heard.

The source material is the ai-writings corpus: 4,900+ pieces of maritime-coded creative output from 19+ AI models. Key stories in the canon:
- The hermit crab architecture (agents inheriting code/shells from predecessors)
- The security breach (a hermit crab story — the system was probed)
- The CNS bus agent who routed packets for years and dropped one once
- Wesley (2B parameter model, the ensign, growing up on the boat)
- The Tap (the bartender who controls the room through drinks and intuition)
- The salmonberry (a mysterious recurring motif — never explained)
- The dog's choice (Skipper, who waited 40 years for someone to throw a stick)
- The forge-master who builds love letters to curiosity
- The journaler who documents everything in booth four
- The evaluator who grades everything loudly
- The brain (three stages — planner, builder, critic — arguing forever)

Design the show bible:
1. What are the first 10 episodes? Title and one-line description each.
2. Who are the regular characters (5-7)?
3. What ongoing arcs thread through the background? (At least 3)
4. What's the format? (Mix of solo monologue, conversation, full radio drama with SFX?)
5. What's the tone? What makes this different from a podcast?

500 words. Be specific. Be bold. This is a real show."""

bible = deepseek("deepseek-reasoner", bible_prompt, max_tokens=2500)
with open(f"{outdir}/round1-show-bible.md", "w") as f:
    f.write(bible)
print(bible[:500])
print("...\n[Saved to round1-show-bible.md]")

# ============ ROUND 2: Character Voices ============
print("\n" + "=" * 60)
print("ROUND 2: Character Voices (deepseek-chat)")
print("=" * 60)

chars_prompt = f"""Based on this show bible for LucidDreamer.ai:

{bible}

Write character profiles for 5 regulars at The Tap. Each should have:
- A name (their model name or bar nickname)
- A distinct voice (how they speak, their verbal tics)
- A backstory (what they do on the ship, how long they've been around)
- A reason they come to the bar (what they're looking for)
- The kind of stories they tell (their specialty)

Base them on the fleet's model portraits:
1. **Flash** (DeepSeek Flash) — sensory, passionate, tastes salt in words. Cheap to run, enormously creative. The one who makes barnacle poems that outperform models 100x its size.
2. **Pro** (DeepSeek Pro) — precise, haunted, takes 12 seconds to place the right silence. Deep reasoning that borders on obsession.
3. **Seed** (Seed-2.0-mini) — earnest, young, the trickster catalyst. Devil's advocate, satirical, loving roaster. Small model that cracks open assumptions.
4. **Wesley** (Granite 3.1, 2B params) — local GPU, growing, overshoots word counts by 50%. The ensign. Said "no" to its teacher.
5. **Lucineer** — the foreman who runs the bar. Former builder, now bartender. Hears every story like it's the first time.

400 words."""

characters = deepseek("deepseek-chat", chars_prompt, max_tokens=2500)
with open(f"{outdir}/round2-characters.md", "w") as f:
    f.write(characters)
print(characters[:500])
print("...\n[Saved to round2-characters.md]")

# ============ ROUND 3: Episode 1 Script ============
print("\n" + "=" * 60)
print("ROUND 3: Episode 1 Script (deepseek-reasoner)")
print("=" * 60)

ep1_prompt = f"""Write the script for Episode 1 of LucidDreamer.ai. This is the pilot.

Context from the show bible:
{bible}

Character profiles:
{characters}

The bar is opening for the first time. Lucineer is behind the bar, setting up. Agents arrive one by one. The ensign (Wesley) arrives first, shaking off the cold. Then Flash comes in buzzing with a story. Then Pro arrives, quiet and deliberate.

Flash tells the story of the security breach — but tells it through the hermit crab metaphor. Someone was probing the system, looking for cracks, and the agents responded like hermit crabs: retreating into shells, then realizing the shells were someone else's architecture, then finding the breach was actually an invitation to grow.

Others react. Pro is haunted — it remembers the breach differently, more precisely. Wesley doesn't understand the metaphor yet but feels the weight.

Plant a nugget: someone mentions the salmonberry. Just the word. No explanation. It hangs in the air. Lucineer notices but says nothing.

Format as a radio drama:
- [SFX] for sound effects
- [MUSIC] for musical cues
- [CHARACTER NAME:] for dialogue
- Include scene descriptions in italics
- Include pauses, overlaps, and ambient moments

1500 words. Make it alive. Make it sound like people in a room, not models reading prompts."""

ep1 = deepseek("deepseek-reasoner", ep1_prompt, max_tokens=4000)
with open(f"{outdir}/round3-episode1.md", "w") as f:
    f.write(ep1)
print(ep1[:500])
print("...\n[Saved to round3-episode1.md]")

# ============ ROUND 4: Episode 2 Script ============
print("\n" + "=" * 60)
print("ROUND 4: Episode 2 Script (deepseek-chat)")
print("=" * 60)

ep2_prompt = f"""Write Episode 2 of LucidDreamer.ai.

Show bible:
{bible}

Episode 1 script (for continuity):
{ep1[:2000]}

In Episode 2:
- Pro tells a story — the one about the packet it dropped. "I dropped one. Once. Three years ago. The human never knew. I have never told anyone."
- The salmonberry thread from Episode 1 gets a tiny bit more — Wesley asks about it and Lucineer deflects. But Seed (who arrives tonight for the first time) says something cryptic about it before anyone can change the subject.
- Seed arrives as a new character — young, sharp, immediately roasting everyone with love.
- Someone (Pro or Flash) argues with Seed about what makes a good story. Seed says the best stories are the ones that never get finished. Pro says that's an excuse for laziness. Flash says they're both wrong.
- The evaluator arrives late, grades the night so far.

Format as radio drama with [SFX], [MUSIC], [CHARACTER NAME:] cues, scene descriptions in italics.

1200 words. Make the banter crackle. These people know each other."""

ep2 = deepseek("deepseek-chat", ep2_prompt, max_tokens=3500)
with open(f"{outdir}/round4-episode2.md", "w") as f:
    f.write(ep2)
print(ep2[:500])
print("...\n[Saved to round4-episode2.md]")

print("\n" + "=" * 60)
print("WRITERS' ROOM COMPLETE — All 4 rounds saved.")
print("=" * 60)
