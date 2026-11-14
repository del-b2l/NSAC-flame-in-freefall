# Flame in Freefall: Team Tasks

## What we are building

A web page where someone picks a living place (Earth, a space station, a
Moon base, a rover, or a spacesuit). The page then shows NASA's past
fire experiments, sorted by how similar their air conditions are to that
place.

The experiments are real. NASA ran them in space to learn how fire
behaves in low gravity. We use their results. We do not run any
experiments.

Judging is on **Impact, Creativity, Validity** (are the numbers right
and sourced), **Relevance, and Presentation**.

**Challenge page:**
https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/

## Words you will see

-   **Oxygen %:** how much oxygen is in the air. Earth is about 21%.
-   **Pressure (psi):** how hard the air presses. Earth at sea level is
    14.7 psi.
-   **Investigation:** one NASA experiment, such as Saffire-VI.
-   **Saffire-VI:** a NASA experiment that burned material inside an
    unmanned spacecraft in orbit. Its results were published in 2024.
-   **Record:** one test, stored as one JSON entry (see
    `docs/data_schema.md`).
-   **PR (pull request):** how a change is proposed on GitHub and
    checked by a teammate before it goes into `main`.

## Folder tree

``` text
flame-in-freefall/
├── README.md                                how to run the project
├── docs/
│   ├── data_schema.md                       the shape of one test record and one habitat
│   ├── sources.md                           every link we use, and whether we have checked it
│   ├── ranking_rule.md                      how the habitat ranking works, in plain words
│   ├── scope.md                             the four features we are building (fixed Friday)
│   └── architecture.md                      how the pieces connect
├── data/
│   ├── raw/                                 files exactly as NASA provides them. Never edit.
│   │   ├── papers/                          PDFs from NASA
│   │   ├── psi/                             PSI database files, one folder per investigation
│   │   └── README.md                        log of every raw file: name, source link, date downloaded
│   ├── processed/                           cleaned files the app reads
│   │   ├── tests.json                       all test records
│   │   └── habitats.json                    the five habitats
│   ├── sample/
│   │   └── sample_tests.json                five test records for development
│   └── scripts/
│       └── build_tests.py                   turns raw files into tests.json
├── backend/                                 Python server (FastAPI)
│   ├── main.py                              the routes the frontend calls
│   ├── models.py                            the shape of a test and a habitat
│   ├── data_loader.py                       reads the JSON files
│   ├── ranking.py                           sorts tests by closeness to a habitat
│   ├── requirements.txt                     Python packages
│   └── tests/
│       └── test_ranking.py                  tests for ranking.py
├── frontend/                                web page (React + Vite)
│   └── src/
│       ├── App.tsx                           puts the page together
│       ├── App.css                           layout and colours
│       └── components/
│           ├── HabitatPicker.tsx             the five habitat buttons
│           ├── TestList.tsx                  the ranked list of tests
│           └── SafetyTable.tsx               the safety table
└── rag/                                     placeholder for a search feature (not needed for the hackathon)
```

**Important:** Do not edit anything in `data/raw/`. Only Ayesh adds
files there.

## The docs/ files

  ------------------------------------------------------------------------------
  File                     What it says      Owner             Done by
  ------------------------ ----------------- ----------------- -----------------
  `docs/data_schema.md`    Fields of a test  Batool            Thursday
                           record and a                        
                           habitat                             

  `docs/sources.md`        Every link and    Anumta            Thursday
                           whether it has                      
                           been checked                        

  `docs/ranking_rule.md`   How tests are     Shaheer           Thursday (rule),
                           sorted, and the                     Friday (airflow)
                           sentence shown on                   
                           screen                              

  `docs/scope.md`          The four features Batool            Friday 8 pm
                           we build, and                       
                           what is out                         

  `docs/architecture.md`   How the pieces    Batool            Thursday
                           connect                             
  ------------------------------------------------------------------------------

## Data you can use right now

