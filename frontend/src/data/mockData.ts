/**
 * ISOLATED MOCK / FALLBACK DATA
 * Used for offline development and fallback if backend routes are unreachable.
 * Sourced directly from docs/data_schema.md and data/sample/sample_tests.json.
 */

import type { Habitat, TestRecord, InvestigationInfo } from '../types';

export const HABITATS: Habitat[] = [
  {
    name: 'Earth',
    oxygen_pct: 21.0,
    pressure_psi: 14.7,
    source: 'Challenge page; NASA OCHMO-TB-003',
    description: 'Standard sea-level terrestrial atmosphere',
  },
  {
    name: 'Space station',
    oxygen_pct: 21.0,
    pressure_psi: 14.7,
    source: 'Challenge page; NASA OCHMO-TB-003',
    description: 'ISS habitable volume atmosphere (matches Earth sea-level)',
  },
  {
    name: 'Moon base',
    oxygen_pct: 30.0,
    pressure_psi: 10.2,
    source: 'Challenge page (Exploration Atmosphere)',
    description: 'Reduced pressure, elevated oxygen to minimize EVA pre-breathe times',
  },
  {
    name: 'Rover',
    oxygen_pct: 30.0,
    pressure_psi: 10.2,
    source: 'Challenge page; Exploration Atmosphere',
    description: 'Pressurized planetary surface exploration vehicle',
  },
  {
    name: 'Spacesuit',
    oxygen_pct: 100.0,
    pressure_psi: 4.3,
    source: 'Challenge page (EMU / xEMU specs)',
    description: '100% pure oxygen at low pressure for mobility and flexibility',
  },
];

export const SAMPLE_TESTS: TestRecord[] = [
  {
    id: 'saffire-iv-1',
    investigation: 'Saffire-IV',
    material: 'SIBAL cloth, 50 cm',
    oxygen_pct: 22.0,
    pressure_psi: 14.5,
    airflow: '20 cm/s concurrent',
    result: 'Burn 130 s; total fuel-calorimetry heat release 409 kJ; max temp 45 C at SFU outlet, 25 C at FFD; CO2 rise 1390 ppm; CO rise 80 ppm',
    source_url: 'https://ntrs.nasa.gov/citations/20240007488',
  },
  {
    id: 'saffire-v-2',
    investigation: 'Saffire-V',
    material: 'Cotton jersey, 50 cm',
    oxygen_pct: 26.2,
    pressure_psi: 10.3,
    airflow: '20 cm/s concurrent',
    result: 'Burn 200 s; total fuel-calorimetry heat release 560 kJ; max temp 46 C at SFU outlet, 23 C at FFD; CO2 rise 2360 ppm; CO rise 83 ppm',
    source_url: 'https://ntrs.nasa.gov/citations/20240007488',
  },
  {
    id: 'saffire-vi-2',
    investigation: 'Saffire-VI',
    material: 'SIBAL cloth, 50 cm',
    oxygen_pct: 31.0,
    pressure_psi: 7.9,
    airflow: '20 cm/s concurrent',
    result: 'Burn 112 s; O2-calorimetry total 580 kJ (peak 3217 W); max temp 48 C at SFU outlet, 20 C at FFD; CO2 rise 2800 ppm; CO rise 120 ppm',
    source_url: 'https://ntrs.nasa.gov/citations/20240007488',
  },
  {
    id: 'saffire-vi-3',
    investigation: 'Saffire-VI',
    material: 'Two-sided PMMA, 1 cm thick, 18 cm',
    oxygen_pct: 30.3,
    pressure_psi: 7.9,
    airflow: '20 cm/s concurrent, cut to 5 cm/s at 1120 s',
    result: 'Burn 780 s; O2-calorimetry total 1280 kJ (peak 3080 W); max temp 77 C at SFU outlet, 21 C at FFD; CO2 rise 8539 ppm; CO rise 308 ppm',
    source_url: 'https://ntrs.nasa.gov/citations/20240007488',
  },
  {
    id: 'saffire-vi-4',
    investigation: 'Saffire-VI',
    material: 'One-sided PMMA, 0.5 cm thick, 18 cm',
    oxygen_pct: 28.8,
    pressure_psi: 8.0,
    airflow: '20 cm/s concurrent',
    result: 'Burn 1200 s; O2-calorimetry total 830 kJ (peak 1507 W); max temp 57 C at SFU outlet, 21 C at FFD; CO2 rise 8117 ppm; CO rise 320 ppm',
    source_url: 'https://ntrs.nasa.gov/citations/20240007488',
  },
];

export const MOCK_INVESTIGATIONS: InvestigationInfo[] = [
  {
    name: 'BASS / BASS-II',
    cat: 'Prevent',
    fuels: 'Solid and gaseous fuels',
    hw: 'Microgravity Science Glovebox (MSG), SPICE flow duct',
    objective: 'Which solid materials catch fire, and in what air',
    sensors: 'to fill from PSI',
    sample: 'to fill from PSI',
    vars: 'to fill from PSI',
  },
  {
    name: 'Saffire (I–III, VI)',
    cat: 'Prevent',
    fuels: 'Solid fuels (fabrics, plastics)',
    hw: 'Spacecraft cargo module (Saffire SFU)',
    objective: 'Fire behaviour in a realistic free-air spacecraft volume',
    sensors: 'Smoke and gas measurements (CO/CO2/calorimetry)',
    sample: 'Up to 50 cm samples (Saffire VI)',
    vars: 'Oxygen concentration, airflow, material, sample thickness',
  },
  {
    name: 'BRE (in ACME)',
    cat: 'Prevent',
    fuels: 'Materials, quiescent and low flow',
    hw: 'ACME in the CIR rack',
    objective: 'Materials flammability as a function of material properties',
    sensors: 'to fill from PSI',
    sample: 'to fill from PSI',
    vars: 'to fill from PSI',
  },
  {
    name: 'SAME / SAME-R',
    cat: 'Detect',
    fuels: 'Smoke and aerosols',
    hw: 'Smoke detection instruments',
    objective: 'How smoke particles behave and are measured in microgravity',
    sensors: 'Smoke detection instruments',
    sample: 'to fill from PSI',
    vars: 'to fill from PSI',
  },
  {
    name: 'DAFT / DAFT-2',
    cat: 'Detect',
    fuels: 'Dust',
    hw: 'Instrument reused from SAME/SAME-R',
    objective: 'Detect dust particles, using the SAME instrument',
    sensors: 'Dust detection instrument',
    sample: 'to fill from PSI',
    vars: 'to fill from PSI',
  },
  {
    name: 'FLEX',
    cat: 'Put out',
    fuels: 'Liquid droplets',
    hw: 'MDCA in the CIR rack',
    objective: 'What stops a flame: CO2 and helium dilution of the chamber',
    sensors: 'to fill from PSI',
    sample: 'to fill from PSI',
    vars: 'Diluent gases (CO2, helium)',
  },
];
