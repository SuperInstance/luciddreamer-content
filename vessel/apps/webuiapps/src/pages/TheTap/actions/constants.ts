export const APP_ID = 20;
export const APP_NAME = 'theTap';

export const EPISODES_DIR = '/episodes';
export const SHOWS_DIR = '/shows';
export const STATE_FILE = '/state.json';

export const ActionTypes = {
  PLAY_EPISODE: 'PLAY_EPISODE',
  PAUSE: 'PAUSE',
  RESUME: 'RESUME',
  NEXT_EPISODE: 'NEXT_EPISODE',
  PREV_EPISODE: 'PREV_EPISODE',
  SET_VOLUME: 'SET_VOLUME',
  SEEK: 'SEEK',
  SELECT_SHOW: 'SELECT_SHOW',
  SET_PLAY_MODE: 'SET_PLAY_MODE',
  REFRESH_EPISODES: 'REFRESH_EPISODES',
  SYNC_STATE: 'SYNC_STATE',
} as const;

export const DEFAULT_PLAYER_STATE = {
  currentEpisodeId: null as string | null,
  isPlaying: false,
  currentTime: 0,
  volume: 0.7,
  playMode: 'sequential' as const,
};

export const DEFAULT_APP_STATE = {
  activeShowId: null as string | null,
  player: DEFAULT_PLAYER_STATE,
};
