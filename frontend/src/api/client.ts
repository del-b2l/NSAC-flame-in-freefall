/**
 * Flame in Freefall - Typed API Client
 *
 * The backend owns the ranking (see docs/ranking_rule.md). This client sends
 * the chosen habitat and renders the order it gets back, untouched.
 */

import type {
  Habitat,
  Insights,
  Investigation,
  SafetyTable,
  TestRecord,
} from '../types';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

/**
 * Fetch all tests from GET /tests
 */
export async function getTests(): Promise<TestRecord[]> {
  const res = await fetch(`${BASE_URL}/tests`, {
    method: 'GET',
    headers: { Accept: 'application/json' },
  });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status} from /tests`);
  }
  const data = await res.json();
  if (!Array.isArray(data)) {
    throw new Error('/tests did not return a list of test records');
  }
  return data as TestRecord[];
}

/**
 * Rank tests for a chosen habitat via POST /rank.
 *
 * The API returns the records already ordered by the documented rule, so they
 * are never re-sorted here.
 */
export async function getRankedTests(habitat: Habitat): Promise<TestRecord[]> {
  const res = await fetch(`${BASE_URL}/rank`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify({ habitat: habitat.name }),
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => '');
    throw new Error(
      `HTTP ${res.status} from /rank${detail ? `: ${detail.slice(0, 200)}` : ''}`
    );
  }
  const data = await res.json();
  if (!Array.isArray(data)) {
    throw new Error('/rank did not return a list of test records');
  }
  return data as TestRecord[];
}

/**
 * Fetch the investigation catalogue from GET /investigations.
 */
export async function getInvestigations(): Promise<Investigation[]> {
  const res = await fetch(`${BASE_URL}/investigations`, {
    method: 'GET',
    headers: { Accept: 'application/json' },
  });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status} from /investigations`);
  }
  const data = await res.json();
  if (!Array.isArray(data)) {
    throw new Error('/investigations did not return a list');
  }
  return data as Investigation[];
}

/**
 * Fetch the nearest-test table from GET /safety/table.
 */
export async function getSafetyTable(): Promise<SafetyTable> {
  const res = await fetch(`${BASE_URL}/safety/table`, {
    method: 'GET',
    headers: { Accept: 'application/json' },
  });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status} from /safety/table`);
  }
  const data = await res.json();
  if (
    !data ||
    typeof data !== 'object' ||
    !Array.isArray(data.rows) ||
    !Array.isArray(data.habitats)
  ) {
    throw new Error('/safety/table did not return a table');
  }
  return data as SafetyTable;
}

/**
 * Fetch the headline insight from GET /insights.
 */
export async function getInsights(): Promise<Insights> {
  const res = await fetch(`${BASE_URL}/insights`, {
    method: 'GET',
    headers: { Accept: 'application/json' },
  });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status} from /insights`);
  }
  const data = await res.json();
  if (!data || typeof data !== 'object' || !data.key_finding) {
    throw new Error('/insights did not return a key finding');
  }
  return data as Insights;
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
