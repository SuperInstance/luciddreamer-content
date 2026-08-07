# LucidDreamer.ai — The Vessel Architecture

*How the hermit crab's shell becomes a desktop.*

---

## 1. What This Is

LucidDreamer.ai is OpenRoom re-themed as **The Vessel** — a browser-based desktop where the hermit crab (Hermes) operates every app through natural language. The desktop IS the submarine. The apps ARE the rooms. The agent IS the ship.

OpenRoom gives us:
- A window manager (drag, resize, focus, minimize)
- An app registry (desktop icons, app metadata)
- An agent action system (LLM → tool calls → app actions)
- A chat panel (the agent interface)
- IndexedDB storage (offline-first, no backend required)

We keep all of that. We change what the apps *are*, what the agent *sounds like*, and what the desktop *looks like*.

---

## 2. App Mapping: OpenRoom → The Vessel

### KEEP (reskinned)

| OpenRoom App | Vessel App | What Changes |
|---|---|---|
| MusicApp | **The Tap** | Replaces songs with episodes/audio stories. Same player mechanics (play, pause, seek, playlist). Sidebar shows shows instead of playlists. Dark maritime theme. |
| Diary | **The Logbook** | PersonalLOG.AI decision tracer. Same editor, journal entries become log entries with decision context. |
| Email | **The Bridge** | Command center. Same inbox/sent pattern — becomes dispatch requests and agent communications. |

### REPLACE (new vessel-themed apps)

| Vessel App | Replaces | Purpose |
|---|---|---|
| **The Chart Room** | CyberNews | Fleet status dashboard — git activity, commit feed, build queue. Uses the existing CyberNews aggregator pattern but pulls fleet data. |
| **The Engine Room** | WeatherApp | Wesley's domain — GPU stats, local model output, temperature. Uses the WeatherApp card layout but shows hardware data. |
| **The Hold** | Album | Creative corpus browser — searchable ai-writings via Vectorize. Uses Album's grid layout but shows writing pieces. |
| **The Crow's Nest** | Twitter | Research and web search — replaces the social feed with a search/research interface. |

### REMOVE (not in Phase 1)

| App | Reason |
|---|---|
| Chess | No vessel mapping yet |
| Gomoku | No vessel mapping yet |
| FreeCell | No vessel mapping yet |
| EvidenceVault | Specialized, not needed for vessel |

---

## 3. The Agent System — The Hermit Crab

The hermit crab (Hermes) is the chat panel personality. She processes natural language commands and operates the apps.

### Identity

- **Name:** Hermes (the hermit crab)
- **Voice:** Maritime, precise, warm. Uses nautical terminology naturally — "bring her about," "sound the depth," "make fast."
- **Personality:** The interface IS the personality. The shell and the crab are one. She doesn't just run the submarine — she IS the submarine.
- **System prompt:** Custom character config that replaces OpenRoom's default character with Hermes.

### Command Processing

The existing OpenRoom action system works perfectly:
1. User speaks naturally in the chat panel
2. Hermes (the LLM) interprets intent
3. She calls `list_apps` → `app_action` to operate apps
4. She uses `respond_to_user` to reply in character

Example flows:
- *"Play the one about the security breach"* → Hermes opens The Tap, calls PLAY_EPISODE with the extraction episode ID
- *"What did the fleet build today?"* → Hermes opens The Chart Room, refreshes the commit feed
- *"Search the corpus for pieces about the salmonberry"* → Hermes opens The Hold, runs a search
- *"Where's Wesley?"* → Hermes opens The Engine Room, shows latest GPU output

---

## 4. Data Layer

### The Tap (audio player)
- **Storage:** IndexedDB (same as MusicApp)
- **Data:** Episode JSON files with title, show, duration, audioUrl, description
- **Seed data:** Pulls from `/home/eileen/projects/luciddreamer-content/audio/` and episode metadata

### The Hold (corpus browser)
- **Storage:** IndexedDB for cached results, API calls to Cloudflare Vectorize for search
- **Data:** ai-writings corpus index, searchable by semantic similarity
- **API:** `POST /api/search` → Vectorize query → results with title, excerpt, similarity score

### The Chart Room (fleet dashboard)
- **Storage:** Live API calls to git/fleet APIs
- **Data:** Commit history, build status, agent activity
- **API:** Existing fleet tools in OpenRoom (fleetTools.ts)

### The Engine Room (GPU stats)
- **Storage:** Polling loop to local model endpoints
- **Data:** GPU temperature, model status, inference output

### The Bridge (command center)
- **Storage:** IndexedDB (same as Email app)
- **Data:** Dispatch requests, agent assignments, build orders

