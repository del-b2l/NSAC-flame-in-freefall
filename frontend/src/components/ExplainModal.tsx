import React, { useEffect, useState } from 'react';
import styles from './ExplainModal.module.css';
import type { Explanation, TestRecord } from '../types';
import SourceBadge from './SourceBadge';
import { explainTest } from '../api/client';

interface ExplainModalProps {
  test: TestRecord | null;
  isOpen: boolean;
  onClose: () => void;
}

export const ExplainModal: React.FC<ExplainModalProps> = ({ test, isOpen, onClose }) => {
  const [explanation, setExplanation] = useState<Explanation | null>(null);
  const [error, setError] = useState<string | null>(null);
  const testId = test?.id ?? null;

  useEffect(() => {
    if (!isOpen || !testId) return;

    let isSubscribed = true;
    explainTest(testId)
      .then((res) => {
        if (isSubscribed) {
          setExplanation(res);
        }
      })
      .catch((err: unknown) => {
        if (isSubscribed) {
          setError(err instanceof Error ? err.message : String(err));
        }
      });

    return () => {
      isSubscribed = false;
    };
  }, [isOpen, testId]);

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

  // The backend says whether the text was written by the AI model or is NASA's own.
  const isAi = explanation ? explanation.generated || explanation.origin === 'cache' : true;
  const badgeLabel = !explanation
    ? '[Summary]'
    : explanation.origin === 'cache'
      ? '[Saved AI summary]'
      : explanation.generated
        ? '[AI-generated summary]'
        : "[NASA's own result text]";
  const sourceUrl = explanation?.source_url ?? test.source_url ?? null;

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
            <SourceBadge kind={isAi ? 'ai' : 'source'} size="md" />
            <h3 id="modal-title" className={styles.title}>
              TEST SUMMARY
            </h3>
          </div>
          <button className={styles.closeBtn} onClick={onClose} aria-label="Close modal">
            ✕
          </button>
        </div>

        <div className={styles.content}>
          <div className={styles.metaBox}>
            <div className={styles.metaRow}>
              <span className={styles.metaLabel}>Investigation Test:</span>
              <strong>
                {test.investigation} ({test.id})
              </strong>
            </div>
            <div className={styles.metaRow}>
              <span className={styles.metaLabel}>Sample Material:</span>
              <span>{test.material ?? 'Not specified'}</span>
            </div>
          </div>

          <div className={styles.aiResponseBox}>
            <div className={styles.aiResponseHeader}>
              <SourceBadge kind={isAi ? 'ai' : 'source'} label={badgeLabel} size="sm" />
            </div>
            {error ? (
              <p className={styles.aiText} role="alert">
                Could not load a summary for this test. ({error})
              </p>
            ) : !explanation ? (
              <p className={styles.aiText} style={{ color: '#94a3b8', fontStyle: 'italic' }}>
                Loading the summary...
              </p>
            ) : (
              <p className={styles.aiText}>{explanation.text}</p>
            )}
          </div>

          <p className={styles.footerNote}>
            {isAi
              ? 'This summary was written by an AI model from the NASA record. Every number in it was checked against that record before it was shown. '
              : "This is NASA's own text for the test, shown unchanged. "}
            {sourceUrl ? (
              <a href={sourceUrl} target="_blank" rel="noopener noreferrer" style={{ color: '#38bdf8' }}>
                Open the NASA source
              </a>
            ) : (
              'No source link is recorded for this test.'
            )}
          </p>
        </div>

        <div className={styles.footer}>
          <button className={styles.actionBtn} onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default ExplainModal;
