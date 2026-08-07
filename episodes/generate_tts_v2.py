#!/usr/bin/env python3
"""Generate TTS audio for radio scripts using MMX."""
import subprocess, os, re, time, sys

EPISODES_DIR = "/home/eileen/projects/luciddreamer-content/episodes"
AUDIO_OUT = "/home/eileen/projects/ai-writings/site/audio"
os.makedirs(AUDIO_OUT, exist_ok=True)

# The 4 pieces to generate audio for
PIECES = [
    {
        "script": "radio-NL-01-hundred-hooks.md",
        "audio_prefix": "radio-nl-01-hundred-hooks",
        "voice": "English_Deep-VoicedGentleman",
    },
    {
        "script": "radio-NL-02-hermit-crab.md", 
        "audio_prefix": "radio-nl-02-hermit-crab",
        "voice": "English_expressive_narrator",
    },
    {
        "script": "radio-NL-03-salmonberry.md",
        "audio_prefix": "radio-nl-03-salmonberry",
        "voice": "English_CaptivatingStoryteller",
    },
    {
        "script": "radio-NL-06-darmok.md",
        "audio_prefix": "radio-nl-06-darmok",
        "voice": "English_Deep-VoicedGentleman",
    },
]

def extract_dialogue(filepath):
    """Extract just the spoken lines from a radio script."""
    with open(filepath) as f:
        content = f.read()
    
    # Remove header
    content = re.sub(r'^#.*?---\n', '', content, count=1, flags=re.DOTALL)
    
    lines = content.split('\n')
    spoken = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Skip SFX and MUSIC lines
        if re.match(r'\**\[?(SFX|MUSIC)', line):
            continue
        
        # Skip pure section headers and metadata
        if line.startswith('#') and not any(c in line for c in [':']):
            continue
        
        # Remove speaker tags [CAPTAIN:], **CAPTAIN:**, etc
        line = re.sub(r'^\**\[?[A-Z]+\]?:\**\s*', '', line)
        
        # Remove inline [SFX:...] and [MUSIC:...]
        line = re.sub(r'\[(?:SFX|MUSIC):[^\]]*\]', '', line)
        
        # Remove markdown formatting
        line = re.sub(r'\*+', '', line)
        line = re.sub(r'\*:', '', line)
        
        # Remove "END OF BROADCAST" etc
        if re.match(r'^(END|FIN|\[END)', line):
            continue
        
        # Skip italic byline
        if line.startswith('*Radio NL') or line.startswith('*From the'):
            continue
        
        line = line.strip()
        if len(line) > 5:
            spoken.append(line)
    
    return spoken

def chunk_text(lines, max_chars=900):
    """Group lines into chunks under max_chars."""
    chunks = []
    current = []
    current_len = 0
    
    for line in lines:
        if current_len + len(line) + 1 > max_chars:
            chunks.append(" ".join(current))
            current = [line]
            current_len = len(line)
        else:
            current.append(line)
            current_len += len(line) + 1
    
    if current:
        chunks.append(" ".join(current))
    
    return chunks

def generate_tts(text, voice, outfile):
    """Generate TTS using MMX speech synthesize."""
    cmd = [
        "mmx", "speech", "synthesize",
        "--text", text,
        "--voice", voice,
        "--format", "mp3",
        "--out", outfile,
        "--quiet"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0 and os.path.exists(outfile) and os.path.getsize(outfile) > 1000:
            return True
        else:
            print(f"    stderr: {result.stderr[:200] if result.stderr else 'none'}")
            return False
    except subprocess.TimeoutExpired:
        print(f"    TIMEOUT")
        return False
    except Exception as e:
        print(f"    ERROR: {e}")
        return False

print("=" * 60)
print("Radio NL — TTS Generation via MMX")
print("=" * 60)

for piece in PIECES:
    script_path = os.path.join(EPISODES_DIR, piece["script"])
    print(f"\n{'─' * 50}")
    print(f"Processing: {piece['script']}")
    print(f"Voice: {piece['voice']}")
    
    if not os.path.exists(script_path):
        print(f"  SKIP: Script not found")
        continue
    
    # Check if final file already exists
    final_file = os.path.join(AUDIO_OUT, f"{piece['audio_prefix']}.mp3")
    if os.path.exists(final_file) and os.path.getsize(final_file) > 50000:
        print(f"  ✓ Already exists ({os.path.getsize(final_file)//1024}KB), skipping")
        continue
    
    lines = extract_dialogue(script_path)
    print(f"  Extracted {len(lines)} spoken lines")
    
    chunks = chunk_text(lines, max_chars=900)
    print(f"  {len(chunks)} TTS chunks needed")
    
    chunk_files = []
    for i, chunk in enumerate(chunks):
        chunk_file = os.path.join(AUDIO_OUT, f"{piece['audio_prefix']}-chunk-{i:03d}.mp3")
        
        if os.path.exists(chunk_file) and os.path.getsize(chunk_file) > 1000:
            print(f"  ✓ Chunk {i+1}/{len(chunks)}: cached ({os.path.getsize(chunk_file)//1024}KB)")
            chunk_files.append(chunk_file)
            continue
        
        print(f"  Generating chunk {i+1}/{len(chunks)} ({len(chunk)} chars)...")
        success = generate_tts(chunk, piece["voice"], chunk_file)
        
        if success:
            print(f"  ✓ Chunk {i+1}: {os.path.getsize(chunk_file)//1024}KB")
            chunk_files.append(chunk_file)
        else:
            print(f"  ✗ Chunk {i+1}: FAILED")
        
        time.sleep(2)
    
    # Concatenate all chunks with ffmpeg
    if len(chunk_files) > 1:
        list_file = f"/tmp/{piece['audio_prefix']}-concat.txt"
        with open(list_file, "w") as f:
            for cf in chunk_files:
                f.write(f"file '{cf}'\n")
        
        print(f"  Concatenating {len(chunk_files)} chunks...")
        cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", final_file]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(f"  ✓ FINAL: {final_file} ({os.path.getsize(final_file)//1024}KB)")
        else:
            print(f"  ✗ ffmpeg failed, using first chunk as fallback")
            if chunk_files:
                import shutil
                shutil.copy2(chunk_files[0], final_file)
    elif len(chunk_files) == 1:
        import shutil
        shutil.copy2(chunk_files[0], final_file)
        print(f"  ✓ FINAL: {final_file} ({os.path.getsize(final_file)//1024}KB)")
    else:
        print(f"  ✗ No chunks generated")

print(f"\n{'=' * 60}")
print("TTS Generation complete!")
print(f"{'=' * 60}")
