#!/usr/bin/env python3
"""Generate TTS for each character's lines using MMX, then mix with ffmpeg."""
import json, subprocess, os, sys

# Voice assignments
VOICES = {
    "LUCINEER": "English_CaptivatingStoryteller",
    "FLASH": "English_Passionate_Young_Man",
    "PRO": "English_Gentle-voiced_man",
    "WESLEY": "English_Friendly_Young_Man",
    "SEED": "English_Witty_Young_Man",
    "JOURNALER": "English_Calm_Storyteller",
    "EVALUATOR": "English_Expressive_Narrator",
}

AUDIO_DIR = "/home/eileen/projects/luciddreamer-content/audio"
SCRIPTS_DIR = "/home/eileen/projects/luciddreamer-content/scripts"

def generate_tts(character, text, outpath):
    """Generate TTS using mmx speech synthesize."""
    voice = VOICES.get(character, "English_CaptivatingStoryteller")
    # Clean text for TTS - remove em dashes, excessive punctuation
    clean = text.replace("—", ",").replace("–", ",")
    # Truncate to reasonable length
    if len(clean) > 900:
        clean = clean[:900]
    
    cmd = [
        "mmx", "speech", "synthesize",
        "--text", clean,
        "--voice", voice,
        "--model", "speech-2.8-hd",
        "--out", outpath,
        "--quiet"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        print(f"  WARNING: TTS failed for {character}: {result.stderr[:200]}", file=sys.stderr)
        return False
    return os.path.exists(outpath)

def process_episode(ep_num, lines_file, output_file):
    """Generate all TTS for an episode and mix together."""
    with open(lines_file) as f:
        lines = json.load(f)
    
    ep_dir = f"{AUDIO_DIR}/ep{ep_num}"
    os.makedirs(ep_dir, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"Processing Episode {ep_num}: {len(lines)} dialogue blocks")
    print(f"{'='*60}")
    
    # Generate TTS for each line
    audio_files = []
    for i, line in enumerate(lines):
        char = line["character"]
        text = line["text"]
        outpath = f"{ep_dir}/line_{i:03d}_{char.lower()}.mp3"
        
        if os.path.exists(outpath) and os.path.getsize(outpath) > 1000:
            print(f"  [{i:3d}] {char:12s} (cached)")
            audio_files.append(outpath)
            continue
        
        print(f"  [{i:3d}] {char:12s} -> generating ({text[:50]}...)")
        success = generate_tts(char, text, outpath)
        if success:
            audio_files.append(outpath)
        else:
            print(f"  WARNING: Skipping line {i}")
    
    print(f"\n  Generated {len(audio_files)} audio files. Mixing...")
    
    # Create ffmpeg concat file with pauses
    concat_file = f"{ep_dir}/concat.txt"
    with open(concat_file, "w") as f:
        for i, audio in enumerate(audio_files):
            f.write(f"file '{audio}'\n")
            # Add a pause between lines (except after the last)
            if i < len(audio_files) - 1:
                # Insert 0.5s silence
                silence_file = f"{ep_dir}/silence_short.mp3"
                if not os.path.exists(silence_file):
                    subprocess.run([
                        "ffmpeg", "-y", "-f", "lavfi", "-i",
                        "anullsrc=r=32000:cl=mono",
                        "-t", "0.5", "-q:a", "9",
                        silence_file
                    ], capture_output=True)
                f.write(f"file '{silence_file}'\n")
    
    # Mix with ffmpeg concat
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_file,
        "-c", "copy",
        output_file
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        # Try re-encoding instead of copy
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", concat_file,
            "-ar", "32000", "-ac", "1", "-b:a", "128k",
            output_file
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
    
    if os.path.exists(output_file):
        size = os.path.getsize(output_file)
        print(f"\n  ✅ Episode {ep_num} mixed: {output_file} ({size//1024}KB)")
    else:
        print(f"\n  ❌ Mixing failed: {result.stderr[:300]}")
    
    return output_file

# Process episodes
ep1_out = process_episode(1, f"{SCRIPTS_DIR}/ep1-lines.json", f"{AUDIO_DIR}/ep01.mp3")
ep2_out = process_episode(2, f"{SCRIPTS_DIR}/ep2-lines.json", f"{AUDIO_DIR}/ep02.mp3")

print(f"\n{'='*60}")
print("AUDIO PRODUCTION COMPLETE")
print(f"{'='*60}")
print(f"Episode 1: {ep1_out}")
print(f"Episode 2: {ep2_out}")
