import React, { useState } from 'react';
import styles from './DashboardView.module.css';
import type { Habitat, TestRecord } from '../types';
import HabitatPicker from './HabitatPicker';
import TestList from './TestList';
import Legend from './Legend';
import ExplainModal from './ExplainModal';
import SourceBadge from './SourceBadge';
import { MOCK_INVESTIGATIONS } from '../data/mockData';

interface DashboardViewProps {
  habitats: Habitat[];
  selectedHabitat: Habitat;
  onSelectHabitat: (habitat: Habitat) => void;
  tests: TestRecord[];
  isLoading: boolean;
  error: string | null;
  onRetry: () => void;
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

  const pdaFiltered = MOCK_INVESTIGATIONS.filter((inv) => inv.cat === pdaCategory);

  return (
    <div className={styles.mainWrapper}>
      {/* App Header */}
      <header className={styles.appHeader}>
        <div className={styles.titleRow}>
          <h1 className={styles.mainTitle}>FLAME IN FREEFALL</h1>
          <SourceBadge kind="source" label="[Data from source: NASA Physical Sciences]" size="md" />
        </div>
        <p className={styles.subtitle}>
          Microgravity combustion flight analysis &amp; crew habitat fire safety dashboard. Evaluating flame propagation, oxygen boundary thresholds, and toxicity buildup across space environments.
        </p>
      </header>

      {/* Provenance Key / Accessibility Legend */}
      <Legend />

      {/* Navigation Tabs */}
      <nav className={styles.navTabs} aria-label="Dashboard sections">
        <button
          type="button"
          className={`${styles.tabBtn} ${activeTab === 'rank' ? styles.tabBtnActive : ''}`}
          onClick={() => setActiveTab('rank')}
        >
          1. Habitat &amp; Tests
        </button>
        <button
          type="button"
          className={`${styles.tabBtn} ${activeTab === 'investigations' ? styles.tabBtnActive : ''}`}
          onClick={() => setActiveTab('investigations')}
        >
          2. Investigations
        </button>
        <button
          type="button"
          className={`${styles.tabBtn} ${activeTab === 'pda' ? styles.tabBtnActive : ''}`}
          onClick={() => setActiveTab('pda')}
        >
          3. Prevent · Detect · Put out
        </button>
        <button
          type="button"
          className={`${styles.tabBtn} ${activeTab === 'safety' ? styles.tabBtnActive : ''}`}
          onClick={() => setActiveTab('safety')}
        >
          4. Key Finding &amp; Safety Table
        </button>
      </nav>

      {/* TAB 1: HABITAT & RANKED TESTS */}
      {activeTab === 'rank' && (
        <main>
          <HabitatPicker
            habitats={habitats}
            selectedHabitat={selectedHabitat}
            onSelectHabitat={onSelectHabitat}
            isLoading={isLoading}
          />

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
            <h2 id="inv-heading" style={{ margin: 0, fontSize: '20px', fontFamily: 'monospace' }}>
              NASA MICROGRAVITY INVESTIGATIONS CATALOGUE
            </h2>
            <SourceBadge kind="source" size="sm" />
          </div>
          <div className={styles.invGrid}>
            {MOCK_INVESTIGATIONS.map((inv) => (
              <div key={inv.name} className={styles.invCard}>
                <div className={styles.invCardHeader}>
                  <h3 className={styles.invTitle}>{inv.name}</h3>
                  <span className={styles.categoryPill}>{inv.cat}</span>
                </div>
                <div className={styles.invDetail}>
                  <strong>Objective:</strong> {inv.objective}
                </div>
                <div className={styles.invDetail}>
                  <strong>Fuels:</strong> {inv.fuels}
                </div>
                <div className={styles.invDetail}>
                  <strong>Hardware:</strong> {inv.hw}
                </div>
                <div className={styles.invDetail}>
                  <strong>Sensors:</strong> {inv.sensors}
                </div>
                <div className={styles.invDetail}>
                  <strong>Key Variables:</strong> {inv.vars}
                </div>
              </div>
            ))}
          </div>
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
          <div className={styles.pdaBtnRow}>
            {(['Prevent', 'Detect', 'Put out'] as const).map((cat) => (
              <button
                key={cat}
                type="button"
                className={`${styles.pdaBtn} ${pdaCategory === cat ? styles.pdaBtnActive : ''}`}
                onClick={() => setPdaCategory(cat)}
              >
                {cat}
              </button>
            ))}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {pdaFiltered.map((inv) => (
              <div key={inv.name} className={styles.invCard}>
                <div className={styles.invCardHeader}>
                  <h3 className={styles.invTitle}>{inv.name}</h3>
                  <SourceBadge kind="source" size="sm" />
                </div>
                <p style={{ margin: 0, fontSize: '14px', color: '#cbd5e1' }}>
                  <strong>Focus:</strong> {inv.objective}
                </p>
                <p style={{ margin: 0, fontSize: '13px', color: '#94a3b8' }}>
                  Hardware: {inv.hw} | Fuels: {inv.fuels}
                </p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* TAB 4: KEY FINDING & SAFETY TABLE */}
      {activeTab === 'safety' && (
        <section aria-labelledby="safety-heading">
          {/* Saffire-VI 981-Second Key Finding Card */}
          <div className={styles.findingCard}>
            <div className={styles.findingHeader}>
              <h2 className={styles.findingTitle}>CRITICAL KEY FINDING: SAFFIRE-VI</h2>
              <SourceBadge kind="source" label="[Data from source: ICES 2024]" size="sm" />
            </div>
            <blockquote className={styles.findingQuote}>
              &ldquo;In Saffire VI, the smoke was readily detected at 981 seconds, after most of the hazardous gas release had already happened.&rdquo;
            </blockquote>
            <div className={styles.findingSource}>
              <span>Source:</span>
              <a
                href="https://ntrs.nasa.gov/citations/20240007488"
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: '#38bdf8', textDecoration: 'underline' }}
              >
                Saffire VI Presentation, ICES 2024 (NTRS 20240007488)
              </a>
            </div>
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
              Each cell displays verified NASA microgravity test boundaries or official standards. We never invent arbitrary pass/fail thresholds.
            </p>

            <div className={styles.tableContainer}>
              <table className={styles.dataTable}>
                <thead>
                  <tr>
                    <th>Sample Material</th>
                    <th>Tested Conditions (O₂, Pressure)</th>
                    <th>Earth Air (21%, 14.7 psi)</th>
                    <th>Moon Base Air (30%, 10.2 psi)</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>
                      <strong>Two-sided PMMA, 1 cm thick, 18 cm</strong>
                      <br />
                      <small style={{ color: '#94a3b8' }}>Saffire VI-3</small>
                    </td>
                    <td>
                      <SourceBadge kind="source" size="sm" /> 30.3% O₂, 7.9 psi
                    </td>
                    <td className={styles.notTested}>Not tested yet in microgravity</td>
                    <td>
                      <span className={styles.testedPill}>Tested</span>
                      <br />
                      Tested at 30.3% O₂ and 7.9 psi (close to Moon base 30%, but at reduced pressure)
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <strong>SIBAL cloth, 50 cm</strong>
                      <br />
                      <small style={{ color: '#94a3b8' }}>Saffire IV-1, VI-2</small>
                    </td>
                    <td>
                      <SourceBadge kind="source" size="sm" /> 22.0%, 14.5 psi (IV-1)
                      <br />
                      31.0%, 7.9 psi (VI-2)
                    </td>
                    <td>
                      <span className={styles.testedPill}>Tested</span>
                      <br />
                      Tested at 22.0% O₂, 14.5 psi (close to Earth sea level)
                    </td>
                    <td>
                      <span className={styles.testedPill}>Tested</span>
                      <br />
                      Tested at 31.0% O₂, 7.9 psi (matches elevated oxygen range)
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <strong>Cotton jersey, 50 cm</strong>
                      <br />
                      <small style={{ color: '#94a3b8' }}>Saffire V-2</small>
                    </td>
                    <td>
                      <SourceBadge kind="source" size="sm" /> 26.2% O₂, 10.3 psi
                    </td>
                    <td className={styles.notTested}>Not tested yet</td>
                    <td>
                      <span className={styles.testedPill}>Tested</span>
                      <br />
                      Tested at 10.3 psi (closely bounds Moon base 10.2 psi atmosphere)
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <p style={{ fontSize: '12px', color: '#64748b', marginTop: '12px' }}>
              Standard References: NASA-STD-6001B Flammability Test Standard · NASA Physical Sciences Informatics (PSI)
            </p>
          </div>
        </section>
      )}

      {/* AI Explanation Modal */}
      <ExplainModal
        key={explainTarget ? explainTarget.id : 'none'}
        test={explainTarget}
        habitat={selectedHabitat}
        isOpen={explainTarget !== null}
        onClose={() => setExplainTarget(null)}
      />

      {/* Global Footer */}
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
      </footer>
    </div>
  );
};

export default DashboardView;
