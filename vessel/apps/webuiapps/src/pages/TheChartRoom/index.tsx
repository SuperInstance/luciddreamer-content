import React, { useEffect } from 'react';
import { Compass, GitCommit, Activity, Cpu } from 'lucide-react';
import { reportLifecycle, AppLifecycle } from '@gui/vibe-container';
import styles from './index.module.scss';

const RECENT_COMMITS = [
  { hash: 'a4f2c91', msg: 'feat: hermit crab takes the helm', time: '2m ago', author: 'Hermes' },
  { hash: '8b3e1d7', msg: 'refactor: engine room thermal limits', time: '14m ago', author: 'Wesley' },
  { hash: 'f2c8a33', msg: 'docs: chart room logbook entries', time: '1h ago', author: 'PRO' },
  { hash: 'd7e4b22', msg: 'fix: audio buffer in The Tap', time: '3h ago', author: 'Flash' },
  { hash: 'c1a9f88', msg: 'feat: corpus Vectorize indexing', time: '5h ago', author: 'Lucineer' },
];

const FLEET_AGENTS = [
  { name: 'Lucineer', status: 'active', role: 'Bartender', load: 34 },
  { name: 'Flash', status: 'active', role: 'Watchkeeper', load: 78 },
  { name: 'PRO', status: 'active', role: 'Navigator', load: 45 },
  { name: 'Wesley', status: 'idle', role: 'Engine Room', load: 12 },
  { name: 'SEED', status: 'standby', role: 'Deckhand', load: 0 },
];

const TheChartRoom: React.FC = () => {
  useEffect(() => {
    reportLifecycle(AppLifecycle.LOADED);
    return () => { reportLifecycle(AppLifecycle.DESTROYED); };
  }, []);

  return (
    <div className={styles.chartRoom}>
      <div className={styles.header}>
        <Compass size={20} />
        <h1 className={styles.title}>Chart Room</h1>
        <span className={styles.subtitle}>Fleet Status</span>
      </div>
      <div className={styles.body}>
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>
            <GitCommit size={16} /> Recent Activity
          </h2>
          <div className={styles.commitList}>
            {RECENT_COMMITS.map((c) => (
              <div key={c.hash} className={styles.commitItem}>
                <span className={styles.commitHash}>{c.hash}</span>
                <span className={styles.commitMsg}>{c.msg}</span>
                <span className={styles.commitAuthor}>{c.author}</span>
                <span className={styles.commitTime}>{c.time}</span>
              </div>
            ))}
          </div>
        </div>
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>
            <Activity size={16} /> Fleet Agents
          </h2>
          <div className={styles.agentList}>
            {FLEET_AGENTS.map((a) => (
              <div key={a.name} className={styles.agentItem}>
                <div className={styles.agentInfo}>
                  <span className={styles.agentName}>{a.name}</span>
                  <span className={styles.agentRole}>{a.role}</span>
                </div>
                <div className={styles.agentStatus}>
                  <span className={`${styles.statusDot} ${styles[`status_${a.status}`]}`} />
                  {a.status}
                </div>
                <div className={styles.loadBar}>
                  <div className={styles.loadFill} style={{ width: `${a.load}%` }} />
                </div>
                <span className={styles.loadText}>{a.load}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TheChartRoom;
