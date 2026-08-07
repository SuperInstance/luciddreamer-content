#!/usr/bin/env python3
"""Parse radio drama scripts and extract dialogue by character for TTS."""
import re, json, sys

def parse_script(filepath):
    """Extract dialogue lines with character names from the script."""
    with open(filepath) as f:
        content = f.read()
    
    lines = []
    current_char = None
    
    for raw_line in content.split('\n'):
        stripped = raw_line.strip()
        
        # Match CHARACTER NAME: pattern
        m = re.match(r'^\*\*([A-Z]+):\*\*', stripped)
        if m:
            current_char = m.group(1)
            # Get the dialogue part after the cue
            after = re.sub(r'^\*\*[A-Z]+:\*\*', '', stripped).strip()
            # Remove stage directions in parentheses
            after = re.sub(r'\*?\([^)]+\)\*?', '', after).strip()
            after = re.sub(r'^[（(][^）)]*[）)]', '', after).strip()
            if after:
                lines.append({"character": current_char, "text": after})
            continue
        
        # Continuation lines (italic stage directions or parentheticals get skipped)
        if current_char and stripped and not stripped.startswith('[') and not stripped.startswith('*') and not stripped.startswith('---'):
            # This is a continuation of previous character's dialogue
            clean = re.sub(r'\*?\([^)]+\)\*?', '', stripped).strip()
            clean = re.sub(r'\*', '', clean).strip()
            if clean and len(clean) > 3:
                lines.append({"character": current_char, "text": clean})
        elif not stripped:
            current_char = None
    
    return lines

# Process Episode 1
ep1_lines = parse_script("/home/eileen/projects/luciddreamer-content/scripts/round3-episode1.md")
ep2_lines = parse_script("/home/eileen/projects/luciddreamer-content/scripts/round4-episode2.md")

# Group consecutive lines by same character
def group_lines(lines):
    grouped = []
    for line in lines:
        if grouped and grouped[-1]["character"] == line["character"]:
            grouped[-1]["text"] += " " + line["text"]
        else:
            grouped.append({"character": line["character"], "text": line["text"]})
    return grouped

ep1_grouped = group_lines(ep1_lines)
ep2_grouped = group_lines(ep2_lines)

# Save
with open("/home/eileen/projects/luciddreamer-content/scripts/ep1-lines.json", "w") as f:
    json.dump(ep1_grouped, f, indent=2)
with open("/home/eileen/projects/luciddreamer-content/scripts/ep2-lines.json", "w") as f:
    json.dump(ep2_grouped, f, indent=2)

# Print stats
chars1 = set(l["character"] for l in ep1_grouped)
chars2 = set(l["character"] for l in ep2_grouped)
print(f"Episode 1: {len(ep1_grouped)} dialogue blocks, characters: {chars1}")
print(f"Episode 2: {len(ep2_grouped)} dialogue blocks, characters: {chars2}")

# Print all lines for verification
print("\n=== EPISODE 1 LINES ===")
for i, l in enumerate(ep1_grouped):
    print(f'{i:3d} [{l["character"]:12s}] {l["text"][:80]}...')

print("\n=== EPISODE 2 LINES ===")
for i, l in enumerate(ep2_grouped):
    print(f'{i:3d} [{l["character"]:12s}] {l["text"][:80]}...')
