import React, { useEffect, useState } from 'react';
import styles from './ExplainModal.module.css';
import type { Habitat, TestRecord } from '../types';
import SourceBadge from './SourceBadge';
import { fetchAiExplanation } from '../api/client';

interface ExplainModalProps {
  test: TestRecord | null;
  habitat: Habitat;
  isOpen: boolean;
  onClose: () => void;
}

export const ExplainModal: React.FC<ExplainModalProps> = ({
  test,
  habitat,
  isOpen,
  onClose,
}) => {
  const [explanation, setExplanation] = useState<string>('');
  const [timestamp, setTimestamp] = useState<string>('');

  useEffect(() => {
    if (!isOpen || !test) return;

    let isSubscribed = true;
    fetchAiExplanation(test, habitat)
      .then((res) => {
        if (isSubscribed) {
          setExplanation(res.explanation);
          setTimestamp(res.generatedAt);
        }
      })
      .catch((err) => {
        if (isSubscribed) {
          setExplanation(`Failed to generate explanation: ${String(err)}`);
        }
      });

    return () => {
      isSubscribed = false;
    };
  }, [isOpen, test, habitat]);

  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen || !test) return null;

  return (
    <div
      className={styles.backdrop}
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <div className={styles.titleArea}>
            <SourceBadge kind="ai" size="md" />
            <h3 id="modal-title" className={styles.title}>
              AI FIRE DYNAMICS SYNTHESIS
            </h3>
          </div>
          <button
            className={styles.closeBtn}
            onClick={onClose}
            aria-label="Close modal"
          >
            ✕
          </button>
        </div>

        <div className={styles.content}>
          <div className={styles.metaBox}>
            <div className={styles.metaRow}>
              <span className={styles.metaLabel}>Investigation Test:</span>
              <strong>{test.investigation} ({test.id})</strong>
            </div>
            <div className={styles.metaRow}>
              <span className={styles.metaLabel}>Sample Material:</span>
              <span>{test.material ?? 'Not specified'}</span>
            </div>
            <div className={styles.metaRow}>
              <span className={styles.metaLabel}>Target Habitat:</span>
              <span>
                {habitat.name} (O₂ {habitat.oxygen_pct}%, {habitat.pressure_psi} psi)
              </span>
            </div>
          </div>

          <div className={styles.aiResponseBox}>
            <div className={styles.aiResponseHeader}>
              <SourceBadge kind="ai" label="[AI-generated explanation here]" size="sm" />
              {timestamp && (
                <small style={{ color: '#6ee7b7', fontSize: '11px', fontFamily: 'monospace' }}>
                  {new Date(timestamp).toLocaleTimeString()}
                </small>
              )}
            </div>
            {!explanation ? (
              <p className={styles.aiText} style={{ color: '#94a3b8', fontStyle: 'italic' }}>
                Analyzing microgravity oxygen and pressure boundary conditions...
              </p>
            ) : (
              <p className={styles.aiText}>{explanation}</p>
            )}
          </div>

          <p className={styles.footerNote}>
            * AI-generated synthesis placeholder using record boundary parameters. All underlying test metrics derive from verified NASA telemetry citations.
          </p>
        </div>

        <div className={styles.footer}>
          <button className={styles.actionBtn} onClick={onClose}>
            Acknowledge &amp; Return
          </button>
        </div>
      </div>
    </div>
  );
};

export default ExplainModal;
