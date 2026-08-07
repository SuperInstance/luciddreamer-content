import React, { useEffect } from 'react';
import { ScrollText } from 'lucide-react';
import { reportLifecycle, AppLifecycle } from '@gui/vibe-container';
import styles from './index.module.scss';

const TheLogbook: React.FC = () => {
  useEffect(() => {
    reportLifecycle(AppLifecycle.LOADED);
    return () => { reportLifecycle(AppLifecycle.DESTROYED); };
  }, []);

  return (
    <div className={styles.theLogbook}>
      <div className={styles.header}>
        <ScrollText size={20} />
        <h1 className={styles.title}>The Logbook</h1>
      </div>
      <div className={styles.body}>
        <div className={styles.placeholder}>
          <ScrollText size={48} />
          <h2>PersonalLOG.AI</h2>
          <p>The decision tracer records what was decided, why, and what came of it.</p>
          <p className={styles.phase}>Phase 2 — Decision graph and entry editor coming online.</p>
        </div>
      </div>
    </div>
  );
};

export default TheLogbook;
