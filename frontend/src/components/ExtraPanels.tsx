/**
 * Panels for the backend routes that had no place on the page yet: the habitat
 * brief, the question box, the hardware comparison and the Earth-use notes.
 * Every fact shown here comes from the backend response, unchanged.
 */

import React, { useState } from 'react';
import styles from './DashboardView.module.css';
import SourceBadge from './SourceBadge';
import { useApi } from '../api/useApi';
import { askQuestion, getBrief, getEarthUse, getHardware, getQaExamples } from '../api/client';
import type { Habitat, QaAnswer } from '../types';

const linkStyle: React.CSSProperties = { color: '#38bdf8', textDecoration: 'underline' };
const mutedStyle: React.CSSProperties = { color: '#94a3b8', fontSize: '13px' };
const panelHeadingStyle: React.CSSProperties = { margin: 0, fontSize: '18px', fontFamily: 'monospace' };
const panelHeaderStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  gap: '12px',
  flexWrap: 'wrap',
};

const SourceLink: React.FC<{ href?: string | null; children: React.ReactNode }> = ({ href, children }) =>
  href ? (
    <a href={href} target="_blank" rel="noopener noreferrer" style={linkStyle}>
      {children}
    </a>
  ) : (
    <span style={mutedStyle}>No source link recorded</span>
  );

const LoadState: React.FC<{ loading: boolean; error: string | null; what: string }> = ({
  loading,
  error,
  what,
}) => {
  if (loading) {
    return (
      <p style={mutedStyle} aria-busy="true">
        Loading {what}...
      </p>
    );
  }
  if (error) {
    return (
      <p role="alert" style={{ color: '#fca5a5', fontSize: '14px' }}>
        Could not load {what} from the backend. ({error})
      </p>
    );
  }
  return null;
};

/** A statement with its status (if any) and the link it rests on. */
const SourcedNote: React.FC<{
  label: string;
  text: string;
  status?: string;
  href?: string | null;
  linkLabel?: string;
}> = ({ label, text, status, href, linkLabel }) => (
  <div style={{ marginTop: '14px', fontSize: '14px', color: '#cbd5e1' }}>
    <strong>{label}</strong>
    {status ? <span style={mutedStyle}> ({status})</span> : null}
    <div style={{ marginTop: '4px' }}>{text}</div>
    <div style={{ marginTop: '4px', fontSize: '13px' }}>
      <SourceLink href={href}>{linkLabel ?? 'Source this is based on'}</SourceLink>
    </div>
  </div>
);

/* ------------------------------------------------------------------ */
/* One-page habitat brief (GET /brief)                                 */
/* ------------------------------------------------------------------ */

