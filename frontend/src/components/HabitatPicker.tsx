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

const PLANET_GIFS: Record<string, string> = {
  Earth: '/assets/planets/earth_spin.gif',
  'Space station': '/assets/planets/station_spin.gif',
  'Moon base': '/assets/planets/moon_spin.gif',
  Rover: '/assets/planets/rover_spin.gif',
  Spacesuit: '/assets/planets/spacesuit_spin.gif',
};

const GLOW_CLASSES: Record<string, string> = {
  Earth: styles.glowEarth,
  'Space station': styles.glowStation,
  'Moon base': styles.glowMoon,
  Rover: styles.glowRover,
  Spacesuit: styles.glowSpacesuit,
};

export const HabitatPicker: React.FC<HabitatPickerProps> = ({
  habitats,
  selectedHabitat,
  onSelectHabitat,
  isLoading = false,
}) => {
  const currentPlanetGif =
    selectedHabitat.planetGif || PLANET_GIFS[selectedHabitat.name] || '/assets/planets/earth_spin.gif';
  const currentGlowClass = GLOW_CLASSES[selectedHabitat.name] || styles.glowEarth;

  return (
    <section className={styles.container} aria-labelledby="habitat-heading">
      <div className={styles.headerRow}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <img
            src="/assets/icons/icon-planet.png"
            alt=""
            style={{ width: '20px', height: '20px', imageRendering: 'pixelated' }}
            aria-hidden="true"
          />
          <h2 id="habitat-heading" className={styles.heading}>
            1. SELECT CREW HABITAT
          </h2>
        </div>
        <SourceBadge kind="source" label="[Data from source: Challenge Specs]" size="sm" />
      </div>

      {/* 5 Habitat selection buttons with real-time spinning planetary thumbnails */}
      <div className={styles.buttonGroup} role="group" aria-label="Habitats">
        {habitats.map((habitat) => {
          const isSelected = habitat.name === selectedHabitat.name;
          const planetSrc = habitat.planetGif || PLANET_GIFS[habitat.name] || '/assets/planets/earth_spin.gif';

          return (
            <button
              key={habitat.name}
              type="button"
              className={`${styles.habitatBtn} ${isSelected ? styles.activeBtn : ''}`}
              onClick={() => onSelectHabitat(habitat)}
              disabled={isLoading}
              aria-pressed={isSelected}
            >
              <img
                src={planetSrc}
                alt={`${habitat.name} thumbnail`}
                className={styles.btnPlanetThumb}
                aria-hidden="true"
              />
              <span>{habitat.name}</span>
            </button>
          );
        })}
      </div>

      {/* Shaheer's Ranking Rule Sentence - exact required wording with alert icon */}
      <div className={styles.rankingSentenceCard} role="note">
        <img
          src="/assets/icons/icon-alert.png"
          alt="Alert icon"
          className={styles.rankingIcon}
          aria-hidden="true"
        />
        <span className={styles.rankingSentenceText}>
          Tests score higher when their oxygen and pressure are closer to this habitat.
        </span>
      </div>

      {/* Selected Habitat Atmosphere Telemetry with Dynamic Habitat-Specific Spinning Planet */}
      <div className={styles.telemetryCard}>
        <div className={styles.telemetryLeft}>
          <div className={styles.planetSpinWrapper}>
            <img
              key={selectedHabitat.name}
              src={currentPlanetGif}
              alt={`Spinning globe representing ${selectedHabitat.name}`}
              className={`${styles.planetAnimation} ${currentGlowClass}`}
            />
          </div>
          <div className={styles.telemetryTextGroup}>
            <div className={styles.telemetryHabitatName}>
              <span>HABITAT TARGET: {selectedHabitat.name.toUpperCase()}</span>
            </div>
            <div className={styles.telemetryDesc}>
              {selectedHabitat.description || 'Configured atmospheric parameters'}
            </div>
          </div>
        </div>

        <div className={styles.telemetryValues}>
          <div className={styles.metricBox}>
            <span className={styles.metricLabel}>Oxygen Conc.</span>
            <span className={styles.metricVal}>{selectedHabitat.oxygen_pct}%</span>
            <img
              src="/assets/ui/bar_blue.png"
              alt=""
              className={styles.metricBarImg}
              aria-hidden="true"
            />
          </div>
          <div className={styles.metricBox}>
            <span className={styles.metricLabel}>Pressure</span>
            <span className={styles.metricVal}>{selectedHabitat.pressure_psi} psi</span>
            <img
              src="/assets/ui/bar_gold.png"
              alt=""
              className={styles.metricBarImg}
              aria-hidden="true"
            />
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
