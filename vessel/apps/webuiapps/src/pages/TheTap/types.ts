export interface Episode {
  id: string;
  title: string;
  show: string;
  showId: string;
  description: string;
  duration: number;
  audioUrl: string;
  createdAt: number;
  episodeNumber: number;
}

export interface Show {
  id: string;
  name: string;
  description: string;
  host: string;
}

export interface PlayerState {
  currentEpisodeId: string | null;
  isPlaying: boolean;
  currentTime: number;
  volume: number;
  playMode: 'sequential' | 'repeat-one' | 'shuffle';
}

export interface AppState {
  activeShowId: string | null;
  player: PlayerState;
}
