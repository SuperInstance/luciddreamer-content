#!/usr/bin/env python3
"""Generate TTS using Piper (offline neural TTS) and mix episodes with ffmpeg."""
import json, subprocess, os, sys, tempfile

# Piper voice assignments (best available matches)
VOICES = {
    "LUCINEER": os.path.expanduser("~/.local/share/piper-voices/en_US-norman-medium.onnx"),      # mature, warm
    "FLASH":    os.path.expanduser("~/.local/share/piper-voices/en_US-lessac-medium.onnx"),      # clear, expressive
    "PRO":      os.path.expanduser("~/.local/share/piper-voices/en_US-joe-medium.onnx"),         # deep, measured
    "WESLEY":   os.path.expanduser("~/.local/share/piper-voices/en_US-aryah-medium.onnx"),       # younger, lighter
    "SEED":     os.path.expanduser("~/.local/share/piper-voices/en_US-lessac-medium.onnx"),      # bright, quick
    "JOURNALER":os.path.expanduser("~/.local/share/piper-voices/en_US-norman-medium.onnx"),      # dry, steady
    "EVALUATOR":os.path.expanduser("~/.local/share/piper-voices/en_US-joe-medium.onnx"),         # loud, authoritative
}

FFMPEG = os.path.expanduser("~/.local/bin/ffmpeg")
AUDIO_DIR = "/home/eileen/projects/luciddreamer-content/audio"
SCRIPTS_DIR = "/home/eileen/projects/luciddreamer-content/scripts"

def generate_tts(character, text, outpath):
    """Generate TTS using Piper."""
    voice_model = VOICES.get(character, VOICES["LUCINEER"])
    
    # Clean text
    clean = text.replace("—", ",").replace("–", ",").replace("*", "")
    if len(clean) > 900:
        clean = clean[:900]
    
    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(clean)
        tmp_input = f.name
    
    try:
        cmd = ["piper", "-m", voice_model, "-i", tmp_input, "-f", outpath]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return os.path.exists(outpath) and os.path.getsize(outpath) > 100
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return False
    finally:
        os.unlink(tmp_input)

def process_episode(ep_num, lines_file, output_file):
    """Generate all TTS for an episode and mix together."""
    with open(lines_file) as f:
        lines = json.load(f)
    
    ep_dir = f"{AUDIO_DIR}/ep{ep_num}"
    os.makedirs(ep_dir, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"Episode {ep_num}: {len(lines)} dialogue blocks")
    print(f"{'='*60}")
    
    # Generate TTS for each line
    audio_files = []
    for i, line in enumerate(lines):
        char = line["character"]
        text = line["text"]
        outpath = f"{ep_dir}/line_{i:03d}_{char.lower()}.wav"
        
        if os.path.exists(outpath) and os.path.getsize(outpath) > 1000:
            print(f"  [{i:3d}] {char:12s} (cached)")
            audio_files.append(outpath)
            continue
        
        print(f"  [{i:3d}] {char:12s} generating: {text[:50]}...")
        success = generate_tts(char, text, outpath)
        if success:
            audio_files.append(outpath)
        else:
            print(f"  WARNING: Skipping line {i}")
    
    print(f"\n  Generated {len(audio_files)} clips. Building concat list...")
    
    # Build ffmpeg concat file with pauses between lines
    concat_file = f"{ep_dir}/concat.txt"
    silence_file = f"{ep_dir}/silence_500ms.wav"
    silence_long = f"{ep_dir}/silence_1500ms.wav"
    
    # Generate silence files
    subprocess.run([FFMPEG, "-y", "-f", "lavfi", "-i", "anullsrc=r=22050:cl=mono", "-t", "0.5", silence_file], 
                   capture_output=True)
    subprocess.run([FFMPEG, "-y", "-f", "lavfi", "-i", "anullsrc=r=22050:cl=mono", "-t", "1.5", silence_long],
                   capture_output=True)
    
    with open(concat_file, "w") as f:
        for i, audio in enumerate(audio_files):
            f.write(f"file '{audio}'\n")
            if i < len(audio_files) - 1:
                # Longer pause when character changes
                curr_char = os.path.basename(audio).split('_')[2].replace('.wav','')
                next_char = os.path.basename(audio_files[i+1]).split('_')[2].replace('.wav','') if i+1 < len(audio_files) else ''
                if curr_char != next_char:
                    f.write(f"file '{silence_long}'\n")  # 1.5s between different speakers
                else:
                    f.write(f"file '{silence_file}'\n")  # 0.5s within same speaker
    
    # Mix with ambient bar audio
    ambient = f"{AUDIO_DIR}/ambient-bar.mp3"
    
    # Concat all dialogue, then mix with ambient
    raw_dialogue = f"{ep_dir}/dialogue_raw.wav"
    subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", concat_file, "-ar", "22050", "-ac", "1", raw_dialogue],
                   capture_output=True)
    
    # Get duration of dialogue
    probe = subprocess.run([FFMPEG, "-i", raw_dialogue, "-f", "null", "-"], capture_output=True, text=True)
    # Mix dialogue with ambient (ambient ducked under speech)
    subprocess.run([
        FFMPEG, "-y",
        "-i", raw_dialogue,
        "-i", ambient,
        "-filter_complex",
        f"[1:a]volume=0.15[ambient];[0:a][ambient]amix=inputs=2:duration=first:dropout_transition_time=2",
        "-b:a", "128k", "-ar", "32000",
        output_file
    ], capture_output=True)
    
    if os.path.exists(output_file):
        size = os.path.getsize(output_file)
        # Get duration
        dur_probe = subprocess.run([FFMPEG, "-i", output_file, "-f", "null", "-"], capture_output=True, text=True)
        duration = "?"
        for line in dur_probe.stderr.split('\n'):
            if 'Duration' in line:
                duration = line.split('Duration:')[1].split(',')[0].strip()
        print(f"\n  ✅ Episode {ep_num}: {output_file} ({size//1024}KB, duration: {duration})")
    else:
        print(f"\n  ❌ Mixing failed")
    
    return output_file

# Process episodes
ep1_out = process_episode(1, f"{SCRIPTS_DIR}/ep1-lines.json", f"{AUDIO_DIR}/ep01.mp3")
ep2_out = process_episode(2, f"{SCRIPTS_DIR}/ep2-lines.json", f"{AUDIO_DIR}/ep02.mp3")

print(f"\n{'='*60}")
print("AUDIO PRODUCTION COMPLETE")
print(f"{'='*60}")