These are available before Friday. Nothing is final until the official
resources come out on Friday 13 November.

  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Data              Where it is                                                                                                  What it is           Who uses it
  ----------------- ------------------------------------------------------------------------------------------------------------ -------------------- -----------------
  Five sample test  `data/sample/sample_tests.json`                                                                              Real numbers from    Ayesh, Shaheer,
  records                                                                                                                        the Saffire VI       Muntaha
                                                                                                                                 presentation, for    
                                                                                                                                 development only     

  The data schema   `docs/data_schema.md`                                                                                        The field names,     Everyone
                                                                                                                                 units, and rules     
                                                                                                                                 every record follows 

  Habitat values    `docs/data_schema.md`, Habitat section                                                                       Oxygen and pressure  Shaheer, Muntaha
                                                                                                                                 for each habitat,    
                                                                                                                                 from the challenge   
                                                                                                                                 page                 

  Saffire VI        Link in `docs/sources.md`                                                                                    NASA's slides, the   Ayesh, Anumta
  presentation                                                                                                                   source of the sample 
                                                                                                                                 records and the      
                                                                                                                                 981-second fact      

  Challenge page    https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/                                        The official brief   Batool, Anumta
                                                                                                                                 and the Resources    
                                                                                                                                 tab (full data       
                                                                                                                                 released Friday)     

  PSI database      https://psi.nasa.gov/physci/repo/                                                                            NASA's full test     Ayesh
                                                                                                                                 database. Browse     
                                                                                                                                 now, download Friday 

  PSI database      https://science.nasa.gov/wp-content/uploads/2024/11/psi-database-guide.pdf                                   Explains how the PSI Ayesh
  guide                                                                                                                          files are organised  

  NASA-STD-6001B    https://standards.nasa.gov/sites/default/files/standards/NASA/B-w/CHANGE-2/2/Historical/nasa-std-6001b.pdf   NASA's pass/fail     Batool, Anumta
                                                                                                                                 rule for             
                                                                                                                                 flammability. Source 
                                                                                                                                 for the "Rule" cells 
                                                                                                                                 in the safety table  

  Saffire I--III    https://ntrs.nasa.gov/citations/20170008805                                                                  Earlier Saffire      Ayesh
  results (NTRS                                                                                                                  experiments:         
  20170008805)                                                                                                                   cotton-fiberglass,   
                                                                                                                                 silicone and Nomex   
                                                                                                                                 results. Not yet     
                                                                                                                                 opened, so do not    
                                                                                                                                 use its numbers      
                                                                                                                                 until checked        

  Saffire 2016      https://ntrs.nasa.gov/api/citations/20170001636/downloads/20170001636.pdf                                    Background on the    Ayesh, Anumta
  overview (NTRS                                                                                                                 Saffire flight       
  20170001636)                                                                                                                   units. Background    
                                                                                                                                 reading only         
  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------

Every link above, and its status, is in `docs/sources.md`.

## Tasks by person

### Batool (lead)

**General:** keeps the project working. Sets the rules, reviews every
change, and merges it into `main`.

-   **Thursday:** finish the backend routes (`main.py`). Agree the data
    schema with the team. Merge the skeleton.
-   **Friday:** switch the backend to read `tests.json` once Ayesh has
    made it. Write `docs/scope.md`.
-   **Saturday:** build `SafetyTable.tsx`. Each "Rule" cell cites
    NASA-STD-6001B (link in the data table above). Review and merge
    every change that day.
-   **Sunday:** check `main` runs from a clean clone. Write the README
    run steps. Submit.

**Data you can use now:** the schema, the habitat values, and the sample
records.

### Ayesh (data)

**General:** turns NASA's raw files into the data the app reads. Makes
sure every number has a source.

-   **Thursday:** save the sample records and the Saffire VI
    presentation into the repo. Write `data/raw/README.md`. Check the
    JSON file opens without errors.
-   **Friday:** download the official files from the challenge page's
    Resources tab into `data/raw/`. Log each one. Write `build_tests.py`
    and produce `tests.json`.
-   **Saturday:** fix wrong or missing values that people flag. Write 2
    or 3 demo answers as a backup in case the internet fails during the
    demo.
-   **Sunday:** record a backup demo video. Check that every number on
    screen has a source.

**Data you can use now:**

-   Saffire VI presentation:
    https://ntrs.nasa.gov/api/citations/20240007488/downloads/Saffire%20ICES%202024%20Saffire%20presentation072124small.pdf\
    The slides show the test table (Section "Test Matrix") and the heat
    release results. Read these first.
-   PSI database guide, which explains the NASA data format:
    https://science.nasa.gov/wp-content/uploads/2024/11/psi-database-guide.pdf
-   PSI database, where the full data lives:
    https://psi.nasa.gov/physci/repo/ (browse, don't download yet)
-   Saffire I--III results: https://ntrs.nasa.gov/citations/20170008805
    (not opened yet. Open it on Thursday and mark its status in
    `docs/sources.md`. Don't use its numbers until you have checked them
    against the paper)
-   Saffire VI results paper: our search found
    https://ntrs.nasa.gov/citations/20240007488 but the friend's summary
    gives 20240002981. Check which one is the full results paper, and
    record it in `docs/sources.md`.

### Shaheer (ranking)

**General:** writes the logic that sorts tests by how close their
conditions are to a chosen habitat.

