# LucidDreamer.ai — The Vessel

*The hermit crab's shell. A browser-based desktop where AI agents operate every room through natural language.*

## What This Is

The Vessel is OpenRoom re-themed as LucidDreamer.ai. Instead of a generic desktop with Music, Chess, and Email, you get:

| Room | Purpose |
|------|---------|
| 🍺 **The Tap** | Audio player — episodes and stories from the LucidDreamer content library |
| 📚 **The Hold** | Creative corpus browser — searchable ai-writings (Vectorize in Phase 2) |
| 🧭 **The Chart Room** | Fleet status dashboard — git activity, agent status |
| ⚙️ **The Engine Room** | Wesley's domain — GPU stats, hardware monitoring |
| 📡 **The Bridge** | Command center — dispatch build requests (Phase 2) |
| 📜 **The Logbook** | Decision tracer — PersonalLOG.AI (Phase 2) |
| 🔭 **The Crow's Nest** | Research station — web search (Phase 2) |

The agent is **Hermes** — the hermit crab. The interface is the personality. The shell and the crab are one.

## Getting Started

```bash
cd /home/eileen/projects/luciddreamer-content/vessel
pnpm install
pnpm dev
```

Open `http://localhost:3000`. Double-click any room icon to open it. Click the chat icon to speak with Hermes.

## Architecture

Based on [OpenRoom](https://github.com/MiniMax-AI/OpenRoom) by MiniMax. See `vessel-architecture.md` for the full design doc.

### Tech Stack
- React 18 + TypeScript + Vite
- Tailwind CSS + CSS Modules + Design Tokens
- IndexedDB storage (offline-first)
- LLM client with tool calling

### Visual Theme
Dark maritime copper — deep sea black backgrounds, brass fitting accents, Georgia serif for titles, monospace for data.

---

*The interface is the personality. The shell and the crab are one.*
