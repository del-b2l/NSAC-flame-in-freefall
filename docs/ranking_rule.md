# Ranking rules

There are two ranking methods in this project:

- **Original ranking (`rank_tests`)** — owned by Shaheer, implemented in
  `backend/ranking.py`, and used by the `/rank` endpoint. It ranks tests by
  oxygen and pressure distance, with airflow as a tie-breaker.
- **Tier-based ranking (`rank_tests_by_tier`)** — used by the `/brief`
  endpoint. It prioritises tests according to how many measurements are
  available.

These methods serve different purposes. Changes to one should not silently
change the behaviour of the other.

## Tier-based ranking for `/brief`

When a user selects a habitat, tests are grouped into three tiers according
to the availability of their oxygen and pressure measurements.

- **Tier 1:** Both oxygen and pressure are available.
- **Tier 2:** Only one measurement is available.
- **Tier 3:** Neither measurement is available.

Within each tier, tests with the smallest available distance appear first.
Tests are never given invented or inferred measurement values.

## The rule

For each test:

1. **Oxygen gap** = the test's oxygen % minus the habitat's oxygen %, as a
   positive number.
2. **Pressure gap** = the test's pressure in psi minus the habitat's pressure
   in psi, as a positive number.
3. **Distance** = oxygen gap + pressure gap. One mol % of oxygen counts exactly
   the same as one psi of pressure.
4. **Sort** by distance, smallest first. The smallest distance is the best
   match, so it goes at the top.

Units are used exactly as NASA reports them (mol % and psi). Nothing is
normalised, weighted, or rescaled, so every number on screen can be checked by
hand against the source.

### Worked example

Moon base habitat (oxygen 30%, pressure 10.2 psi) and the Saffire VI-3 test
(oxygen 30.3%, pressure 7.9 psi):

- Oxygen gap: 0.3
- Pressure gap: 2.3
- Distance: **2.6**

That 2.6 is the closest any Saffire fire test gets to a Moon base, and it is
15th of the 994 records. The 14 ahead of it are FLEX droplet tests that NASA
ran at 30% oxygen and 10.2–10.5 psi, which is almost exactly Moon-base air, so
they score 0.13 to 0.46. That is the ranking doing its job, not an error.

### The order this produces today

Real records from `data/processed/tests.json` (994 records), nearest first:

| Habitat | First five |
|---|---|
| Earth | `cfi-1206` (0.00) → `cfi-1207` (0.00) → `cfi-1208` (0.00) → `cfi-1209` (0.00) → `cfi-1210` (0.00) |
| Space station | same as Earth |
| Moon base | `flex-219f001` (0.13) → `flex-223f002` (0.14) → `flex-219r001` (0.15) → `flex-223f001` (0.15) → `flex-191r001` (0.19) |
| Rover | same as Moon base |
| Spacesuit | `acme-fd-inverse-21349a1` (16.96) → `acme-fd-inverse-21349b1` (16.99) → `acme-fd-inverse-22024g1` (18.09) → `acme-fd-inverse-22024h1` (18.11) → `acme-fd-inverse-22035j1` (18.12) |

The Earth row is a five-way tie at distance 0.00: CFI ran at 21% oxygen and
1 atm, so `id` decides the order. Many FLEX tests share the same ambient
conditions, which is why ties are common and why the last tie-break has to be
stable.

The Spacesuit row is not a mistake. No NASA test burned material in 100%
oxygen, so every distance there is above 16 and "closest" means "least far",
not "similar".

## Airflow

Airflow is **not** part of the distance. It is a tie-break.

NASA does not publish an airflow figure for Earth, the space station, a Moon
base, a rover, or a spacesuit, and `data/processed/habitats.json` has no
airflow field. Adding one would mean inventing five numbers, which breaks the
schema rule "Missing values are `null`. Never guess" and would cost us marks on
Validity for no gain.

So airflow is used where it is honest to use it:

- Two tests whose distances fall in the same **half-unit band** (0.5 wide) are
  treated as equally close.
- Inside that band, a test with a recorded airflow ranks above one without,
  because the source actually documented its air movement.
- A blank or whitespace-only `airflow` counts as missing.
- Airflow never outranks a test that is further away by 0.5 or more.

