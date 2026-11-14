/**
 * Flame in Freefall - Typed API Client
 * Centralized API service with offline fallbacks.
 */

import type { Habitat, TestRecord } from '../types';
import { SAMPLE_TESTS } from '../data/mockData';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

/**
 * Calculates distance following Shaheer's rule in docs/ranking_rule.md:
 * Distance = |oxygen_pct - hab.oxygen_pct| + |pressure_psi - hab.pressure_psi|
 * Tests with null oxygen or pressure are placed at the bottom.
 */
export function calculateCloseness(test: TestRecord, habitat: Habitat): number {
  if (test.oxygen_pct == null || test.pressure_psi == null) {
    return Number.POSITIVE_INFINITY;
  }
  return (
    Math.abs(test.oxygen_pct - habitat.oxygen_pct) +
    Math.abs(test.pressure_psi - habitat.pressure_psi)
  );
}

/**
 * Client-side ranking fallback when backend ranking is pending or unavailable.
 */
export function rankTestsLocally(tests: TestRecord[], habitat: Habitat): TestRecord[] {
  return [...tests].sort((a, b) => {
    const distA = calculateCloseness(a, habitat);
    const distB = calculateCloseness(b, habitat);
    return distA - distB;
  });
}

/**
 * Fetch all tests from GET /tests
 */
export async function getTests(): Promise<TestRecord[]> {
  try {
    const res = await fetch(`${BASE_URL}/tests`, {
      method: 'GET',
      headers: { Accept: 'application/json' },
    });
    if (!res.ok) {
      throw new Error(`HTTP error ${res.status}`);
    }
    const data = await res.json();
    if (Array.isArray(data) && data.length > 0) {
      return data;
    }
    return SAMPLE_TESTS;
  } catch (err) {
    console.warn('Backend /tests unavailable, falling back to sample tests:', err);
    return SAMPLE_TESTS;
  }
}

/**
 * Rank tests for a chosen habitat via POST /rank
 */
export async function getRankedTests(habitat: Habitat): Promise<TestRecord[]> {
  try {
    const res = await fetch(`${BASE_URL}/rank`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify({
        name: habitat.name,
        oxygen_pct: habitat.oxygen_pct,
        pressure_psi: habitat.pressure_psi,
      }),
    });
    if (!res.ok) {
      throw new Error(`HTTP error ${res.status}`);
    }
    const data = await res.json();
    if (Array.isArray(data) && data.length > 0) {
      // If backend returned unranked items (Shaheer's TODO), apply local sorting
      // so the UI always accurately reflects Shaheer's ranking rule.
      return rankTestsLocally(data, habitat);
    }
    return rankTestsLocally(SAMPLE_TESTS, habitat);
  } catch (err) {
    console.warn('Backend /rank unavailable, applying local ranking with sample data:', err);
    return rankTestsLocally(SAMPLE_TESTS, habitat);
  }
}

/**
 * AI Explanation placeholder function.
 * Marked as AI-generated; will connect to Gemini / RAG endpoint in future.
 */
export async function fetchAiExplanation(
  test: TestRecord,
  habitat: Habitat
): Promise<{ explanation: string; generatedAt: string }> {
  // Simulating async call for AI generation
  await new Promise((resolve) => setTimeout(resolve, 350));

  const oxyDiff = test.oxygen_pct != null
    ? (test.oxygen_pct - habitat.oxygen_pct).toFixed(1)
    : 'unknown';
  const psiDiff = test.pressure_psi != null
    ? (test.pressure_psi - habitat.pressure_psi).toFixed(1)
    : 'unknown';

  return {
    explanation:
      `[AI Synthesis] In this microgravity run (${test.investigation}, ${test.id}), ` +
      `the sample (${test.material ?? 'unspecified material'}) burned under ${test.oxygen_pct ?? 'N/A'}% O2 ` +
      `and ${test.pressure_psi ?? 'N/A'} psi. Compared to ${habitat.name} (${habitat.oxygen_pct}% O2, ` +
      `${habitat.pressure_psi} psi), the test environment had an oxygen delta of ${oxyDiff}% and pressure ` +
      `delta of ${psiDiff} psi. Primary flame propagation and thermal release indicate that in low-flow ` +
      `conditions (${test.airflow ?? 'quiescent'}), toxic gaseous buildup (CO/CO2) precedes visible thermal flareups.`,
    generatedAt: new Date().toISOString(),
  };
}
