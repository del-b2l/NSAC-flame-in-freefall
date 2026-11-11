# Ranking rule

## In plain words

When a user picks a habitat, every NASA test is sorted so that the tests with conditions closest to that habitat appear first.

"Closest" means two things are compared: oxygen % and pressure (psi). A test whose oxygen and pressure are near the habitat's values ranks higher than one that is far away.

Airflow is added on Friday, once the official data is in.

## Provisional rule (Shaheer confirms the exact numbers on Thursday)

For each test:

1. Oxygen difference = the test's oxygen % minus the habitat's oxygen %, as a positive number.
2. Pressure difference = the test's pressure in psi minus the habitat's pressure in psi, as a positive number.
3. Distance = oxygen difference + pressure difference.
4. Sort by distance, smallest first. Smallest distance means the best match, so it goes at the top.

Example, with the Moon base habitat (oxygen 30%, pressure 10.2 psi) and the Saffire VI-3 test (oxygen 30.3%, pressure 7.9 psi):

- Oxygen difference: 0.3
- Pressure difference: 2.3
- Distance: 2.6

## Rules for missing values

- A test with no oxygen value or no pressure value is not dropped. It is placed at the bottom, after every test that has both values.
- Never guess a missing value to make a test rank higher.

## Text shown on the dashboard

This sentence appears on screen next to the ranked list. Muntaha copies it exactly:

"Tests score higher when their oxygen and pressure are closer to this habitat."