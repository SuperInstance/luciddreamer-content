# The Tap — Guide

The Tap is the waterfront bar. Audio player for LucidDreamer.ai episodes.

## Directory Structure

```
/episodes/{episode-id}.json   — Episode JSON files
/shows/{show-id}.json         — Show JSON files
/state.json                   — Player state
```

## Episode JSON Schema

```json
{
  "id": "ep-01-the-stick",
  "title": "The Stick",
  "show": "The Tap's Late Show",
  "showId": "the-taps-late-show",
  "description": "A security breach. An amber light...",
  "duration": 240,
  "audioUrl": "https://...",
  "createdAt": 1234567890,
  "episodeNumber": 1
}
```

## Show JSON Schema

```json
{
  "id": "the-taps-late-show",
  "name": "The Tap's Late Show",
  "description": "Stories told at the waterfront bar.",
  "host": "Lucineer"
}
```
