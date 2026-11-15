/**
 * Live dashboard data: investigations, safety table and headline insight.
 *
 * The three endpoints are independent, so one failure must not blank the other
 * two. Errors are surfaced to the caller instead of being swallowed.
 */

import { useEffect, useState } from 'react';
import type { Insights, Investigation, SafetyTable } from '../types';
import { getInsights, getInvestigations, getSafetyTable } from './client';

export interface DashboardData {
  investigations: Investigation[] | null;
  safety: SafetyTable | null;
  insights: Insights | null;
  loading: boolean;
  error: string | null;
}

function reasonText(reason: unknown): string {
  if (reason instanceof Error) {
    return reason.message;
  }
  return String(reason);
}

export function useDashboardData(): DashboardData {
  const [investigations, setInvestigations] = useState<Investigation[] | null>(null);
  const [safety, setSafety] = useState<SafetyTable | null>(null);
  const [insights, setInsights] = useState<Insights | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    setLoading(true);
    setError(null);

    Promise.allSettled([getInvestigations(), getSafetyTable(), getInsights()]).then(
      ([invResult, safetyResult, insightResult]) => {
        if (cancelled) {
          return;
        }

        const failures: string[] = [];

        if (invResult.status === 'fulfilled') {
          setInvestigations(invResult.value);
        } else {
          failures.push(`/investigations: ${reasonText(invResult.reason)}`);
        }

        if (safetyResult.status === 'fulfilled') {
          setSafety(safetyResult.value);
        } else {
          failures.push(`/safety/table: ${reasonText(safetyResult.reason)}`);
        }

        if (insightResult.status === 'fulfilled') {
          setInsights(insightResult.value);
        } else {
          failures.push(`/insights: ${reasonText(insightResult.reason)}`);
        }

        setError(
          failures.length > 0
            ? `Could not load live dashboard data. ${failures.join(' · ')}`
            : null
        );
        setLoading(false);
      }
    );

    return () => {
      cancelled = true;
    };
  }, []);

  return { investigations, safety, insights, loading, error };
}
