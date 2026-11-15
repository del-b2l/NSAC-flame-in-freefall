import React from 'react';
import styles from './TestList.module.css';
import type { Habitat, TestRecord } from '../types';
import SourceBadge from './SourceBadge';

interface TestListProps {
  tests: TestRecord[];
  selectedHabitat: Habitat;
  isLoading: boolean;
  error: string | null;
  onRetry?: () => void;
  onExplain: (test: TestRecord) => void;
}

export const TestList: React.FC<TestListProps> = ({
  tests,
  selectedHabitat,
  isLoading,
  error,
  onRetry,
  onExplain,
}) => {
  return (
    <section className={styles.container} aria-labelledby="tests-heading">
      <div className={styles.sectionHeader}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <img
            src="/assets/icons/icon-flask.png"
            alt=""
            className={styles.flaskIcon}
            aria-hidden="true"
          />
          <h2 id="tests-heading" className={styles.heading}>
            2. RANKED MICROGRAVITY INVESTIGATIONS
          </h2>
          <span className={styles.countPill}>
            {tests.length} {tests.length === 1 ? 'Record' : 'Records'}
          </span>
        </div>
        <SourceBadge kind="source" label="[Data from source: NASA Test Matrix]" size="sm" />
      </div>

      {/* Error state */}
      {error && (
        <div className={styles.errorBox} role="alert">
          <div>
            <strong>Telemetry Error:</strong> {error}
          </div>
          {onRetry && (
            <button className={styles.retryBtn} onClick={onRetry}>
              Retry Connection
            </button>
          )}
        </div>
      )}

      {/* Loading state */}
      {isLoading && (
        <div aria-busy="true" aria-label="Loading investigation tests">
          {[1, 2, 3].map((n) => (
            <div key={n} className={styles.skeletonCard}>
              <div className={styles.skeletonTitle} />
              <div className={styles.skeletonLine} style={{ width: '85%' }} />
              <div className={styles.skeletonLine} style={{ width: '60%' }} />
            </div>
          ))}
        </div>
      )}

      {/* Empty state */}
      {!isLoading && tests.length === 0 && !error && (
        <div className={styles.emptyBox}>
          No microgravity test records found for the current query.
        </div>
      )}

      {/* Test records list */}
      {!isLoading &&
        tests.map((test, index) => {
          const rankNumber = index + 1;
          const isTwoSidedPmma = test.material?.toLowerCase().includes('two-sided pmma');

          return (
            <article
              key={test.id}
              className={styles.card}
              aria-label={`Test ${test.id}, ranked #${rankNumber}`}
            >
              <div className={styles.cardTopRow}>
                <div className={styles.titleArea}>
                  <span className={styles.rankBadge}>#{rankNumber}</span>
                  <img
                    src="/assets/icons/icon-flask.png"
                    alt=""
                    className={styles.flaskIcon}
                    aria-hidden="true"
                  />
                  <span className={styles.invName}>{test.investigation}</span>
                  <span className={styles.testIdBadge}>{test.id}</span>
                </div>
                <SourceBadge kind="source" size="sm" />
              </div>

              {/* Sample Material */}
              <div className={styles.materialRow}>
                <span className={styles.materialLabel}>Material Sample:</span>
                <span className={styles.materialValue}>
                  {test.material ? (
                    isTwoSidedPmma ? (
                      <span style={{ color: '#38bdf8', fontWeight: 700 }}>
                        {test.material} (Special Focus)
                      </span>
                    ) : (
                      test.material
                    )
                  ) : (
                    <span className={styles.missingFallback}>Not recorded in matrix</span>
                  )}
                </span>
              </div>

              {/* Condition Telemetry (Oxygen, Pressure, Airflow) with HUD mini-bars */}
              <div className={styles.telemetryGrid}>
                <div className={styles.conditionCol}>
                  <span className={styles.conditionLabel}>
                    <img src="/assets/icons/icon-signal.png" alt="" className={styles.miniIcon} />
                    Oxygen Conc.
                  </span>
                  <span className={styles.conditionValue}>
                    {test.oxygen_pct != null ? (
                      `${test.oxygen_pct}%`
                    ) : (
                      <span className={styles.missingFallback}>Not tested yet</span>
                    )}
                  </span>
                  {test.oxygen_pct != null && (
                    <img src="/assets/ui/bar_blue.png" alt="" className={styles.conditionBarImg} />
                  )}
                </div>

                <div className={styles.conditionCol}>
                  <span className={styles.conditionLabel}>
                    <img src="/assets/icons/icon-fuel.png" alt="" className={styles.miniIcon} />
                    Ambient Pressure
                  </span>
                  <span className={styles.conditionValue}>
                    {test.pressure_psi != null ? (
                      `${test.pressure_psi} psi`
                    ) : (
                      <span className={styles.missingFallback}>Not tested yet</span>
                    )}
                  </span>
                  {test.pressure_psi != null && (
                    <img src="/assets/ui/bar_red.png" alt="" className={styles.conditionBarImg} />
                  )}
                </div>

                <div className={styles.conditionCol}>
                  <span className={styles.conditionLabel}>
                    <img src="/assets/icons/icon-gear.png" alt="" className={styles.miniIcon} />
                    Airflow Speed
                  </span>
                  <span className={styles.conditionValue}>
                    {test.airflow ? (
                      test.airflow
                    ) : (
                      <span className={styles.missingFallback}>Not tested yet</span>
                    )}
                  </span>
                </div>

                <div className={styles.conditionCol}>
                  <span className={styles.conditionLabel}>
                    <img src="/assets/icons/icon-planet.png" alt="" className={styles.miniIcon} />
                    Habitat Match
                  </span>
                  <span
                    className={styles.conditionValue}
                    style={{ fontSize: '12px', color: '#38bdf8' }}
                  >
                    Target: {selectedHabitat.name}
                  </span>
                </div>
              </div>

              {/* Result Summary */}
              <div className={styles.resultBox}>
                <img
                  src="/assets/icons/icon-alert.png"
                  alt=""
                  className={styles.alertIcon}
                  aria-hidden="true"
                />
                <div>
                  <span className={styles.resultLabel}>Test Outcome:</span>
                  <span>
                    {test.result ? (
                      test.result
                    ) : (
                      <span className={styles.missingFallback}>
                        No outcome data recorded in source document
                      </span>
                    )}
                  </span>
                </div>
              </div>

              {/* Bottom Actions Row */}
              <div className={styles.bottomRow}>
                <div className={styles.actionsGroup}>
                  {/* AI Explain Button with GREEN indicator & pixel chip icon */}
                  <button
                    type="button"
                    className={styles.explainBtn}
                    onClick={() => onExplain(test)}
                    title="Generate AI fire dynamics comparison"
                  >
                    <img
                      src="/assets/icons/icon-chip.png"
                      alt=""
                      className={styles.chipIcon}
                      aria-hidden="true"
                    />
                    <span>Explain</span>
                    <SourceBadge kind="ai" label="AI" size="sm" />
                  </button>
                </div>

                {/* NASA Source URL Link */}
                {test.source_url ? (
                  <a
                    href={test.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={styles.sourceLink}
                    title="View NASA primary paper / presentation"
                  >
                    <img
                      src="/assets/icons/icon-check.png"
                      alt=""
                      className={styles.miniIcon}
                      aria-hidden="true"
                    />
                    <span>NASA Source Citation</span>
                    <svg
                      width="12"
                      height="12"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      aria-hidden="true"
                    >
                      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                      <polyline points="15 3 21 3 21 9" />
                      <line x1="10" y1="14" x2="21" y2="3" />
                    </svg>
                  </a>
                ) : (
                  <span className={styles.noSource}>Source URL not catalogued</span>
                )}
              </div>
            </article>
          );
        })}
    </section>
  );
};

export default TestList;
