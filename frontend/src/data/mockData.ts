/**
 * Habitat atmospheres used by the picker.
 *
 * Values mirror the challenge page and NASA OCHMO-TB-003 and are the same
 * numbers the backend serves from GET /habitats. They are reference constants,
 * not fallback data: the ranked test list and every dashboard section come from
 * the API.
 */

import type { Habitat } from '../types';

export const HABITATS: Habitat[] = [
  {
    name: 'Earth',
    oxygen_pct: 21.0,
    pressure_psi: 14.7,
    source: 'Challenge page; NASA OCHMO-TB-003',
    description: 'Standard sea-level terrestrial atmosphere',
    planetGif: '/assets/planets/earth_spin.gif',
  },
  {
    name: 'Space station',
    oxygen_pct: 21.0,
    pressure_psi: 14.7,
    source: 'Challenge page; NASA OCHMO-TB-003',
    description: 'ISS habitable volume atmosphere (matches Earth sea-level)',
    planetGif: '/assets/planets/station_spin.gif',
  },
  {
    name: 'Moon base',
    oxygen_pct: 30.0,
    pressure_psi: 10.2,
    source: 'Challenge page (Exploration Atmosphere)',
    description: 'Reduced pressure, elevated oxygen to minimize EVA pre-breathe times',
    planetGif: '/assets/planets/moon_spin.gif',
  },
  {
    name: 'Rover',
    oxygen_pct: 30.0,
    pressure_psi: 10.2,
    source: 'Challenge page; Exploration Atmosphere',
    description: 'Pressurized planetary surface exploration vehicle',
    planetGif: '/assets/planets/rover_spin.gif',
  },
  {
    name: 'Spacesuit',
    oxygen_pct: 100.0,
    pressure_psi: 4.3,
    source: 'Challenge page (EMU / xEMU specs)',
    description: '100% pure oxygen at low pressure for mobility and flexibility',
    planetGif: '/assets/planets/spacesuit_spin.gif',
  },
];