Airflow is free text (`20 cm/s concurrent, cut to 5 cm/s at 1120 s`), so it is
shown to the user as written and never parsed into a number.

## Where the data comes from

`data/processed/tests.json` holds 994 records built by
`data/scripts/build_tests.py`:

| Source | Records | Oxygen and pressure from |
|---|---|---|
| CFI-G, normal flames (PSI-159) | 179 | `XO2 before test` (mole fraction), `approx p` (bar) |
| CFI-G, inverse flames (PSI-159) | 154 | `XO2`, `approx p` (bar) |
| CFI (PSI-39) | 87 | `Oxygen` (mole fraction), `Pressure` (`1 atm`) |
| ACME / Flame Design, normal (PSI-10) | 187 | `XO2 (init)`, `pmean (atm)` |
| ACME / Flame Design, inverse (PSI-10) | 109 | `XO2`, `pmean (atm)` |
| FLEX (PSI-69) | 273 | `O initial ambient composition`, `Ambient pressure; mmHg` |
| Saffire IV–VI | 5 | hand-transcribed from the NTRS paper |

Every row in the PSI tables is one test. A row is only shipped when it has a
numeric oxygen value, a numeric pressure and a source link; 893 rows were
dropped because the table leaves one of those blank (mostly inverse-flame rows
with no oxygen). The counts and reasons are printed by
`python data/scripts/build_tests.py --dry-run`, and `data/raw/README.md` logs
the files and their hashes.

## Rules for missing values

- A test with no oxygen value or no pressure value keeps its place in the list:
  it goes at the bottom, after every test that has both.
- Its distance is not computed, and no value is inferred from another test or
  from the habitat.
- Two tests that both lack oxygen or pressure are ordered by `id`, so the order
  never changes between requests.

## Ties

After distance, the remaining tie-breaks are: recorded airflow, then `id`.
Two identical requests therefore always return the same order, which keeps the
screen stable and the tests repeatable.

## Text shown on the dashboard

This sentence appears on screen next to the ranked list. Muntaha copies it
exactly, and it must not change without telling her:

> "Tests score higher when their oxygen and pressure are closer to this habitat."

The sentence stays true while airflow is only a tie-break, so it does not need
to mention airflow.

## For the slides (one paragraph)

> We sort NASA's fire tests by how close their air is to the habitat the user
> picked. For each test we measure two gaps: oxygen, in mol %, and pressure, in
> psi. We add them, and the smallest total goes first. A Moon base runs at 30%
> oxygen and 10.2 psi, so a FLEX droplet test at 30% and 10.33 psi scores 0.13
> and tops that list, and Saffire VI-3, at 30.3% and 7.9 psi, scores 2.6 as the
> closest Saffire fire test. We do not invent numbers: a test missing oxygen or
> pressure is shown at the bottom rather than guessed, and airflow only breaks
> near-ties because NASA never published airflow for these habitats.
>
> Everything is traceable: 994 records, each one linked to the NASA table it
> came from, built by a script that refuses to emit a row without a source.

## Two-minute explanation (Sunday)

1. **What the page does.** Pick a habitat; the list re-sorts by how similar each
   NASA test's air was.
2. **The measurement.** Two gaps, absolute values, added. Units as published,
   no weights, so anyone can check a row by hand.
3. **Why it is valid.** Every number comes from a source link in the record. No
   normalisation, no model, no inference.
4. **The honest limitation.** Nothing burned at 100% oxygen, so the Spacesuit
   ranking is "least far", not "similar" — and we say so on screen.
5. **Airflow.** NASA gives no habitat airflow figure, so it is a tie-break, not
   a fake third axis.
6. **Missing data.** Kept and ranked last; `data/sample/edge_cases.json` holds
   two sample rows that exercise exactly that path, and the tests check them.

## How this was checked

```
python -m pytest backend/tests data/tests -q   # 66 passed
python data/scripts/build_tests.py --check     # data/processed/tests.json is up to date
```

That is 66 tests: the ranking rule with synthetic records, the unit converters
with inline values, and the shipped dataset (unique ids, a source link on every
record, oxygen and pressure inside plausible ranges, five records pinned to
hand-checked rows). Last run: Saturday 14 November 2026.