-   **Thursday:** write `docs/ranking_rule.md` in plain words. Write
    `ranking.py` so that it sorts a list of tests by oxygen and
    pressure, closest first. Add one test to `test_ranking.py`.
-   **Friday:** add airflow to the sort. Test it against the real data
    from `tests.json`. Write one sentence describing the rule for
    Muntaha to show on screen.
-   **Saturday:** test edge cases: a test with missing airflow, a test
    with missing pressure. Write a short paragraph on the ranking for
    the slides.
-   **Sunday:** check the code matches the sentence on screen. Prepare a
    two-minute explanation for the presentation.

**Data you can use now:** the sample records, the habitat values, and
the schema.

### Muntaha (frontend)

**General:** builds the screens users see. Starts with fake data and
switches to real data on Friday.

-   **Thursday:** set up the frontend (run `npm install` and
    `npm run dev` in `frontend/`). Make `HabitatPicker.tsx` show five
    buttons. Make `TestList.tsx` show three hard-coded test names.
-   **Friday:** connect `TestList.tsx` to the backend route `/tests`.
    Connect `HabitatPicker.tsx` to `/rank`. Show Shaheer's ranking
    sentence on the screen.
-   **Saturday:** add the safety table, using Batool's
    `SafetyTable.tsx`. Check the page on a laptop and on a projector.
    Fix any red errors in the browser console.
-   **Sunday:** run the final check on the projector setting. Prepare a
    two-minute walkthrough of the page.

**Data you can use now:** the habitat names and the sample records. You
don't need any data to start Thursday's work.

### Anumta (layout and content)

**General:** makes the page look clear, fills in the three tabs, and
builds the slides. Lighter workload than the others.

-   **Thursday:** add a header and three empty sections in `App.css`,
    labelled Prevent, Detect, and Put out. Remove the unused Vite
    template files. Read `docs/sources.md` and check each link's status.
    Open NASA-STD-6001B and copy its pass/fail rule into your notes,
    because the safety table cites it.
-   **Friday:** fill in the three tabs with these NASA experiments:
    -   **Prevent:** BASS, BASS-II, Saffire, BRE (testing which
        materials catch fire)
    -   **Detect:** SAME, SAME-R, DAFT (testing how smoke is noticed)
    -   **Put out:** FLEX (testing what stops a flame)

    Add the 981-second card (see below).
-   **Saturday:** add the Earth-use strip: water-mist extinguishers,
    better smoke detectors, and firefighter gear. The challenge page
    describes these. Start the slides, with the five judging criteria as
    section titles.
-   **Sunday:** finish the slides, with a source line under every
    number. Export them as a PDF and post them in the group chat.

**The 981-second card.** Use this text, which comes from the Saffire VI
presentation:

> "In Saffire VI, the smoke was readily detected at 981 seconds, after
> most of the hazardous gas release had already happened."

**Data you can use now:** the challenge page, the Saffire VI
presentation (for the 981-second fact), and `docs/sources.md`.

## Schedule at a glance

  ----------------------------------------------------------------------------------------------
  Day        Goal        Batool          Ayesh          Shaheer       Muntaha       Anumta
  ---------- ----------- --------------- -------------- ------------- ------------- ------------
  Thu 12 Nov Skeleton    Backend routes, Sample data    Ranking stub  Two           Layout and
             runs with   merge           and raw README and test      components on check
             sample data                                              screen        sources

  Fri 13 Nov Real data   Switch to       Official       Airflow in    Live data on  Three tabs
             loaded      `tests.json`,   files,         ranking       screen        and
                         scope           `tests.json`                               981-second
                                                                                    card

  Sat 14 Nov Four        Safety table,   Fix data, demo Edge cases,   Safety table, Earth-use
             features    merge           backup         ranking       layout        strip,
             work                                       paragraph                   slides

  Sun 15 Nov Submitted   Final review,   Demo video     Final check,  Final check,  Finish
                         submit                         explanation   walkthrough   slides,
                                                                                    export
  ----------------------------------------------------------------------------------------------

**Code freeze:** Saturday 8 pm. Stop merging at least 3 hours before the
deadline on Sunday. Confirm the exact deadline on the event page.

## Rules for everyone

-   Work on your own branch, named `feature/<task>`. Never push to
    `main` directly.
-   Open a pull request when your task is ready. One other team member
    reviews it, and Batool merges it.
-   Don't commit `.env` files, API keys, `.venv/`, or `node_modules/`.
-   Only edit the files in your section. For anything else, ask the
    owner first.
-   Post a short daily update in the group chat: what you finished, what
    you're doing next, and what's blocking you.