export const BriefPanel: React.FC<{ habitat: Habitat }> = ({ habitat }) => {
  const [open, setOpen] = useState(false);
  const brief = useApi(() => getBrief(habitat.name), habitat.name);

  return (
    <div className={styles.safetySection} style={{ marginBottom: '24px' }}>
      <div style={panelHeaderStyle}>
        <h3 style={panelHeadingStyle}>ONE-PAGE FIRE BRIEF: {habitat.name.toUpperCase()}</h3>
        <button type="button" className={styles.pdaBtn} onClick={() => setOpen((value) => !value)}>
          {open ? 'Hide brief' : 'Show brief'}
        </button>
      </div>
      {open && (
        <div style={{ marginTop: '14px', fontSize: '14px', color: '#cbd5e1' }}>
          <LoadState loading={brief.loading} error={brief.error} what="the brief" />
          {brief.data && (
            <>
              <p style={{ margin: '0 0 10px 0' }}>
                Reference air: {brief.data.habitat.oxygen_pct}% oxygen at {brief.data.habitat.pressure_psi}{' '}
                psi ({brief.data.habitat.status}).
              </p>
              <strong>Five closest NASA tests</strong>
              <ol style={{ margin: '6px 0 0 18px', padding: 0 }}>
                {brief.data.top_tests.map((test) => (
                  <li key={test.id} style={{ marginBottom: '4px' }}>
                    {test.investigation}
                    {test.material ? `, ${test.material}` : ''}: {test.oxygen_pct ?? 'not reported'}% O₂,{' '}
                    {test.pressure_psi ?? 'not reported'} psi (distance {test.distance ?? 'not scored'},{' '}
                    {test.label}) <SourceLink href={test.source_url}>{test.id}</SourceLink>
                  </li>
                ))}
              </ol>
              {brief.data.key_finding && (
                <SourcedNote
                  label="Key finding"
                  text={brief.data.key_finding.text}
                  status={brief.data.key_finding.status}
                  href={brief.data.key_finding.source_url}
                  linkLabel={brief.data.key_finding.source_label}
                />
              )}
              {brief.data.gap && (
                <SourcedNote
                  label="Known data gap"
                  text={brief.data.gap.text}
                  href={brief.data.gap.source_url}
                  linkLabel={brief.data.gap.source_label}
                />
              )}
              {brief.data.control_need && (
                <SourcedNote
                  label="What this suggests for future controls"
                  text={brief.data.control_need.text}
                  status={brief.data.control_need.status}
                  href={brief.data.control_need.basis_url}
                />
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
};

/* ------------------------------------------------------------------ */
/* Question box (POST /qa)                                             */
/* ------------------------------------------------------------------ */

export const AskPanel: React.FC<{ habitat: Habitat }> = ({ habitat }) => {
  const [question, setQuestion] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [answer, setAnswer] = useState<QaAnswer | null>(null);
  const examples = useApi(() => getQaExamples());

  const ask = (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || busy) {
      return;
    }
    setQuestion(trimmed);
    setBusy(true);
    setError(null);
    setAnswer(null);
    askQuestion(trimmed, habitat.name)
      .then((result) => setAnswer(result))
      .catch((err: unknown) => setError(err instanceof Error ? err.message : String(err)))
      .finally(() => setBusy(false));
  };

  const cards = answer ? (answer.citations.length > 0 ? answer.citations : answer.sources_considered) : [];

  return (
    <div className={styles.safetySection} style={{ marginBottom: '24px' }}>
      <div style={panelHeaderStyle}>
        <h3 style={panelHeadingStyle}>ASK ABOUT THE RECORDS</h3>
        <SourceBadge kind="ai" label="[AI answer, checked against the records]" size="sm" />
      </div>
      <p style={{ ...mutedStyle, margin: '8px 0 12px 0' }}>
        The answer uses only the NASA records in this app. Every sentence must cite a record, and every
        number is checked against it. If the records do not hold the answer, the app says so.
      </p>
      <form
        onSubmit={(event) => {
          event.preventDefault();
          ask(question);
        }}
        style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}
      >
        <input
          type="text"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="For example: When was smoke detected in Saffire VI?"
          aria-label="Your question"
          style={{
            flex: '1 1 320px',
            padding: '8px 10px',
            background: '#0b1220',
            color: '#e2e8f0',
            border: '1px solid #374151',
            borderRadius: '6px',
            fontSize: '14px',
          }}
        />
        <button type="submit" className={styles.pdaBtn} disabled={busy || !question.trim()}>
          {busy ? 'Checking...' : 'Ask'}
        </button>
      </form>
      {(examples.data ?? []).length > 0 && (
        <div style={{ marginTop: '10px', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {(examples.data ?? []).map((example) => (
            <button key={example} type="button" className={styles.pdaBtn} onClick={() => ask(example)}>
              {example}
            </button>
          ))}
        </div>
      )}
      {error && (
        <p role="alert" style={{ color: '#fca5a5', fontSize: '14px' }}>
          Could not reach the question service. ({error})
        </p>
      )}
      {answer && (
        <div style={{ marginTop: '14px', fontSize: '14px', color: '#cbd5e1' }} aria-live="polite">
          {answer.answer ? (
            <>
              <SourceBadge
                kind="ai"
                label={answer.origin === 'cache' ? '[Saved AI answer]' : '[AI-generated answer]'}
                size="sm"
              />
              <p style={{ margin: '8px 0' }}>{answer.answer}</p>
            </>
          ) : (
            <p style={{ margin: '8px 0' }}>{answer.note ?? "The records don't answer this."}</p>
          )}
          {cards.length > 0 && (
            <>
              <strong>{answer.answer ? 'Records cited' : 'Closest records'}</strong>
              <ul style={{ margin: '6px 0 0 18px', padding: 0 }}>
                {cards.map((card) => (
                  <li key={card.id}>
                    <SourceLink href={card.source_url}>{card.label}</SourceLink>{' '}
                    <span style={mutedStyle}>[{card.id}]</span>
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
    </div>
  );
};

/* ------------------------------------------------------------------ */
/* Hardware comparison (GET /hardware)                                 */
/* ------------------------------------------------------------------ */

export const HardwarePanel: React.FC = () => {
  const hardware = useApi(() => getHardware());

  return (
    <div className={styles.safetySection} style={{ marginTop: '24px' }}>
      <div style={panelHeaderStyle}>
        <h3 style={panelHeadingStyle}>COMPARE TEST HARDWARE</h3>
        <SourceBadge kind="source" size="sm" />
      </div>
      <p style={{ ...mutedStyle, margin: '8px 0 14px 0' }}>
        Tests run in different equipment are not the same kind of evidence. Investigations are grouped by
        the hardware family named in their NASA record.
      </p>
      <LoadState loading={hardware.loading} error={hardware.error} what="the hardware groups" />
      {hardware.data &&
        Object.entries(hardware.data).map(([family, members]) => (
          <div key={family} style={{ marginBottom: '12px' }}>
            <strong style={{ color: '#e2e8f0' }}>
              {family} ({members.length})
            </strong>
            <div style={{ ...mutedStyle, marginTop: '4px' }}>
              {members.map((member) => member.name).join(' · ')}
            </div>
          </div>
        ))}
    </div>
  );
};

/* ------------------------------------------------------------------ */
/* Earth use (GET /earth-use)                                          */
/* ------------------------------------------------------------------ */

export const EarthUsePanel: React.FC = () => {
  const earthUse = useApi(() => getEarthUse());

  return (
    <div className={styles.safetySection} style={{ marginTop: '24px' }}>
      <div style={panelHeaderStyle}>
        <h3 style={panelHeadingStyle}>HOW THIS HELPS ON EARTH</h3>
        <SourceBadge kind="source" size="sm" />
      </div>
      <LoadState loading={earthUse.loading} error={earthUse.error} what="the Earth-use notes" />
      {(earthUse.data?.spinoffs ?? []).map((item) => (
        <SourcedNote
          key={item.title}
          label={item.title}
          text={item.text}
          href={item.source_url}
          linkLabel={item.source_label}
        />
      ))}
      {earthUse.data && earthUse.data.from_research.length > 0 && (
        <details style={{ marginTop: '16px', color: '#cbd5e1', fontSize: '14px' }}>
          <summary style={{ cursor: 'pointer' }}>
            Earth benefits stated in each NASA investigation record ({earthUse.data.from_research.length})
          </summary>
          {earthUse.data.from_research.map((entry) => (
            <div key={entry.investigation_id} style={{ marginTop: '12px' }}>
              <strong>{entry.investigation_name}</strong>
              {entry.benefits.map((benefit) => (
                <div key={benefit} style={{ marginTop: '4px' }}>
                  {benefit}
                </div>
              ))}
              <div style={{ marginTop: '4px', fontSize: '13px' }}>
                <SourceLink href={entry.source_url}>NASA PSI record {entry.investigation_id}</SourceLink>
              </div>
            </div>
          ))}
        </details>
      )}
    </div>
  );
};
