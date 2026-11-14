/**
 * Flame in Freefall - Core TypeScript Definitions
 * Strictly aligned with docs/data_schema.md and backend/models.py
 */

export interface TestRecord {
  id: string;
  investigation: string;
  material: string | null;
  oxygen_pct: number | null;
  pressure_psi: number | null;
  airflow: string | null;
  result: string | null;
  source_url: string | null;
}

export interface Habitat {
  name: string;
  oxygen_pct: number;
  pressure_psi: number;
  source?: string;
  description?: string;
}

export type SourceBadgeKind = 'source' | 'ai';

export interface InvestigationInfo {
  name: string;
  cat: 'Prevent' | 'Detect' | 'Put out' | 'Related';
  fuels: string;
  hw: string;
  objective: string;
  sensors: string;
  sample: string;
  vars: string;
}
