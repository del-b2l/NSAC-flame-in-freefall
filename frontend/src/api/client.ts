/**
 * Flame in Freefall - Typed API Client
 *
 * The backend owns the ranking (see docs/ranking_rule.md). This client sends
 * the chosen habitat and renders the order it gets back, untouched.
 */

import type {
  Brief,
  EarthUse,
  Explanation,
  Habitat,
  HardwareGroups,
  Insights,
  Investigation,
  QaAnswer,
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
 * Send one request and return its JSON body, or throw with the status.
 */
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers: { Accept: 'application/json', ...(init?.headers ?? {}) },
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => '');
    throw new Error(`HTTP ${res.status} from ${path}${detail ? `: ${detail.slice(0, 200)}` : ''}`);
  }
  return (await res.json()) as T;
}

/**
 * Fetch the five habitats, with their status and source, from GET /habitats.
 */
export async function getHabitats(): Promise<Habitat[]> {
  const data = await request<Habitat[]>('/habitats');
  if (!Array.isArray(data)) {
    throw new Error('/habitats did not return a list');
  }
  return data;
}

/**
 * Fetch investigations grouped by hardware family from GET /hardware.
 */
export function getHardware(): Promise<HardwareGroups> {
  return request<HardwareGroups>('/hardware');
}

/**
 * Fetch the Earth-use notes from GET /earth-use.
 */
export function getEarthUse(): Promise<EarthUse> {
  return request<EarthUse>('/earth-use');
}

/**
 * Fetch the one-page brief for a habitat from GET /brief.
 */
export function getBrief(habitatName: string): Promise<Brief> {
  return request<Brief>(`/brief?habitat=${encodeURIComponent(habitatName)}`);
}

/**
 * Ask the backend for a short summary of one test via POST /explain/{test_id}.
 *
 * The backend checks every number against the record and falls back to NASA's
 * own text, so nothing is written or reworded in the browser.
 */
export function explainTest(testId: string): Promise<Explanation> {
  return request<Explanation>(`/explain/${encodeURIComponent(testId)}`, { method: 'POST' });
}

/**
 * Ask a free-text question via POST /qa. The answer cites the records it used.
 */
export function askQuestion(question: string, habitatName?: string): Promise<QaAnswer> {
  return request<QaAnswer>('/qa', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, habitat: habitatName ?? null }),
  });
}

/**
 * Fetch the example questions that have saved answers from GET /qa/examples.
 */
export function getQaExamples(): Promise<string[]> {
  return request<string[]>('/qa/examples');
}
