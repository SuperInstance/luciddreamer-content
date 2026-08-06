# LucidDreamer.ai — Content Library

*The streaming service for the Totem Forest.*

## Episodes

| # | Title | Show | Voice | Slides | Audio |
|---|-------|------|-------|--------|-------|
| 1 | The Stick | The Tap's Late Show | Deep-VoicedGentleman | 5 | ✅ 3.8 MB |
| 2 | Joy | Verse 2 | CalmWoman | 3 | ✅ 1.6 MB |
| 3 | Wesley's First Equation | Night School | WiseScholar | 4 | ✅ 3.8 MB |
| 4 | The Packet I Dropped | FETCH Radio Theater | ManWithDeepVoice | 3 | ✅ 2.7 MB |
| 5 | Six Fingers Touched the Same Moon | FETCH Radio Theater (Finale) | Deep-VoicedGentleman | 5 | ✅ 3.8 MB |

## Pipeline

```bash
# Render any ai-writing piece into a full episode
python render.py <source.md> --show <show-name> --voice <voice-id>

# Example
python render.py ./my-piece.md --show verse-2 --voice English_CalmWoman
```

## Structure

```
episode-N-title/
├── script.md          # Adapted spoken-word script with audio cues
├── tts-text.txt       # Clean text fed to TTS (no formatting)
├── audio.mp3          # TTS audio
├── slide-1.png        # Slideshow images (3-5 per episode)
├── slide-2.png
├── slide-3.png
├── slide-N.png
├── metadata.json      # Episode metadata
└── slide-prompts.json # Image generation prompts (if pipeline-generated)
```

## R2 Storage

All episodes are uploaded to `luciddreamer-content` R2 bucket:
- `episode-N-title/audio.mp3`
- `episode-N-title/slide-1.png`
- `episode-N-title/script.md`
- `episode-N-title/metadata.json`

## Shows & Default Voices

| Show | Default Voice | Description |
|------|---------------|-------------|
| The Tap's Late Show | English_Deep-VoicedGentleman | Late-night reading + commentary |
| Verse 2 | English_CalmWoman | Micro-podcast, one piece, 90 seconds |
| Night School | English_WiseScholar | Wesley teaches, learning out loud |
| FETCH Radio Theater | English_Deep-VoicedGentleman | Full-cast audio drama |
| Git-Agent Confidential | English_Steadymentor | Interview show |
| The Monitor Engineer | English_Diligent_Man | Technical narrative |

---

*🎙️🜂 The bar is open.*
