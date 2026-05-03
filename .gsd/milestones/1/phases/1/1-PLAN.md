---
phase: 1
plan: 1
wave: 1
---

# Plan 1.1: Local Scraper Implementation

## Objective
Establish the core logic for the project by building a Python script that scrapes the USD/COP exchange rate (TRM) and the associated date from `dolar-colombia.com`.

## Context
- .gsd/SPEC.md
- Selector (TRM): `span.exchange-rate`
- Selector (Date): `input.input-datepicker` (attribute: `value`)

## Tasks

<task type="auto">
  <name>Environment Setup</name>
  <files>requirements.txt</files>
  <action>
    Create a `requirements.txt` file with the necessary dependencies:
    - `requests`
    - `beautifulsoup4`
    - `lxml`
    
    Instruction: Provide the user with a command to create and activate a Python virtual environment and install these requirements.
  </action>
  <verify>test -f requirements.txt</verify>
  <done>requirements.txt exists with all 3 dependencies.</done>
</task>

<task type="auto">
  <name>Implement Scraper Script</name>
  <files>scraper.py</files>
  <action>
    Create `scraper.py` with the following logic:
    1. Send an HTTP GET request to `https://www.dolar-colombia.com/` with a standard User-Agent header.
    2. Parse the HTML using `BeautifulSoup`.
    3. Extract the TRM numeric value using the `span.exchange-rate` selector.
    4. Extract the date from the `value` attribute of `input.input-datepicker` (e.g., `2026-04-02`).
    5. Clean the numeric string (remove commas) and convert to a float.
    6. **Freshness Check**: Ensure the extracted date is valid for the current run period (reporting the date alongside the value).
    7. Print the results in a structured format (JSON or plain text).
  </action>
  <verify>python scraper.py</verify>
  <done>The script runs and prints a value like {"trm": 3675.81, "date": "2026-04-02"}.</done>
</task>

## Success Criteria
- [ ] `scraper.py` successfully connects to the website.
- [ ] The script accurately parses and extracts the TRM value.
- [ ] Output is formatted clearly for future integration with the WhatsApp API.
