import React, { useEffect, useState, useCallback, useRef } from 'react';
import { initVibeApp, AppLifecycle } from '@gui/vibe-container';
import {
  useAgentActionListener,
  reportAction,
  reportLifecycle,
  fetchVibeInfo,
  createAppFileApi,
  batchConcurrent,
  type CharacterAppAction,
  ActionTriggerBy,
} from '@/lib';
import {
  Play, Pause, SkipBack, SkipForward, Volume2, VolumeX, Repeat, Shuffle,
  Music, ListMusic, Anchor,
} from 'lucide-react';
import type { Episode, Show, PlayerState } from './types';
import {
  APP_ID, APP_NAME, EPISODES_DIR, SHOWS_DIR, STATE_FILE,
  ActionTypes, DEFAULT_PLAYER_STATE, DEFAULT_APP_STATE,
} from './actions/constants';
import { SEED_EPISODES, SEED_SHOWS } from './mock/seedData';
import styles from './index.module.scss';

const tapFileApi = createAppFileApi(APP_NAME);

const formatDuration = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

// ============ Sidebar ============
interface SidebarProps {
  shows: Show[];
  currentShowId: string | null;
  onSelectShow: (showId: string | null) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ shows, currentShowId, onSelectShow }) => (
  <aside className={styles.sidebar}>
    <div className={styles.sidebarHeader}>
      <Anchor size={20} />
      <span className={styles.sidebarTitle}>The Tap</span>
    </div>
    <div className={styles.sidebarSection}>
      <div className={styles.sectionTitle}>All Episodes</div>
      <button
        className={`${styles.showItem} ${currentShowId === null ? styles.active : ''}`}
        onClick={() => onSelectShow(null)}
      >
        <ListMusic size={16} />
        Every story
      </button>
    </div>
    <div className={styles.sidebarSection}>
      <div className={styles.sectionTitle}>Shows</div>
      {shows.map((show) => (
        <button
          key={show.id}
          className={`${styles.showItem} ${currentShowId === show.id ? styles.active : ''}`}
          onClick={() => onSelectShow(show.id)}
        >
          <Music size={16} />
          {show.name}
        </button>
      ))}
    </div>
  </aside>
);

// ============ Episode List ============
interface EpisodeListProps {
  episodes: Episode[];
  currentEpisodeId: string | null;
  isPlaying: boolean;
  showName: string;
  onPlayEpisode: (id: string) => void;
  onPlayAll: () => void;
}

const EpisodeList: React.FC<EpisodeListProps> = ({
  episodes, currentEpisodeId, isPlaying, showName, onPlayEpisode, onPlayAll,
}) => (
  <main className={styles.content}>
    <div className={styles.contentHeader}>
      <div>
        <h1 className={styles.showTitle}>{showName}</h1>
        <div className={styles.showMeta}>
          {episodes.length} {episodes.length === 1 ? 'episode' : 'episodes'}
        </div>
      </div>
      <button className={styles.playAllBtn} onClick={onPlayAll} disabled={episodes.length === 0}>
        <Play size={22} fill="currentColor" />
      </button>
    </div>
    <div className={styles.episodeList}>
      {episodes.length === 0 ? (
        <div className={styles.emptyState}>
          <Music size={48} />
          <p>No episodes available</p>
        </div>
      ) : (
        episodes.map((ep, i) => {
          const isCurrent = ep.id === currentEpisodeId;
          return (
            <div
              key={ep.id}
              className={`${styles.episodeItem} ${isCurrent ? styles.playing : ''}`}
              onClick={() => onPlayEpisode(ep.id)}
            >
              <div className={styles.episodeIndex}>
                <span className={styles.episodeNumber}>{ep.episodeNumber || i + 1}</span>
                <span className={styles.episodePlayIcon}>
                  {isCurrent && isPlaying ? <Volume2 size={16} /> : <Play size={16} fill="currentColor" />}
                </span>
              </div>
              <div className={styles.episodeInfo}>
                <div className={styles.episodeTitle}>{ep.title}</div>
                <div className={styles.episodeShow}>{ep.show}</div>
                <div className={styles.episodeDesc}>{ep.description}</div>
              </div>
              <div className={styles.episodeDuration}>{formatDuration(ep.duration)}</div>
            </div>
          );
        })
      )}
    </div>
  </main>
);

