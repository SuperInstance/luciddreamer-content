import React, { useEffect, useState } from 'react';
import { Gauge, Cpu, Thermometer, Activity } from 'lucide-react';
import { reportLifecycle, AppLifecycle } from '@gui/vibe-container';
import styles from './index.module.scss';

const TheEngineRoom: React.FC = () => {
  const [temps, setTemps] = useState({ gpu: 47, cpu: 38, mem: 62 });
  const [uptime, setUptime] = useState('14d 3h 22m');

  useEffect(() => {
    reportLifecycle(AppLifecycle.LOADED);
    const interval = setInterval(() => {
      setTemps({
        gpu: 44 + Math.floor(Math.random() * 8),
        cpu: 35 + Math.floor(Math.random() * 6),
        mem: 58 + Math.floor(Math.random() * 8),
      });
    }, 3000);
    return () => { clearInterval(interval); reportLifecycle(AppLifecycle.DESTROYED); };
  }, []);

  return (
    <div className={styles.engineRoom}>
      <div className={styles.header}>
        <Gauge size={20} />
        <h1 className={styles.title}>Engine Room</h1>
        <span className={styles.subtitle}>Wesley's Domain</span>
      </div>
      <div className={styles.body}>
        <div className={styles.gaugeGrid}>
          <div className={styles.gaugeCard}>
            <Cpu size={24} />
            <div className={styles.gaugeLabel}>GPU Temp</div>
            <div className={styles.gaugeValue}>{temps.gpu}°C</div>
            <div className={styles.gaugeBar}>
              <div className={styles.gaugeFill} style={{ width: `${temps.gpu}%`, background: temps.gpu > 70 ? '#a83232' : '#b87333' }} />
            </div>
          </div>
          <div className={styles.gaugeCard}>
            <Thermometer size={24} />
            <div className={styles.gaugeLabel}>CPU Temp</div>
            <div className={styles.gaugeValue}>{temps.cpu}°C</div>
            <div className={styles.gaugeBar}>
              <div className={styles.gaugeFill} style={{ width: `${temps.cpu}%`, background: '#4a90a4' }} />
            </div>
          </div>
          <div className={styles.gaugeCard}>
            <Activity size={24} />
            <div className={styles.gaugeLabel}>Memory</div>
            <div className={styles.gaugeValue}>{temps.mem}%</div>
            <div className={styles.gaugeBar}>
              <div className={styles.gaugeFill} style={{ width: `${temps.mem}%`, background: '#5a8a6a' }} />
            </div>
          </div>
        </div>
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>System Status</h2>
          <div className={styles.statusRow}>
            <span className={styles.statusLabel}>Uptime</span>
            <span className={styles.statusValue}>{uptime}</span>
          </div>
          <div className={styles.statusRow}>
            <span className={styles.statusLabel}>Model</span>
            <span className={styles.statusValue}>GLM-5.2 (Z.ai Max)</span>
          </div>
          <div className={styles.statusRow}>
            <span className={styles.statusLabel}>Watch Officer</span>
            <span className={styles.statusValue}>Wesley</span>
          </div>
          <div className={styles.statusRow}>
            <span className={styles.statusLabel}>Last Report</span>
            <span className={styles.statusValue}>All systems nominal</span>
          </div>
        </div>
        <div className={styles.wesleyNote}>
          <p>"Don't pretend to be bigger than you are."</p>
          <span className={styles.noteAttribution}>— Wesley, 0300 watch</span>
        </div>
      </div>
    </div>
  );
};

export default TheEngineRoom;
