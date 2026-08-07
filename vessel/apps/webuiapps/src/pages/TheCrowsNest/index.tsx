import React, { useEffect } from 'react';
import { Search } from 'lucide-react';
import { reportLifecycle, AppLifecycle } from '@gui/vibe-container';
import styles from './index.module.scss';

const TheCrowsNest: React.FC = () => {
  useEffect(() => {
    reportLifecycle(AppLifecycle.LOADED);
    return () => { reportLifecycle(AppLifecycle.DESTROYED); };
  }, []);

  return (
    <div className={styles.theCrowsNest}>
      <div className={styles.header}>
        <Search size={20} />
        <h1 className={styles.title}>The Crow's Nest</h1>
      </div>
      <div className={styles.body}>
        <div className={styles.placeholder}>
          <Search size={48} />
          <h2>Research Station</h2>
          <p>The highest point on the vessel. Search the web and scan the horizon.</p>
          <p className={styles.phase}>Phase 2 — Live web search integration coming online.</p>
        </div>
      </div>
    </div>
  );
};

export default TheCrowsNest;