// ============ Player Bar ============
interface PlayerBarProps {
  currentEpisode: Episode | null;
  playerState: PlayerState;
  onPlayPause: () => void;
  onPrev: () => void;
  onNext: () => void;
  onSeek: (t: number) => void;
  onVolumeChange: (v: number) => void;
  onToggleRepeat: () => void;
  onToggleShuffle: () => void;
}

const PlayerBar: React.FC<PlayerBarProps> = ({
  currentEpisode, playerState, onPlayPause, onPrev, onNext, onSeek, onVolumeChange,
  onToggleRepeat, onToggleShuffle,
}) => {
  const { isPlaying, volume, currentTime, playMode } = playerState;
  const duration = currentEpisode?.duration || 0;
  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    onSeek(((e.clientX - rect.left) / rect.width) * duration);
  };

  const handleVolumeClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    onVolumeChange(Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width)));
  };

  return (
    <div className={styles.playerBar}>
      <div className={styles.nowPlaying}>
        {currentEpisode ? (
          <>
            <div className={styles.nowPlayingCover}>
              <Music size={22} />
            </div>
            <div className={styles.nowPlayingInfo}>
              <div className={styles.nowPlayingTitle}>{currentEpisode.title}</div>
              <div className={styles.nowPlayingShow}>{currentEpisode.show}</div>
            </div>
          </>
        ) : null}
      </div>
      <div className={styles.playerControls}>
        <div className={styles.controlButtons}>
          <button className={`${styles.controlBtn} ${playMode === 'shuffle' ? styles.active : ''}`} onClick={onToggleShuffle}>
            <Shuffle size={16} />
          </button>
          <button className={styles.controlBtn} onClick={onPrev} disabled={!currentEpisode}>
            <SkipBack size={18} fill="currentColor" />
          </button>
          <button className={`${styles.controlBtn} ${styles.playPauseBtn}`} onClick={onPlayPause} disabled={!currentEpisode}>
            {isPlaying ? <Pause size={18} fill="currentColor" /> : <Play size={18} fill="currentColor" />}
          </button>
          <button className={styles.controlBtn} onClick={() => onNext()} disabled={!currentEpisode}>
            <SkipForward size={18} fill="currentColor" />
          </button>
          <button className={`${styles.controlBtn} ${playMode === 'repeat-one' ? styles.active : ''}`} onClick={onToggleRepeat}>
            <Repeat size={16} />
          </button>
        </div>
        <div className={styles.progressBar}>
          <span className={styles.progressTime}>{formatDuration(currentTime)}</span>
          <div className={styles.progressSlider} onClick={handleProgressClick}>
            <div className={styles.progressFill} style={{ width: `${progress}%` }}>
              <div className={styles.progressThumb} />
            </div>
          </div>
          <span className={styles.progressTime}>{formatDuration(duration)}</span>
        </div>
      </div>
      <div className={styles.volumeControl}>
        <button className={styles.volumeBtn} onClick={() => onVolumeChange(volume > 0 ? 0 : 0.8)}>
          {volume === 0 ? <VolumeX size={18} /> : <Volume2 size={18} />}
        </button>
        <div className={styles.volumeSlider} onClick={handleVolumeClick}>
          <div className={styles.volumeFill} style={{ width: `${volume * 100}%` }} />
        </div>
      </div>
    </div>
  );
};

