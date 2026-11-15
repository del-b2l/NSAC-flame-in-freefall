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

/**
 * An investigation as served by GET /investigations.
 *
 * Optional fields are `null` when the source does not record them. The UI must
 * show that honestly ("Not recorded") rather than inventing a value.
 */
export interface Investigation {
  id: string;
  name: string;
  acronym: string | null;
  category: string | null;
  type: string | null;
  doi: string | null;
  landing_url: string | null;
  fuels: string | null;
  hardware: string | null;
  hardware_family: string | null;
  objective: string | null;
  sample_size: string | null;
  sensors: string | null;
  variables: string | null;
  earth_benefits: string[] | null;
  related_investigations: string[] | null;
}

/** One row of the safety table, as served by GET /safety/table. */
export interface SafetyTest {
  test_id: string;
  oxygen_pct: number | null;
  pressure_psi: number | null;
  result: string | null;
  source_url: string | null;
}

export type SafetyCellState = 'tested' | 'rule' | 'missing';

export interface SafetyCell {
  habitat: string;
  state: SafetyCellState;
  nearest_test: SafetyTest | null;
  oxygen_gap?: number;
  pressure_gap?: number;
  distance?: number;
  /** Present only when the safety rules file has been read (rules_read). */
  rule?: string;
}

export interface SafetyRow {
  material: string;
  cells: SafetyCell[];
}

export interface SafetyTable {
  habitats: string[];
  rows: SafetyRow[];
  rules_read: boolean;
}

/** Headline insight, as served by GET /insights. */
export interface KeyFinding {
  title: string;
  text: string;
  source_label: string;
  source_url: string;
  status: string;
}

export interface InsightCard {
  text: string;
  source_label: string;
  source_url: string;
}

export interface ControlNeed {
  text: string;
  status: string;
  basis_url: string;
}

export interface Insights {
  key_finding: KeyFinding;
  gaps: InsightCard[];
  control_need: ControlNeed;
}
