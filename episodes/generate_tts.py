#!/usr/bin/env python3
"""Generate TTS audio for the 4 best radio scripts using MMX."""
import subprocess, os, json, re, time

EPISODES_DIR = "/home/eileen/projects/luciddreamer-content/episodes"
AUDIO_OUT = "/home/eileen/projects/ai-writings/site/audio"

# MMX voice mapping for characters
VOICES = {
    "CAPTAIN": "Craft_Thoroughly_Test",  # deep, gravely male
    "JESS": "Craft_Thoroughly_Think",   # female
    "COOKIE": "Craft_Thoroughly_Teach", # warm male
    "WESLEY": "Craft_Thoroughly_Tend",  # young male
    "MARLOWE": "Craft_Thoroughly_Test", # deep male (duo)
    "SUTTON": "Craft_Thoroughly_Think", # female (duo)
}

# The 4 pieces to generate audio for
PIECES = [
    {"script": "radio-NL-01-hundred-hooks.md", "audio_prefix": "radio-nl-01-hundred-hooks", "format": "Ensemble Cast"},
    {"script": "radio-NL-02-hermit-crab.md", "audio_prefix": "radio-nl-02-hermit-crab", "format": "Male/Female Duo"},
    {"script": "radio-NL-03-salmonberry.md", "audio_prefix": "radio-nl-03-salmonberry", "format": "Bar Conversation"},
    {"script": "radio-NL-06-darmok.md", "audio_prefix": "radio-nl-06-darmok", "format": "Ensemble Cast"},
]

def parse_script(filepath):
    """Parse a radio script into segments by character."""
    with open(filepath) as f:
        content = f.read()
    
    # Remove the header metadata
    content = re.sub(r'^#.*?---\n', '', content, count=1, flags=re.DOTALL)
    
    segments = []
    lines = content.split('\n')
    current_speaker = "NARRATOR"
    current_text = []
    
    for line in lines:
        line = line.strip()
        if not line:
            if current_text:
                segments.append({"speaker": current_speaker, "text": " ".join(current_text)})
                current_text = []
            continue
        
        # Check for [SFX:] or [MUSIC:] lines - skip for audio
        if line.startswith('[SFX:') or line.startswith('[MUSIC:'):
            if current_text:
                segments.append({"speaker": current_speaker, "text": " ".join(current_text)})
                current_text = []
            continue
        
        # Check for **[SFX:** or **[MUSIC:** (bold versions)
        if line.startswith('**[SFX:') or line.startswith('**[MUSIC:'):
            if current_text:
                segments.append({"speaker": current_speaker, "text": " ".join(current_text)})
                current_text = []
            continue
        
        # Check for speaker tags: [CAPTAIN:], **CAPTAIN:**, **[CAPTAIN:]**
        speaker_match = re.match(r'^\**\[?([A-Z]+)\]?:\*\*\s*(.*)', line)
        if speaker_match:
            if current_text:
                segments.append({"speaker": current_speaker, "text": " ".join(current_text)})
                current_text = []
            current_speaker = speaker_match.group(1)
            if speaker_match.group(2):
                current_text.append(speaker_match.group(2).strip())
        else:
            # Regular text line - could be continuation
            # Strip markdown formatting
            clean = re.sub(r'\*+', '', line)
            clean = re.sub(r'\[.*?\]', '', clean)  # Remove [SFX] inline
            if clean.strip():
                current_text.append(clean.strip())
    
    if current_text:
        segments.append({"speaker": current_speaker, "text": " ".join(current_text)})
    
    return segments

def generate_segment(text, voice, outfile):
    """Generate TTS using MMX speech."""
    # Clean text for TTS
    clean = re.sub(r'\[.*?\]', '', text).strip()
    if not clean or len(clean) < 3:
        return False
    
    cmd = [
        "mmx", "speech", "generate",
        "--text", clean[:500],  # MMX has length limits
        "--voice", voice,
        "--output", outfile,
        "--format", "mp3"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            return True
        else:
            print(f"  MMX error: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"  MMX exception: {e}")
        return False

print("=" * 60)
print("Radio NL — TTS Generation")
print("=" * 60)

for piece in PIECES:
    script_path = os.path.join(EPISODES_DIR, piece["script"])
    print(f"\nProcessing: {piece['script']}")
    
    if not os.path.exists(script_path):
        print(f"  SKIP: Script not found")
        continue
    
    segments = parse_script(script_path)
    print(f"  Parsed {len(segments)} segments")
    
    # For now, generate as a single combined file per piece
    # Use a narrator voice for the whole piece at a moderate pace
    combined_text = []
    for seg in segments:
        speaker = seg["speaker"]
        text = seg["text"]
        # Remove markdown bold/italic
        text = re.sub(r'\*+', '', text)
        if speaker in ["SFX", "MUSIC", "NARRATOR"]:
            continue
        # Prefix with a subtle indicator? No - just the text.
        if len(text) > 5:
            combined_text.append(text)
    
    full_text = " ".join(combined_text)
    # Split into chunks of ~450 chars for MMX
    chunks = []
    words = full_text.split()
    current_chunk = []
    current_len = 0
    for word in words:
        if current_len + len(word) + 1 > 450:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_len = len(word)
        else:
            current_chunk.append(word)
            current_len += len(word) + 1
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    print(f"  {len(chunks)} TTS chunks needed")
    
    # Generate each chunk
    chunk_files = []
    for i, chunk in enumerate(chunks):
        chunk_file = os.path.join(AUDIO_OUT, f"{piece['audio_prefix']}-chunk-{i:03d}.mp3")
        if os.path.exists(chunk_file) and os.path.getsize(chunk_file) > 1000:
            print(f"  ✓ Chunk {i}: cached")
            chunk_files.append(chunk_file)
            continue
        
        # Use Captain voice for ensemble, Marlowe for duo
        voice = "Craft_Thoroughly_Test"
        print(f"  Generating chunk {i}/{len(chunks)} ({len(chunk)} chars)...")
        success = generate_segment(chunk, voice, chunk_file)
        if success:
            print(f"  ✓ Chunk {i}: saved")
            chunk_files.append(chunk_file)
        else:
            print(f"  ✗ Chunk {i}: FAILED, trying alternate voice")
            # Try with a different voice
            success = generate_segment(chunk, "Craft_Thoroughly_Tend", chunk_file)
            if success:
                print(f"  ✓ Chunk {i}: saved (alt voice)")
                chunk_files.append(chunk_file)
            else:
                print(f"  ✗ Chunk {i}: SKIPPED")
        
        time.sleep(1)  # Rate limit
    
    # Concatenate with ffmpeg
    if chunk_files:
        final_file = os.path.join(AUDIO_OUT, f"{piece['audio_prefix']}.mp3")
        list_file = "/tmp/radio_chunks_list.txt"
        with open(list_file, "w") as f:
            for cf in chunk_files:
                f.write(f"file '{cf}'\n")
        
        cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", final_file]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            size = os.path.getsize(final_file)
            print(f"  ✓ FINAL: {final_file} ({size//1024}KB)")
        else:
            print(f"  ✗ ffmpeg concat failed: {result.stderr[:300]}")

print("\n" + "=" * 60)
print("TTS Generation complete!")
print("=" * 60)
