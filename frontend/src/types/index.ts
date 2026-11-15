/**
 * Flame in Freefall - Core TypeScript Definitions
 * Strictly aligned with docs/data_schema.md and backend/models.py
 */

export interface TestRecord {
  id: string;
  investigation: string;
  investigation_id?: string | null;
  material: string | null;
  oxygen_pct: number | null;
  oxygen_context?: 'chamber_air' | 'burner_gas' | 'unknown';
  pressure_psi: number | null;
  airflow: string | null;
  result: string | null;
  conditions?: Record<string, string>;
  source_url: string | null;
}

export interface Habitat {
  name: string;
  oxygen_pct: number;
  pressure_psi: number;
  source?: string;
  description?: string;
  planetGif?: string;
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
