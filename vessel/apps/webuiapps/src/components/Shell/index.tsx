import React, { useState, useCallback, useEffect, useRef, useSyncExternalStore } from 'react';
import {
  MessageCircle,
  BookOpen,
  Music,
  Compass,
  Gauge,
  Radio,
  ScrollText,
  Search,
  Circle,
  Video,
  VideoOff,
  X,
  type LucideIcon,
} from 'lucide-react';
import ChatPanel from '../ChatPanel';
import AppWindow from '../AppWindow';
import { getWindows, subscribe, openWindow, claimZIndex } from '@/lib/windowManager';
import { getDesktopApps } from '@/lib/appRegistry';
import { reportUserOsAction, onOSEvent } from '@/lib/vibeContainerMock';
import { setReportUserActions } from '@/lib';
import styles from './index.module.scss';

function useWindows() {
  return useSyncExternalStore(subscribe, getWindows);
}

const ICON_MAP: Record<string, LucideIcon> = {
  Music,
  BookOpen,
  Compass,
  Gauge,
  Radio,
  ScrollText,
  Search,
  MessageCircle,
};

const DESKTOP_APPS = getDesktopApps().map((app) => ({
  ...app,
  IconComp: ICON_MAP[app.icon] || Circle,
}));

// Dark maritime wallpaper — deep ocean atmosphere
const VESSEL_WALLPAPER =
  'data:image/svg+xml,' +
  encodeURIComponent(`
    <svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">
      <defs>
        <radialGradient id="depth" cx="50%" cy="40%" r="80%">
          <stop offset="0%" stop-color="#1a2330"/>
          <stop offset="40%" stop-color="#0e1419"/>
          <stop offset="100%" stop-color="#050709"/>
        </radialGradient>
        <pattern id="rivets" x="0" y="0" width="120" height="120" patternUnits="userSpaceOnUse">
          <circle cx="10" cy="10" r="1.5" fill="#b87333" opacity="0.06"/>
          <circle cx="110" cy="10" r="1.5" fill="#b87333" opacity="0.06"/>
          <circle cx="10" cy="110" r="1.5" fill="#b87333" opacity="0.06"/>
          <circle cx="110" cy="110" r="1.5" fill="#b87333" opacity="0.06"/>
        </pattern>
      </defs>
      <rect width="1920" height="1080" fill="url(#depth)"/>
      <rect width="1920" height="1080" fill="url(#rivets)"/>
      <text x="60" y="100" font-family="Georgia, serif" font-size="14" fill="#b87333" opacity="0.3" letter-spacing="4">
        LUCIDDREAMER.AI — THE VESSEL
      </text>
      <text x="60" y="1040" font-family="Georgia, serif" font-size="11" fill="#7a6f5d" opacity="0.4" letter-spacing="2">
        DEPTH: 47M — HEADING: 045° — ALL HANDS AT STATIONS
      </text>
    </svg>
  `);

const Shell: React.FC = () => {
  const [chatOpen, setChatOpen] = useState(true);
  const [reportEnabled, setReportEnabled] = useState(true);
  const [wallpaper, setWallpaper] = useState(VESSEL_WALLPAPER);
  const [chatZIndex, setChatZIndex] = useState(() => claimZIndex());
  const windows = useWindows();

  const handleToggleReport = useCallback(() => {
    setReportEnabled((prev) => {
      const next = !prev;
      setReportUserActions(next);
      return next;
    });
  }, []);

  useEffect(() => {
    return onOSEvent((event) => {
      if (event.type === 'SET_WALLPAPER' && typeof event.wallpaper_url === 'string') {
        setWallpaper(event.wallpaper_url);
      }
    });
  }, []);

  return (
    <div
      className={styles.shell}
      data-testid="shell"
      style={{
        backgroundImage: `url(${wallpaper})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
    >
      {/* Desktop with app icons */}
      <div className={styles.desktop} data-testid="desktop">
        <div className={styles.iconGrid}>
          {DESKTOP_APPS.map((app) => (
            <button
              key={app.appId}
              className={styles.appIcon}
              data-testid={`app-icon-${app.appId}`}
              onDoubleClick={() => {
                openWindow(app.appId);
                reportUserOsAction('OPEN_APP', { app_id: String(app.appId) });
              }}
              title={`Double-click to open ${app.displayName}`}
            >
              <div
                className={styles.iconCircle}
                style={{ background: `${app.color}22`, borderColor: `${app.color}44` }}
              >
                <app.IconComp size={24} color={app.color} />
              </div>
              <span className={styles.iconLabel}>{app.displayName}</span>
            </button>
          ))}
        </div>
      </div>

      {/* App windows */}
      {windows.map((win) => (
        <AppWindow key={win.appId} win={win} />
      ))}

      {/* Chat Panel — Hermes */}
      <ChatPanel
        onClose={() => setChatOpen(false)}
        visible={chatOpen}
        zIndex={chatZIndex}
        onFocus={() => setChatZIndex(claimZIndex())}
      />

      <div className={`${styles.bottomBar} ${chatOpen ? styles.chatOpen : ''}`}>
        <button
          className={`${styles.barBtn} ${reportEnabled ? styles.reportOn : styles.reportOff}`}
          onClick={handleToggleReport}
          title={reportEnabled ? 'Action reporting: ON' : 'Action reporting: OFF'}
          data-testid="report-toggle"
        >
          <Radio size={16} />
        </button>

        <button
          className={`${styles.barBtn} ${styles.chatBtn}`}
          onClick={() => setChatOpen(!chatOpen)}
          title="Toggle Hermes"
          data-testid="chat-toggle"
        >
          <MessageCircle size={18} />
        </button>
      </div>
    </div>
  );
};

export default Shell;
