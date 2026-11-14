import React from 'react';
import styles from './Legend.module.css';
import SourceBadge from './SourceBadge';

export const Legend: React.FC = () => {
  return (
    <aside className={styles.legendContainer} aria-label="Data Provenance Legend">
      <div className={styles.titleGroup}>
        <span>// DATA PROVENANCE KEY:</span>
      </div>
      <div className={styles.itemsGroup}>
        <div className={styles.item}>
          <SourceBadge kind="source" size="sm" />
          <span className={styles.description}>
            Raw NASA microgravity flight data &amp; standards
          </span>
        </div>
        <div className={styles.item}>
          <SourceBadge kind="ai" size="sm" />
          <span className={styles.description}>
            AI-generated contextual explanation
          </span>
        </div>
      </div>
    </aside>
  );
};

export default Legend;