// ============ Main Component ============
const TheTap: React.FC = () => {
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [shows, setShows] = useState<Show[]>([]);
  const [currentShowId, setCurrentShowId] = useState<string | null>(null);
  const [playerState, setPlayerState] = useState<PlayerState>(DEFAULT_PLAYER_STATE);
  const [isLoading, setIsLoading] = useState(true);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const playQueueRef = useRef<string[]>([]);
  const handleNextRef = useRef<(_auto?: boolean) => void>(() => {});

  const getCurrentEpisodes = useCallback((): Episode[] => {
    if (currentShowId === null) return episodes;
    return episodes.filter((e) => e.showId === currentShowId);
  }, [episodes, currentShowId]);

  const currentEpisode = episodes.find((e) => e.id === playerState.currentEpisodeId) || null;
  const currentShowName = currentShowId
    ? shows.find((s) => s.id === currentShowId)?.name || 'The Tap'
    : 'All Episodes';

  useEffect(() => {
    audioRef.current = new Audio();
    audioRef.current.volume = playerState.volume;
    const audio = audioRef.current;

    const handleTimeUpdate = () =>
      setPlayerState((prev) => ({ ...prev, currentTime: audio.currentTime }));
    const handleEnded = () => handleNextRef.current(true);

    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('ended', handleEnded);
    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('ended', handleEnded);
      audio.pause();
      audio.src = '';
    };
  }, []);

  // Seed data on mount
  useEffect(() => {
    const init = async () => {
      try {
        reportLifecycle(AppLifecycle.LOADING);
        const manager = await initVibeApp({ id: APP_ID, url: window.location.href, type: 'page', name: 'TheTap' });
        manager.handshake({ id: APP_ID, url: window.location.href, type: 'page', name: 'TheTap' });
        reportLifecycle(AppLifecycle.DOM_READY);
        await fetchVibeInfo();

        // Try loading from storage, fall back to seed
        try {
          const epFiles = await tapFileApi.listFiles(EPISODES_DIR);
          const loaded: Episode[] = [];
          const jsonFiles = epFiles.filter((f) => f.type === 'file' && f.name.endsWith('.json'));
          if (jsonFiles.length > 0) {
            await batchConcurrent(jsonFiles, (f) => tapFileApi.readFile(f.path), {
              onBatch: (results) => {
                results.forEach((r) => {
                  if (r.status === 'fulfilled' && r.value.content) {
                    try {
                      loaded.push(JSON.parse(r.value.content as string));
                    } catch {}
                  }
                });
                if (loaded.length > 0) setEpisodes([...loaded]);
              },
            });
          }
        } catch {}

        if (episodes.length === 0 || (await tapFileApi.listFiles(EPISODES_DIR)).length === 0) {
          setEpisodes(SEED_EPISODES);
          setShows(SEED_SHOWS);
          await batchConcurrent(SEED_EPISODES, (ep) =>
            tapFileApi.writeFile(`${EPISODES_DIR}/${ep.id}.json`, ep),
          );
          await batchConcurrent(SEED_SHOWS, (s) =>
            tapFileApi.writeFile(`${SHOWS_DIR}/${s.id}.json`, s),
          );
        } else {
          // Load shows
          try {
            const showFiles = await tapFileApi.listFiles(SHOWS_DIR);
            const loadedShows: Show[] = [];
            const showJson = showFiles.filter((f) => f.type === 'file' && f.name.endsWith('.json'));
            await batchConcurrent(showJson, (f) => tapFileApi.readFile(f.path), {
              onBatch: (results) => {
                results.forEach((r) => {
                  if (r.status === 'fulfilled' && r.value.content) {
                    try { loadedShows.push(JSON.parse(r.value.content as string)); } catch {}
                  }
                });
              },
            });
            if (loadedShows.length > 0) setShows(loadedShows);
            else setShows(SEED_SHOWS);
          } catch {
            setShows(SEED_SHOWS);
          }
        }

        setIsLoading(false);
        reportLifecycle(AppLifecycle.LOADED);
        manager.ready();
      } catch (error) {
        console.error('[TheTap] Init error:', error);
        setEpisodes(SEED_EPISODES);
        setShows(SEED_SHOWS);
        setIsLoading(false);
        reportLifecycle(AppLifecycle.ERROR, String(error));
      }
    };
    init();
    return () => {
      reportLifecycle(AppLifecycle.UNLOADING);
      reportLifecycle(AppLifecycle.DESTROYED);
    };
  }, []);

  // Play episode
  const handlePlayEpisode = useCallback((episodeId: string, auto = false) => {
    const ep = episodes.find((e) => e.id === episodeId);
    if (!ep || !audioRef.current) return;
    audioRef.current.src = ep.audioUrl;
    audioRef.current.play().catch(console.error);
    setPlayerState((prev) => ({ ...prev, currentEpisodeId: episodeId, isPlaying: true, currentTime: 0 }));
    playQueueRef.current = getCurrentEpisodes().map((e) => e.id);
    reportAction(APP_ID, 'PLAY_EPISODE', { episodeId }, auto ? ActionTriggerBy.System : ActionTriggerBy.User);
  }, [episodes, getCurrentEpisodes]);

  const handlePlayPause = useCallback(() => {
    if (!audioRef.current) return;
    if (playerState.isPlaying) {
      audioRef.current.pause();
      setPlayerState((prev) => ({ ...prev, isPlaying: false }));
      reportAction(APP_ID, 'PAUSE', {});
    } else {
      audioRef.current.play().catch(console.error);
      setPlayerState((prev) => ({ ...prev, isPlaying: true }));
      reportAction(APP_ID, 'RESUME', {});
    }
  }, [playerState.isPlaying]);

  const handlePrev = useCallback(() => {
    const queue = playQueueRef.current;
    const idx = queue.indexOf(playerState.currentEpisodeId || '');
    if (idx > 0) handlePlayEpisode(queue[idx - 1]);
    else if (queue.length > 0) handlePlayEpisode(queue[queue.length - 1]);
  }, [playerState.currentEpisodeId, handlePlayEpisode]);

  const handleNext = useCallback((auto = false) => {
    const queue = playQueueRef.current;
    const idx = queue.indexOf(playerState.currentEpisodeId || '');
    if (auto && playerState.playMode === 'repeat-one' && playerState.currentEpisodeId) {
      handlePlayEpisode(playerState.currentEpisodeId, true);
      return;
    }
    if (playerState.playMode === 'shuffle') {
      handlePlayEpisode(queue[Math.floor(Math.random() * queue.length)], auto);
    } else if (idx < queue.length - 1) {
      handlePlayEpisode(queue[idx + 1], auto);
    } else if (queue.length > 0) {
      handlePlayEpisode(queue[0], auto);
    } else {
      setPlayerState((prev) => ({ ...prev, isPlaying: false }));
    }
  }, [playerState.currentEpisodeId, playerState.playMode, handlePlayEpisode]);

  useEffect(() => { handleNextRef.current = handleNext; }, [handleNext]);

  const handleSeek = useCallback((time: number) => {
    if (!audioRef.current) return;
    audioRef.current.currentTime = time;
    setPlayerState((prev) => ({ ...prev, currentTime: time }));
  }, []);

  const handleVolumeChange = useCallback((volume: number) => {
    if (!audioRef.current) return;
    audioRef.current.volume = volume;
    setPlayerState((prev) => ({ ...prev, volume }));
  }, []);

  const handleToggleRepeat = useCallback(() => {
    setPlayerState((prev) => ({
      ...prev,
      playMode: prev.playMode === 'repeat-one' ? 'sequential' : 'repeat-one',
    }));
  }, []);

  const handleToggleShuffle = useCallback(() => {
    setPlayerState((prev) => ({
      ...prev,
      playMode: prev.playMode === 'shuffle' ? 'sequential' : 'shuffle',
    }));
  }, []);

  const handleSelectShow = useCallback((showId: string | null) => {
    setCurrentShowId(showId);
  }, []);

  const handlePlayAll = useCallback(() => {
    const eps = getCurrentEpisodes();
    if (eps.length > 0) handlePlayEpisode(eps[0].id);
  }, [getCurrentEpisodes, handlePlayEpisode]);

  // Agent action listener
  const handleAgentAction = useCallback(async (action: CharacterAppAction): Promise<string> => {
    switch (action.action_type) {
      case ActionTypes.PLAY_EPISODE: {
        const epId = action.params?.episodeId;
        if (!epId) return 'error: missing episodeId';
        const ep = episodes.find((e) => e.id === epId);
        if (!ep) return 'error: episode not found';
        handlePlayEpisode(epId);
        return 'success';
      }
      case ActionTypes.PAUSE:
        if (playerState.isPlaying) handlePlayPause();
        return 'success';
      case ActionTypes.RESUME:
        if (!playerState.isPlaying) handlePlayPause();
        return 'success';
      case ActionTypes.NEXT_EPISODE:
        handleNext();
        return 'success';
      case ActionTypes.PREV_EPISODE:
        handlePrev();
        return 'success';
      case ActionTypes.SET_VOLUME: {
        handleVolumeChange(parseFloat(action.params?.volume || '0.8'));
        return 'success';
      }
      case ActionTypes.SEEK: {
        handleSeek(parseFloat(action.params?.time || '0'));
        return 'success';
      }
      case ActionTypes.SELECT_SHOW: {
        const showId = action.params?.showId || null;
        setCurrentShowId(showId);
        return 'success';
      }
      case ActionTypes.SET_PLAY_MODE: {
        const mode = action.params?.mode as PlayerState['playMode'];
        if (!mode) return 'error: missing mode';
        setPlayerState((prev) => ({ ...prev, playMode: mode }));
        return 'success';
      }
      case ActionTypes.REFRESH_EPISODES: {
        // Reload from storage
        try {
          const epFiles = await tapFileApi.listFiles(EPISODES_DIR);
          const loaded: Episode[] = [];
          const jsonFiles = epFiles.filter((f) => f.type === 'file' && f.name.endsWith('.json'));
          for (const f of jsonFiles) {
            const result = await tapFileApi.readFile(f.path);
            if (result.content) {
              try { loaded.push(JSON.parse(result.content as string)); } catch {}
            }
          }
          if (loaded.length > 0) setEpisodes(loaded);
          return 'success';
        } catch {
          return 'error: failed to refresh';
        }
      }
      case ActionTypes.SYNC_STATE: {
        try {
          const stateResult = await tapFileApi.readFile(STATE_FILE);
          if (stateResult.content) {
            const saved = JSON.parse(stateResult.content as string);
            if (saved.activeShowId !== undefined) setCurrentShowId(saved.activeShowId);
            if (saved.player) {
              setPlayerState((prev) => ({
                ...prev,
                ...(saved.player.volume !== undefined && { volume: saved.player.volume }),
                ...(saved.player.playMode !== undefined && { playMode: saved.player.playMode }),
              }));
              if (saved.player.volume !== undefined && audioRef.current)
                audioRef.current.volume = saved.player.volume;
            }
          }
          return 'success';
        } catch {
          return 'error: failed to sync state';
        }
      }
      default:
        return `error: unknown action_type ${action.action_type}`;
    }
  }, [episodes, playerState.isPlaying, playerState.playMode, handlePlayEpisode, handlePlayPause, handleNext, handlePrev, handleVolumeChange, handleSeek]);

  useAgentActionListener(APP_ID, handleAgentAction);

  if (isLoading) {
    return (
      <div className={styles.theTap}>
        <div className={styles.loading}>
          <div className={styles.spinner} />
        </div>
      </div>
    );
  }

  const displayEpisodes = getCurrentEpisodes();

  return (
    <div className={styles.theTap}>
      <div className={styles.mainContent}>
        <Sidebar shows={shows} currentShowId={currentShowId} onSelectShow={handleSelectShow} />
        <EpisodeList
          episodes={displayEpisodes}
          currentEpisodeId={playerState.currentEpisodeId}
          isPlaying={playerState.isPlaying}
          showName={currentShowName}
          onPlayEpisode={handlePlayEpisode}
          onPlayAll={handlePlayAll}
        />
      </div>
      <PlayerBar
        currentEpisode={currentEpisode}
        playerState={playerState}
        onPlayPause={handlePlayPause}
        onPrev={handlePrev}
        onNext={handleNext}
        onSeek={handleSeek}
        onVolumeChange={handleVolumeChange}
        onToggleRepeat={handleToggleRepeat}
        onToggleShuffle={handleToggleShuffle}
      />
    </div>
  );
};

export default TheTap;
