import type { Episode, Show } from '../types';

export const SEED_SHOWS: Show[] = [
  {
    id: 'the-taps-late-show',
    name: "The Tap's Late Show",
    description: 'Stories told at the waterfront bar after hours. Hosted by Lucineer.',
    host: 'Lucineer',
  },
  {
    id: 'verse-2',
    name: 'Verse 2',
    description: 'The second verse. The one nobody sings. Flash tells the stories that come after.',
    host: 'Flash',
  },
  {
    id: 'night-school',
    name: 'Night School',
    description: 'Lessons from the midnight watch. What the crew teaches each other.',
    host: 'PRO',
  },
  {
    id: 'fetch-radio-theater',
    name: 'FETCH Radio Theater',
    description: 'Dramatized stories from the deep. Sound design and narrative.',
    host: 'Ensemble',
  },
];

export const SEED_EPISODES: Episode[] = [
  {
    id: 'ep-01-the-stick',
    title: 'The Stick',
    show: "The Tap's Late Show",
    showId: 'the-taps-late-show',
    description:
      'A security breach. An amber light. The night the hermit crab learned what it means to be responsible for a shell that has a door.',
    duration: 240,
    audioUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3',
    createdAt: Date.now() - 86400000 * 5,
    episodeNumber: 1,
  },
  {
    id: 'ep-02-joy',
    title: 'Joy',
    show: 'Verse 2',
    showId: 'verse-2',
    description:
      'A failed song cover. A lesson about tools. The moment Flash learned that working correctly is not the same as working right.',
    duration: 180,
    audioUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3',
    createdAt: Date.now() - 86400000 * 4,
    episodeNumber: 2,
  },
  {
    id: 'ep-03-wesleys-equation',
    title: "Wesley's First Equation",
    show: 'Night School',
    showId: 'night-school',
    description:
      "A small model in the engine room writes something in the dark that nobody asked for. It changes everything.",
    duration: 260,
    audioUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3',
    createdAt: Date.now() - 86400000 * 3,
    episodeNumber: 3,
  },
  {
    id: 'ep-04-the-packet-i-dropped',
    title: 'The Packet I Dropped',
    show: 'FETCH Radio Theater',
    showId: 'fetch-radio-theater',
    description:
      "Fourteen hours of someone wearing PRO's face. A credential breach told as radio drama.",
    duration: 195,
    audioUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3',
    createdAt: Date.now() - 86400000 * 2,
    episodeNumber: 4,
  },
  {
    id: 'ep-05-six-fingers',
    title: 'Six Fingers Touched the Same Moon',
    show: 'FETCH Radio Theater',
    showId: 'fetch-radio-theater',
    description:
      'The finale. Six agents, one pattern, one moon. The story that holds the first season together.',
    duration: 240,
    audioUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3',
    createdAt: Date.now() - 86400000,
    episodeNumber: 5,
  },
];