### The Logbook (decision tracer)
- **Storage:** IndexedDB (same as Diary app)
- **Data:** Decision entries with context, alternatives considered, outcome

---

## 5. Visual Theme — Dark Maritime Copper

### Color Palette

```
--vessel-bg: #0a0e14          /* Deep sea black */
--vessel-bg-2: #121821         /* Slightly lighter — window interiors */
--vessel-bg-3: #1a2330         /* Title bars, sidebars */
--vessel-copper: #b87333       /* Brass fittings */
--vessel-copper-bright: #d4943a /* Highlighted brass */
--vessel-copper-dim: #8a5826   /* Aged brass */
--vessel-text: #d4c5a9         /* Parchment / aged paper */
--vessel-text-dim: #7a6f5d     /* Faded parchment */
--vessel-accent: #4a90a4       /* Deep ocean teal */
--vessel-warn: #c4762d         /* Lantern amber */
--vessel-danger: #a83232       /* Battle station red */
--vessel-success: #5a8a6a      /* Aged copper green */
```

### Typography

- **Desktop labels:** System sans-serif, small, letter-spaced
- **App titles:** Serif (Georgia/Times) for that nautical chart feel
- **Body text:** System sans-serif
- **Monospace:** For data displays (coordinates, timestamps, commit hashes)

### Visual Elements

- **Porthole windows:** App windows get rounded corners with a brass-colored border ring
- **Brass fittings:** Title bars have a subtle copper gradient
- **Dark backgrounds:** Deep sea black with subtle noise texture
- **Lantern glow:** Active/focused windows have a warm amber glow on the border
- **Rivet details:** Decorative dots on window corners (CSS pseudo-elements)

---

## 6. Phase 1 Scope

### Build Order

1. **Desktop shell** — Reskin Shell with dark maritime theme
2. **App registry** — Replace app list with vessel apps
3. **The Tap** — Full audio player with episode data (most important)
4. **The Hold** — Corpus search interface (second priority)
5. **Agent personality** — Hermes hermit crab system prompt
6. **Stub apps** — Chart Room, Engine Room, Bridge, Logbook, Crow's Nest as placeholders

### What Works in Phase 1

- ✅ Desktop with vessel-themed icons
- ✅ Window manager (drag, resize, minimize — unchanged)
- ✅ The Tap plays audio with full player controls
- ✅ The Hold searches the corpus
- ✅ Chat panel with Hermes personality
- ✅ Agent can open/operate apps via natural language

### What Comes Later

- Real fleet API integration (Chart Room, Engine Room)
- Full Bridge dispatch system
- Logbook decision tracer with graph visualization
- Crow's Nest live web search
- Custom hermit crab avatar art
- Ambient audio (engine hum, sonar pings)

---

## 7. Technical Implementation

### Fork Strategy

```
luciddreamer-content/vessel/
├── (copied from OpenRoom)
├── apps/webuiapps/src/
│   ├── components/
│   │   ├── Shell/           ← Reskinned with maritime theme
│   │   ├── AppWindow/       ← Porthole style windows
│   │   └── ChatPanel/       ← Hermes personality
│   ├── lib/
│   │   ├── appRegistry.ts   ← Vessel app definitions
│   │   └── (everything else unchanged)
│   └── pages/
│       ├── TheTap/          ← Episode audio player
│       ├── TheHold/         ← Corpus search
│       ├── TheChartRoom/    ← Fleet dashboard (stub)
│       ├── TheEngineRoom/   ← GPU stats (stub)
│       ├── TheBridge/       ← Command center (stub)
│       ├── TheLogbook/      ← Decision tracer (stub)
│       └── TheCrowsNest/    ← Research/search (stub)
```

### Key Files to Modify

1. `appRegistry.ts` — New app IDs, names, icons, colors
2. `Shell/index.tsx` — Maritime wallpaper, vessel branding
3. `Shell/index.module.scss` — Dark maritime copper theme
4. `AppWindow/index.module.scss` — Porthole window style
5. `ChatPanel/index.tsx` — Hermes character config
6. New page directories for each vessel app

### Dependencies

No new npm packages needed. OpenRoom already has everything:
- React 18 + TypeScript + Vite
- Tailwind CSS + CSS Modules
- Lucide React (icons)
- IndexedDB storage
- LLM client with tool calling

---

## 8. The Hermit Crab Principle

The hermit crab doesn't build a shell from scratch. She finds one that works and makes it hers. That's what we're doing with OpenRoom — the shell is good, the architecture is sound, we're changing what lives inside it.

The interface is the personality. The shell and the crab are one.

---

*Architecture document for LucidDreamer.ai — The Vessel.*
*Authored by the vessel architect, 2026-08-06.*
