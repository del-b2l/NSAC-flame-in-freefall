/**
 * Habitat atmospheres used to draw the picker before GET /habitats answers.
 *
 * The numbers match data/processed/habitats.json. The backend response replaces
 * them and adds each habitat's status, note and source link; only the planet
 * artwork is kept from here.
 */

import type { Habitat } from '../types';

export const HABITATS: Habitat[] = [
  { name: 'Earth', oxygen_pct: 21.0, pressure_psi: 14.7, planetGif: '/assets/planets/earth_spin.gif' },
  { name: 'Space station', oxygen_pct: 21.0, pressure_psi: 14.7, planetGif: '/assets/planets/station_spin.gif' },
  { name: 'Moon base', oxygen_pct: 30.0, pressure_psi: 10.2, planetGif: '/assets/planets/moon_spin.gif' },
  { name: 'Rover', oxygen_pct: 30.0, pressure_psi: 10.2, planetGif: '/assets/planets/rover_spin.gif' },
  { name: 'Spacesuit', oxygen_pct: 100.0, pressure_psi: 4.3, planetGif: '/assets/planets/spacesuit_spin.gif' },
];
