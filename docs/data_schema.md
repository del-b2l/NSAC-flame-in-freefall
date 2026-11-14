# Data schema

This file defines the shape of the data the app uses. The Python models in `backend/models.py` must match it exactly. If you change one, change the other in the same pull request.

## Test record

One record is one test: one row of a NASA test matrix, or one run of one experiment. Stored in `data/processed/tests.json` as a list of records.

| Field | Type | Required | Meaning | Example |
|---|---|---|---|---|
| `id` | string | yes | Unique ID: investigation and test number, lowercase, hyphens | `saffire-vi-3` |
| `investigation` | string | yes | Investigation name exactly as NASA writes it | `Saffire-VI` |
| `investigation_id` | string | yes | Investigation ID as in the PSI Data Repository | `PSI-102` |
| `material` | string or null | no | Sample material with size or thickness | `Two-sided PMMA, 1 cm thick, 18 cm` |
| `oxygen_pct` | number or null | no | Oxygen concentration, in mol % | `30.3` |
| `pressure_psi` | number or null | no | Total ambient pressure, in psi | `7.9` |
| `airflow` | string or null | no | Air speed and direction | `20 cm/s concurrent` |
| `result` | string or null | no | Short outcome, copied from the source | `Burn 780 s; O2-calorimetry total 1280 kJ` |
| `conditions` | object or {} | yes | Every other column from the source table, header text unchanged | {"Fuel": "Ethylene"}
| `source_url` | string or null | yes in practice | Link to the page or file the values came from | `https://ntrs.nasa.gov/citations/20240007488` |

### Rules

1. **Units.** Oxygen is always percent (mol %). Pressure is always psi. If the source gives kPa, convert it: psi = kPa × 0.145038. Airflow is always written with its unit, for example `cm/s`.
2. **Missing values are `null`.** Never guess, estimate, or copy a value from a different test.
3. **One record per test.** Do not merge tests. If a test has two conditions, make two records.
4. **Keep the source's wording** in `result` and `investigation`. Don't rewrite names.
5. **Always set `source_url`.** Every number on the dashboard must be traceable to it.
6. **Conflicts are noted, not resolved.** If two sources disagree, use the one from the primary paper and put the other value in the `result` field as a note.

### Example

```json
{
  "id": "saffire-vi-3",
  "investigation": "Saffire-VI",
  "material": "Two-sided PMMA, 1 cm thick, 18 cm",
  "oxygen_pct": 30.3,
  "pressure_psi": 7.9,
  "airflow": "20 cm/s concurrent, cut to 5 cm/s at 1120 s",
  "result": "Burn 780 s; O2-calorimetry total 1280 kJ; max temp 77 C at SFU outlet",
  "source_url": "https://ntrs.nasa.gov/citations/20240007488"
}
```

## Habitat

A habitat is one of the five settings a user can pick. Stored in `data/processed/habitats.json`.

| Field | Type | Meaning |
|---|---|---|
| `name` | string | Display name: Earth, Space station, Moon base, Rover, Spacesuit |
| `oxygen_pct` | number | Oxygen in mol % |
| `pressure_psi` | number | Pressure in psi |

### Starting values

| Name | oxygen_pct | pressure_psi | Source |
|---|---|---|---|
| Earth | 21 | 14.7 | Challenge page; NASA OCHMO-TB-003 |
| Space station | 21 | 14.7 | Same as Earth until a source says otherwise |
| Moon base | 30 | 10.2 | Challenge page ("30% or more", "10.2 psi or less") |
| Rover | 30 | 10.2 | Challenge page; same range as Moon base |
| Spacesuit | 100 | 4.3 | Challenge page |

Mark any value that isn't in a source with a comment in the PR. Don't invent new habitats.