# Sources

Every link the team uses. Owner: Anumta. Add a row whenever you use a new source.

**Status meanings**
- **Opened:** someone on the team opened the page or file and confirmed it.
- **Search result:** the link came up in a search, but nobody has opened it yet.
- **Unchecked:** the link came from a friend's summary. Confirm it before using any number from it.

---

## Challenge

| Source | URL | Status |
|---|---|---|
| Flame in Freefall challenge page (scoring, objectives, habitat values, resources tab) | https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/ | Opened |

Resources tab: on the challenge page. Full data is released Friday 13 November.

---

## NASA data and papers

"Opened on" is the date someone last opened the link and checked it against what we use.

| Source | URL | Status | Opened on | Used for |
|---|---|---|---|---|
| PSI database (main data repository) | https://psi.nasa.gov/physci/repo/ | Opened | 14 Nov 2026 | Raw test data, Ayesh |
| PSI investigation PSI-10 (ACME / Flame Design) | https://psi.nasa.gov/physci/repo/data/investigations/PSI-10 | Opened | 14 Nov 2026 | Test records in tests.json |
| PSI investigation PSI-159 (ACME CFI-G) | https://psi.nasa.gov/physci/repo/data/investigations/PSI-159 | Opened | 14 Nov 2026 | Test records in tests.json |
| PSI investigation PSI-39 (CFI) | https://psi.nasa.gov/physci/repo/data/investigations/PSI-39 | Opened | 14 Nov 2026 | Test records in tests.json |
| PSI investigation PSI-69 (FLEX) | https://psi.nasa.gov/physci/repo/data/investigations/PSI-69 | Opened | 14 Nov 2026 | Test records in tests.json |
| PSI database guide (PDF) | https://science.nasa.gov/wp-content/uploads/2024/11/psi-database-guide.pdf | Unchecked | | How the data is organized |
| Saffire VI, ICES 2024 landing page (slide deck) | https://ntrs.nasa.gov/citations/20240007488 | Opened | 14 Nov 2026 | Record page for the presentation |
| Saffire VI, ICES 2024 presentation (PDF) | https://ntrs.nasa.gov/api/citations/20240007488/downloads/Saffire%20ICES%202024%20Saffire%20presentation072124small.pdf | Opened | 14 Nov 2026 | Sample records, test matrix, 981 s, CO2/CO limits |
| Spacecraft Fire Experiment overview (2016) | https://ntrs.nasa.gov/api/citations/20170001636/downloads/20170001636.pdf | Search result | | Background on the Saffire flight units |
| Saffire: A Novel Approach (2018) | https://ntrs.nasa.gov/citations/20180005168 | Search result | | Background on Saffire |
| Spacecraft Fire Safety Demonstration (2016) | https://ntrs.nasa.gov/citations/20160010292 | Search result | | Background on the Saffire goals |
| NASA-STD-6001B (flammability pass/fail rule), Historical copy approved 2011-08-26 | https://standards.nasa.gov/sites/default/files/standards/NASA/B-w/CHANGE-2/2/Historical/nasa-std-6001b.pdf | Opened | 14 Nov 2026 | The safety table's "Rule" cells |
| NASA-STD-6001B with Change 3 (2025), current version | https://standards.nasa.gov/sites/default/files/standards/NASA/B-w/CHANGE-3/3/2025_06_25_NASA-STD-6001B_w_Change_3_FINAL_Admin-Change-FINAL.pdf | Opened | 14 Nov 2026 | The safety table's "Rule" cells. Test 1 wording is unchanged from the Historical copy |
| NTRS (NASA Technical Reports Server) | https://ntrs.nasa.gov/ | Unchecked | | Finding papers |
| NTRS search API docs | https://ntrs.nasa.gov/api/openapi/ | Unchecked | | Automated paper search, if needed |
| NTRS harvesting guide | https://sti.nasa.gov/harvesting-data-from-ntrs/ | Unchecked | | Bulk download, if needed |

---

## NASA Spinoff (Earth-use strip)

| Source | URL | Status | Opened on | Used for |
|---|---|---|---|---|
| NASA Spinoff: Fire Detector (1978) | https://spinoff.nasa.gov/node/9407 | Opened | 14 Nov 2026 | Earth-use strip |
| NASA Spinoff: Fireman's Air Tanks (1976) | https://spinoff.nasa.gov/node/9582 | Opened | 14 Nov 2026 | Earth-use strip. Developed with Johnson Space Center; the page does not mention spacesuits |
| NASA Spinoff: New Technology for the Fire Attire (1982) | https://spinoff.nasa.gov/node/9918 | Opened | 14 Nov 2026 | Earth-use strip |

---

## Papers from the team's research summary

These came from a friend's summary. Open each one still marked Unchecked and confirm the numbers before using them.

| Source | Reference | Status | Opened on | Note |
|---|---|---|---|---|
| Saffire I–III results | https://ntrs.nasa.gov/citations/20170008805 | Opened | 14 Nov 2026 | ICES 2017 presentation "Results of Large-Scale Spacecraft Flammability Tests" (Saffire I–III). Its numbers are not used in the app data yet |
| Saffire VI results (full paper) | https://ntrs.nasa.gov/citations/20240002981 | Opened | 14 Nov 2026 | Full written conference paper ICES-2024-365, "Preliminary Results from the Saffire VI Experiment". 20240007488 is the slide deck of the same title presented at ICES 2024 |
| Exploration Atmosphere report (2010) | NASA, lunar sortie and lander atmospheres | Unchecked | | Oxygen and pressure for habitat values |
| Exploration Atmosphere | NTRS 20140000417 | Unchecked | | Habitat atmosphere values |
| Exploration Atmosphere | NTRS 20220015737 | Unchecked | | Habitat atmosphere values |
| Habitable Atmosphere | NASA OCHMO-TB-003 | Unchecked | | Earth and habitat atmosphere values |

Try the NTRS links directly as https://ntrs.nasa.gov/citations/<number>, for example https://ntrs.nasa.gov/citations/20170008805. If a link doesn't open, search for the title on NTRS.

---

## Where the files are stored

| Type | Location | Owner |
|---|---|---|
| Downloaded PDFs | `data/raw/papers/` | Ayesh |
| Downloaded PSI files | `data/raw/psi/` | Ayesh |
| Log of every downloaded file (name, URL, date) | `data/raw/README.md` | Ayesh |
| This file | `docs/sources.md` | Anumta |

---

## Rules

1. Every number in the app must trace to a row in this file.
2. Preliminary results must be labelled as preliminary.
3. If two sources disagree, record both and say which one is primary.