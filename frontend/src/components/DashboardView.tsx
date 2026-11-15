import React, { useLayoutEffect, useRef, useState } from 'react';
import styles from './DashboardView.module.css';
import type { Habitat, Investigation, TestRecord } from '../types';
import HabitatPicker from './HabitatPicker';
import TestList from './TestList';
import Legend from './Legend';
import ExplainModal from './ExplainModal';
import SourceBadge from './SourceBadge';
import { useDashboardData } from '../api/useDashboardData';
import { AskPanel, BriefPanel, EarthUsePanel, HardwarePanel } from './ExtraPanels';

interface DashboardViewProps {
  habitats: Habitat[];
  selectedHabitat: Habitat;
  onSelectHabitat: (habitat: Habitat) => void;
  tests: TestRecord[];
  isLoading: boolean;
  error: string | null;
  onRetry: () => void;
}

const CATEGORY_ORDER = ['prevent', 'detect', 'put out', 'related'];

const CATEGORY_LABELS: Record<string, string> = {
  prevent: 'Prevent',
  detect: 'Detect',
  'put out': 'Put out',
  related: 'Related',
};

function categoryLabel(category: string | null): string {
  if (!category || !category.trim()) {
    return 'Uncategorised';
  }
  return CATEGORY_LABELS[category.trim().toLowerCase()] ?? category.trim();
}

function recorded(value: string | null): string {
  const trimmed = value?.trim();
  return trimmed ? trimmed : 'Not recorded';
}

