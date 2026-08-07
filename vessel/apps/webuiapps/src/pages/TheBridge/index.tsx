import React, { useEffect } from 'react';
import { Radio, Send } from 'lucide-react';
import { reportLifecycle, AppLifecycle } from '@gui/vibe-container';
import styles from './index.module.scss';

const TheBridge: React.FC = () => {
  useEffect(() => {
    reportLifecycle(AppLifecycle.LOADED);
    return () => { reportLifecycle(AppLifecycle.DESTROYED); };
  }, []);

  return (
    <div className={styles.theBridge}>
      <div className={styles.header}>
        <Radio size={20} />
        <h1 className={styles.title}>The Bridge</h1>
      </div>
      <div className={styles.body}>
        <div className={styles.placeholder}>
          <Radio size={48} />
          <h2>Command Center</h2>
          <p>Dispatch build requests and agent assignments from here.</p>
          <p className={styles.phase}>Phase 2 — The dispatch system will connect to fleet agent APIs.</p>
        </div>
      </div>
    </div>
  );
};

export default TheBridge;
