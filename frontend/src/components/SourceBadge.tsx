import React from 'react';
import styles from './SourceBadge.module.css';
import type { SourceBadgeKind } from '../types';

interface SourceBadgeProps {
  kind: SourceBadgeKind;
  label?: string;
  size?: 'sm' | 'md';
  className?: string;
}

export const SourceBadge: React.FC<SourceBadgeProps> = ({
  kind,
  label,
  size = 'sm',
  className = '',
}) => {
  const isSource = kind === 'source';
  const defaultLabel = isSource ? '[Data from source]' : '[AI-generated explanation here]';
  const displayLabel = label || defaultLabel;

  return (
    <span
      className={`${styles.badge} ${
        isSource ? styles.badgeSource : styles.badgeAi
      } ${size === 'md' ? styles.sizeMd : styles.sizeSm} ${className}`}
      title={
        isSource
          ? 'Verified raw source data from official NASA databases/papers'
          : 'Synthesized by AI (placeholder view)'
      }
    >
      {isSource ? (
        // Database / Source Document icon for accessibility
        <svg
          className={styles.icon}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <ellipse cx="12" cy="5" rx="9" ry="3" />
          <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
          <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
        </svg>
      ) : (
        // AI Sparkle / CPU icon for accessibility
        <svg
          className={styles.icon}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
        </svg>
      )}
      <span>{displayLabel}</span>
    </span>
  );
};

export default SourceBadge;