/** Prevent → Detect → Put out → Related, then by short name. */
function sortInvestigations(list: Investigation[]): Investigation[] {
  const rank = (category: string | null) => {
    const index = CATEGORY_ORDER.indexOf((category ?? '').trim().toLowerCase());
    return index === -1 ? CATEGORY_ORDER.length : index;
  };
  return [...list].sort((a, b) => {
    const byCategory = rank(a.category) - rank(b.category);
    if (byCategory !== 0) {
      return byCategory;
    }
    return (a.acronym ?? a.name).localeCompare(b.acronym ?? b.name, 'en');
  });
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  habitats,
  selectedHabitat,
  onSelectHabitat,
  tests,
  isLoading,
  error,
  onRetry,
}) => {
  const [activeTab, setActiveTab] = useState<'rank' | 'investigations' | 'pda' | 'safety'>('rank');
  const [pdaCategory, setPdaCategory] = useState<'Prevent' | 'Detect' | 'Put out'>('Prevent');
  const [explainTarget, setExplainTarget] = useState<TestRecord | null>(null);
  const [introComplete, setIntroComplete] = useState(false);
  const { investigations, safety, insights, loading: dataLoading, error: dataError } = useDashboardData();
  const titleGroupRef = useRef<HTMLDivElement>(null);
  const planetRef = useRef<HTMLImageElement>(null);
  const titleRef = useRef<HTMLHeadingElement>(null);

  const catalogue = investigations ? sortInvestigations(investigations) : null;
  const pdaGroups: Record<'Prevent' | 'Detect' | 'Put out', Investigation[]> = {
    Prevent: [],
    Detect: [],
    'Put out': [],
  };
  for (const inv of catalogue ?? []) {
    const label = categoryLabel(inv.category);
    if (label === 'Prevent' || label === 'Detect' || label === 'Put out') {
      pdaGroups[label].push(inv);
    }
  }
  const pdaFiltered = pdaGroups[pdaCategory];

  useLayoutEffect(() => {
    if (introComplete) {
      return;
    }

    const titleGroup = titleGroupRef.current;
    const planet = planetRef.current;
    const title = titleRef.current;

    if (!titleGroup || !planet || !title) {
      setIntroComplete(true);
      return;
    }

    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      setIntroComplete(true);
      return;
    }

    const previousOverflow = document.documentElement.style.overflow;
    document.documentElement.style.overflow = 'hidden';

    const planetBounds = planet.getBoundingClientRect();
    const groupBounds = titleGroup.getBoundingClientRect();
    const planetSize = Math.min(240, Math.max(150, window.innerWidth * 0.28));
    const titleSeparation = (planetSize - planetBounds.width) / 2;
    const centerX = window.innerWidth / 2 - (groupBounds.left + groupBounds.width / 2);
    const centerY = window.innerHeight / 2 - (groupBounds.top + groupBounds.height / 2);
    const planetCentered = `translate3d(${window.innerWidth / 2 - (planetBounds.left + planetBounds.width / 2)}px, ${window.innerHeight / 2 - (planetBounds.top + planetBounds.height / 2)}px, 0)`;
    const compositionCentered = `translate3d(${centerX - titleSeparation}px, ${centerY}px, 0)`;
    const settleEasing = 'cubic-bezier(0.22, 1, 0.36, 1)';
    const revealStart = 350 / 6000;
    const revealEnd = 1500 / 6000;
    const travelStart = 3000 / 6000;

    const groupAnimation = titleGroup.animate(
      [
        { transform: planetCentered, offset: 0, easing: 'linear' },
        {
          transform: planetCentered,
          offset: revealStart,
          easing: settleEasing,
        },
        { transform: compositionCentered, offset: revealEnd, easing: 'linear' },
        { transform: compositionCentered, offset: travelStart, easing: settleEasing },
        { transform: 'translate3d(0, 0, 0)', offset: 1 },
      ],
      { duration: 6000, fill: 'both' }
    );
    const planetAnimation = planet.animate(
      [
        { transform: `scale(${planetSize / 44})`, offset: 0 },
        { transform: `scale(${planetSize / 44})`, offset: travelStart, easing: settleEasing },
        { transform: 'scale(1)', offset: 1 },
      ],
      { duration: 6000, fill: 'both' }
    );
    const titleAnimation = title.animate(
      [
        {
          clipPath: 'inset(0 100% 0 0)',
          opacity: 0,
          transform: 'translateX(-22px) scaleX(0.88)',
          offset: 0,
        },
        {
          clipPath: 'inset(0 100% 0 0)',
          opacity: 0,
          transform: 'translateX(-22px) scaleX(0.88)',
          offset: revealStart,
          easing: settleEasing,
        },
        {
          clipPath: 'inset(0 0 0 0)',
          opacity: 1,
          transform: `translateX(${titleSeparation}px) scaleX(1)`,
          offset: revealEnd,
        },
        {
          clipPath: 'inset(0 0 0 0)',
          opacity: 1,
          transform: `translateX(${titleSeparation}px) scaleX(1)`,
          offset: travelStart,
          easing: settleEasing,
        },
        { clipPath: 'inset(0 0 0 0)', opacity: 1, transform: 'translateX(0) scaleX(1)', offset: 1 },
      ],
      {
        duration: 6000,
        fill: 'both',
      }
    );

    groupAnimation.onfinish = () => setIntroComplete(true);

    return () => {
      groupAnimation.cancel();
      planetAnimation.cancel();
      titleAnimation.cancel();
      document.documentElement.style.overflow = previousOverflow;
    };
  }, [introComplete]);

  return (
    <div className={`${styles.mainWrapper} ${introComplete ? '' : styles.opening}`}>
      {/* App Header with Rotating Planet Logo */}
      <header className={styles.appHeader}>
        <div className={styles.titleRow}>
          <div className={styles.titleWithIcon} ref={titleGroupRef}>
            <img
              src={selectedHabitat.planetGif || '/assets/planets/earth_spin.gif'}
              alt="Spinning Planet Emblem"
              className={styles.headerPlanet}
              ref={planetRef}
            />
            <h1 className={styles.mainTitle} ref={titleRef}>FLAME IN FREEFALL</h1>
          </div>
          <SourceBadge kind="source" label="[Data from source: NASA Physical Sciences]" size="md" />
        </div>
        <p className={styles.subtitle}>
          Microgravity combustion flight analysis &amp; crew habitat fire safety dashboard. Evaluating flame propagation, oxygen boundary thresholds, and toxicity buildup across space environments.
        </p>
      </header>

      {/* Provenance Key / Accessibility Legend */}
      <Legend />

      {/* Navigation Tabs with Retro Pixel Icons */}
      <nav className={styles.navTabs} aria-label="Dashboard sections">
        <button
          type="button"
          className={`${styles.tabBtn} ${activeTab === 'rank' ? styles.tabBtnActive : ''}`}
          onClick={() => setActiveTab('rank')}
        >
          <img src="/assets/icons/icon-planet.png" alt="" className={styles.tabIcon} />
          <span>1. Habitat &amp; Tests</span>
        </button>
        <button
          type="button"
          className={`${styles.tabBtn} ${activeTab === 'investigations' ? styles.tabBtnActive : ''}`}
          onClick={() => setActiveTab('investigations')}
        >
          <img src="/assets/icons/icon-flask.png" alt="" className={styles.tabIcon} />
          <span>2. Investigations</span>
        </button>
        <button
          type="button"
          className={`${styles.tabBtn} ${activeTab === 'pda' ? styles.tabBtnActive : ''}`}
          onClick={() => setActiveTab('pda')}
        >
          <img src="/assets/icons/icon-shield.png" alt="" className={styles.tabIcon} />
          <span>3. Prevent · Detect · Put out</span>
        </button>
        <button
          type="button"
          className={`${styles.tabBtn} ${activeTab === 'safety' ? styles.tabBtnActive : ''}`}
          onClick={() => setActiveTab('safety')}
        >
          <img src="/assets/icons/icon-alert.png" alt="" className={styles.tabIcon} />
          <span>4. Key Finding &amp; Safety Table</span>
        </button>
      </nav>

      {dataError && (
        <p className={styles.dataError} role="alert">
          {dataError}
        </p>
      )}

      {/* TAB 1: HABITAT & RANKED TESTS */}
      {activeTab === 'rank' && (
        <main>
          <HabitatPicker
            habitats={habitats}
            selectedHabitat={selectedHabitat}
            onSelectHabitat={onSelectHabitat}
            isLoading={isLoading}
          />

          <BriefPanel habitat={selectedHabitat} />
          <AskPanel habitat={selectedHabitat} />

          <TestList
            tests={tests}
            selectedHabitat={selectedHabitat}
            isLoading={isLoading}
            error={error}
            onRetry={onRetry}
            onExplain={(t) => setExplainTarget(t)}
          />
        </main>
      )}

      {/* TAB 2: INVESTIGATIONS */}
      {activeTab === 'investigations' && (
        <section aria-labelledby="inv-heading">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div>
              <h2 id="inv-heading" style={{ margin: 0, fontSize: '20px', fontFamily: 'monospace' }}>
                NASA MICROGRAVITY INVESTIGATIONS CATALOGUE
              </h2>
              <p style={{ margin: '4px 0 0', color: '#94a3b8', fontSize: '13px' }}>
                {catalogue
                  ? `${catalogue.length} investigations from the PSI Data Repository`
                  : 'From the PSI Data Repository'}
              </p>
            </div>
            <SourceBadge kind="source" size="sm" />
          </div>

          {!catalogue ? (
            <p style={{ color: '#94a3b8', fontSize: '14px' }}>
              {dataLoading
                ? 'Loading investigations…'
                : 'Investigation catalogue unavailable. See the error above.'}
            </p>
          ) : catalogue.length === 0 ? (
            <p style={{ color: '#94a3b8', fontSize: '14px' }}>
              No investigations were returned.
            </p>
          ) : (
            <div className={styles.invGrid}>
              {catalogue.map((inv) => (
                <div key={inv.id} className={styles.invCard}>
                  <div className={styles.invCardHeader}>
                    <div>
                      <h3 className={styles.invTitle}>
                        <img src="/assets/icons/icon-flask.png" alt="" style={{ width: '16px', height: '16px', imageRendering: 'pixelated' }} />
                        {inv.acronym?.trim() || inv.name}
                      </h3>
                      {inv.acronym?.trim() && (
                        <p className={styles.invFullName}>{inv.name}</p>
                      )}
                    </div>
                    <span className={styles.categoryPill}>{categoryLabel(inv.category)}</span>
                  </div>
                  <div className={styles.invDetail}>
                    <strong>Objective:</strong> {recorded(inv.objective)}
                  </div>
                  <div className={styles.invDetail}>
                    <strong>Fuels:</strong> {recorded(inv.fuels)}
                  </div>
                  <div className={styles.invDetail}>
                    <strong>Hardware:</strong> {recorded(inv.hardware_family ?? inv.hardware)}
                  </div>
                  <div className={styles.invDetail}>
                    <strong>Sensors:</strong> {recorded(inv.sensors)}
                  </div>
                  <div className={styles.invDetail}>
                    <strong>Key Variables:</strong> {recorded(inv.variables)}
                  </div>
                </div>
              ))}
            </div>
          )}
          <HardwarePanel />
        </section>
      )}

      {/* TAB 3: PREVENT · DETECT · PUT OUT */}
      {activeTab === 'pda' && (
        <section className={styles.pdaContainer} aria-labelledby="pda-heading">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h2 id="pda-heading" style={{ margin: 0, fontSize: '20px', fontFamily: 'monospace' }}>
              NASA FIRE SAFETY ARCHITECTURE
            </h2>
            <SourceBadge kind="source" size="sm" />
          </div>
          <p style={{ color: '#94a3b8', fontSize: '14px', marginBottom: '16px' }}>
            NASA groups human spaceflight fire safety into three sequential phases. Select a phase below:
          </p>
          {!catalogue ? (
            <p style={{ color: '#94a3b8', fontSize: '14px' }}>
              {dataLoading
                ? 'Loading investigations…'
                : 'Investigation data unavailable. See the error above.'}
            </p>
          ) : (
            <>
              <div className={styles.pdaBtnRow}>
                {(['Prevent', 'Detect', 'Put out'] as const).map((cat) => (
                  <button
                    key={cat}
                    type="button"
                    className={`${styles.pdaBtn} ${pdaCategory === cat ? styles.pdaBtnActive : ''}`}
                    onClick={() => setPdaCategory(cat)}
                  >
                    <img
                      src={
                        cat === 'Prevent'
                          ? '/assets/icons/icon-shield.png'
                          : cat === 'Detect'
                          ? '/assets/icons/icon-alert.png'
                          : '/assets/icons/icon-check.png'
                      }
                      alt=""
                      style={{ width: '16px', height: '16px', imageRendering: 'pixelated' }}
                    />
                    <span>
                      {cat} ({pdaGroups[cat].length})
                    </span>
                  </button>
                ))}
              </div>

              {pdaFiltered.length === 0 ? (
                <p style={{ color: '#94a3b8', fontSize: '14px' }}>
                  No investigations in the data are tagged &ldquo;{pdaCategory}&rdquo;.
                </p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {pdaFiltered.map((inv) => (
                    <div key={inv.id} className={styles.invCard}>
                      <div className={styles.invCardHeader}>
                        <div>
                          <h3 className={styles.invTitle}>
                            <img src="/assets/icons/icon-flask.png" alt="" style={{ width: '16px', height: '16px', imageRendering: 'pixelated' }} />
                            {inv.acronym?.trim() || inv.name}
                          </h3>
                          {inv.acronym?.trim() && (
                            <p className={styles.invFullName}>{inv.name}</p>
                          )}
                        </div>
                        <SourceBadge kind="source" size="sm" />
                      </div>
                      <p style={{ margin: 0, fontSize: '14px', color: '#cbd5e1' }}>
                        <strong>Focus:</strong> {recorded(inv.objective)}
                      </p>
                      <p style={{ margin: 0, fontSize: '13px', color: '#94a3b8' }}>
                        Hardware: {recorded(inv.hardware_family ?? inv.hardware)} | Fuels: {recorded(inv.fuels)}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </section>
      )}

      {/* TAB 4: KEY FINDING & SAFETY TABLE */}
      {activeTab === 'safety' && (
        <section aria-labelledby="safety-heading">
          {/* Key finding, served by GET /insights */}
          <div className={styles.findingCard}>
            <div className={styles.findingHeader}>
              <h2 className={styles.findingTitle}>
                <img src="/assets/icons/icon-alert.png" alt="" style={{ width: '22px', height: '22px', imageRendering: 'pixelated' }} />
                CRITICAL KEY FINDING{insights ? `: ${insights.key_finding.title.toUpperCase()}` : ''}
              </h2>
              <SourceBadge kind="source" size="sm" />
            </div>
            {insights ? (
              <>
                <blockquote className={styles.findingQuote}>
                  &ldquo;{insights.key_finding.text}&rdquo;
                </blockquote>
                <div className={styles.findingSource}>
                  <span>Source:</span>
                  <a
                    href={insights.key_finding.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ color: '#38bdf8', textDecoration: 'underline' }}
                  >
                    {insights.key_finding.source_label}
                  </a>
                  {insights.key_finding.status && (
                    <span style={{ color: '#94a3b8' }}>
                      ({insights.key_finding.status})
                    </span>
                  )}
                </div>
              </>
            ) : (
              <p style={{ color: '#94a3b8', fontSize: '14px', margin: 0 }}>
                {dataLoading
                  ? 'Loading key finding…'
                  : 'Key finding unavailable. See the error above.'}
              </p>
            )}
          </div>

          {/* Safety Table: What NASA Has Tested */}
          <div className={styles.safetySection}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 id="safety-heading" style={{ margin: 0, fontSize: '18px', fontFamily: 'monospace' }}>
                HONEST SAFETY TABLE: WHAT NASA HAS TESTED
              </h3>
              <SourceBadge kind="source" size="sm" />
            </div>
            <p style={{ color: '#94a3b8', fontSize: '13px', margin: '8px 0 16px 0' }}>
              Each cell shows the closest NASA microgravity test for that habitat, linked to its source. We never invent arbitrary pass/fail thresholds.
            </p>

            {safety ? (
              <>
                <div className={styles.tableContainer}>
                  <table className={styles.dataTable}>
                    <thead>
                      <tr>
                        <th>Sample Material</th>
                        {safety.habitats.map((habitat) => (
                          <th key={habitat}>{habitat}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {safety.rows.map((row) => (
                        <tr key={row.material}>
                          <td>
                            <strong>{row.material}</strong>
                          </td>
                          {row.cells.map((cell) => (
                            <td key={`${row.material}-${cell.habitat}`}>
                              {cell.state === 'rule' ? (
                                <span>{cell.rule ?? 'Rule listed'}</span>
                              ) : cell.state === 'tested' && cell.nearest_test ? (
                                <>
                                  <span className={styles.testedPill}>Nearest test</span>
                                  <br />
                                  {cell.nearest_test.source_url ? (
                                    <a
                                      href={cell.nearest_test.source_url}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      style={{ color: '#38bdf8', textDecoration: 'underline' }}
                                    >
                                      {cell.nearest_test.test_id}
                                    </a>
                                  ) : (
                                    cell.nearest_test.test_id
                                  )}
                                  {': '}
                                  {cell.nearest_test.oxygen_pct ?? '—'}% O₂,{' '}
                                  {cell.nearest_test.pressure_psi ?? '—'} psi
                                  <br />
                                  <small style={{ color: '#94a3b8' }}>
                                    Oxygen gap {cell.oxygen_gap ?? '—'} points, pressure gap{' '}
                                    {cell.pressure_gap ?? '—'} psi
                                  </small>
                                </>
                              ) : (
                                <span className={styles.notTested}>Not tested</span>
                              )}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <p style={{ fontSize: '12px', color: '#64748b', marginTop: '12px' }}>
                  {safety.rules_read
                    ? 'Cells marked “Rule” cite the transcribed NASA-STD-6001B requirement instead of a nearest test.'
                    : 'No pass/fail rule is applied: NASA-STD-6001B rules have not been transcribed for these materials, so every cell shows the nearest NASA test only.'}
                  {' '}Standard references: NASA-STD-6001B Flammability Test Standard · NASA Physical Sciences Informatics (PSI).
                </p>
              </>
            ) : (
              <p style={{ color: '#94a3b8', fontSize: '14px' }}>
                {dataLoading
                  ? 'Loading safety table…'
                  : 'Safety table unavailable. See the error above.'}
              </p>
            )}
          </div>
          <EarthUsePanel />
        </section>
      )}

      {/* AI Explanation Modal */}
      <ExplainModal
        key={explainTarget ? explainTarget.id : 'none'}
        test={explainTarget}
        isOpen={explainTarget !== null}
        onClose={() => setExplainTarget(null)}
      />

      {/* Global Footer with Source Links and Asset Pack Licensing Attribution */}
      <footer className={styles.footer}>
        <div className={styles.footerLinks}>
          <a
            href="https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/"
            target="_blank"
            rel="noopener noreferrer"
            className={styles.footerLink}
          >
            NASA Space Apps Challenge: Flame in Freefall
          </a>
          <span>·</span>
          <a
            href="https://psi.nasa.gov/physci/repo/"
            target="_blank"
            rel="noopener noreferrer"
            className={styles.footerLink}
          >
            NASA PSI Database
          </a>
          <span>·</span>
          <a
            href="https://ntrs.nasa.gov/"
            target="_blank"
            rel="noopener noreferrer"
            className={styles.footerLink}
          >
            NASA Technical Reports Server (NTRS)
          </a>
        </div>
        <div>
          Every displayed metric originates from verified NASA microgravity flight investigations. Preliminary data explicitly labeled.
        </div>
        <div className={styles.assetCredits}>
          Visual Assets &amp; Retro UI credits:{' '}
          <a href="https://heyheythere.itch.io/pixel-ui-scifi-free" target="_blank" rel="noopener noreferrer" style={{ color: '#64748b' }}>
            Pixel UI Sci-Fi Free by heyheythere (CC BY 4.0)
          </a>{' '}
          ·{' '}
          <a href="https://helianthus-games.itch.io/animated-pixel-art-planets" target="_blank" rel="noopener noreferrer" style={{ color: '#64748b' }}>
            Spinning Planets by Helianthus Games
          </a>{' '}
          ·{' '}
          <a href="https://aquumgifts.itch.io/cozy-space-icons-ui" target="_blank" rel="noopener noreferrer" style={{ color: '#64748b' }}>
            Cozy Space Icons &amp; UI by Spaceyyy / Aquum Gifts
          </a>
        </div>
      </footer>
    </div>
  );
};

export default DashboardView;
