import React from 'react';
import styles from './HabitatPicker.module.css';
import type { Habitat } from '../types';
import SourceBadge from './SourceBadge';

interface HabitatPickerProps {
  habitats: Habitat[];
  selectedHabitat: Habitat;
  onSelectHabitat: (habitat: Habitat) => void;
  isLoading?: boolean;
}

export const HabitatPicker: React.FC<HabitatPickerProps> = ({
  habitats,
  selectedHabitat,
  onSelectHabitat,
  isLoading = false,
}) => {
  return (
    <section className={styles.container} aria-labelledby="habitat-heading">
      <div className={styles.headerRow}>
        <h2 id="habitat-heading" className={styles.heading}>
          1. SELECT CREW HABITAT
        </h2>
        <SourceBadge kind="source" label="[Data from source: Challenge Specs]" size="sm" />
      </div>

      {/* 5 Habitat selection buttons */}
      <div className={styles.buttonGroup} role="group" aria-label="Habitats">
        {habitats.map((habitat) => {
          const isSelected = habitat.name === selectedHabitat.name;
          return (
            <button
              key={habitat.name}
              type="button"
              className={`${styles.habitatBtn} ${isSelected ? styles.activeBtn : ''}`}
              onClick={() => onSelectHabitat(habitat)}
              disabled={isLoading}
              aria-pressed={isSelected}
            >
              <span>{habitat.name}</span>
            </button>
          );
        })}
      </div>

      {/* Shaheer's Ranking Rule Sentence - exact required wording */}
      <div className={styles.rankingSentenceCard} role="note">
        <svg
          className={styles.rankingIcon}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="16" x2="12" y2="12" />
          <line x1="12" y1="8" x2="12.01" y2="8" />
        </svg>
        <span className={styles.rankingSentenceText}>
          Tests score higher when their oxygen and pressure are closer to this habitat.
        </span>
      </div>

      {/* Selected Habitat Atmosphere Telemetry */}
      <div className={styles.telemetryCard}>
        <div className={styles.telemetryLeft}>
          <div className={styles.telemetryHabitatName}>
            HABITAT TARGET: {selectedHabitat.name.toUpperCase()}
          </div>
          <div className={styles.telemetryDesc}>
            {selectedHabitat.description || 'Configured atmospheric parameters'}
          </div>
        </div>

        <div className={styles.telemetryValues}>
          <div className={styles.metricBox}>
            <span className={styles.metricLabel}>Oxygen Conc.</span>
            <span className={styles.metricVal}>{selectedHabitat.oxygen_pct}%</span>
          </div>
          <div className={styles.metricBox}>
            <span className={styles.metricLabel}>Pressure</span>
            <span className={styles.metricVal}>{selectedHabitat.pressure_psi} psi</span>
          </div>
        </div>

        <div className={styles.sourceLine}>
          <SourceBadge kind="source" size="sm" />
          <span>Source: {selectedHabitat.source || 'NASA OCHMO-TB-003 / Challenge brief'}</span>
        </div>
      </div>
    </section>
  );
};

export default HabitatPicker;
