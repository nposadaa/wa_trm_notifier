---
phase: 5
plan: 2
wave: 1
---

# Plan 5.2: Data Source Migration & Hardening

## Objective
Migrate the TRM data source to the official SuperFinanciera Socrata API to eliminate staleness issues with the third-party site, update the broadcast message template accordingly, and fix the remaining delivery verification bug (BUG-007).

## Context
- scraper.py
- main.py
- broadcaster.py
- https://www.datos.gov.co/resource/mcec-87by.json

## Tasks

<task type="auto">
  <name>FEATURE: Scraper migration to Socrata API</name>
  <files>scraper.py, requirements.txt</files>
  <action>
    Refactor `scraper.py` to fetch TRM directly from the official SuperFinanciera Datos Abiertos API instead of `dolar-colombia.com`.
    
    Steps:
    1. Remove BeautifulSoup and lxml usage (and from requirements.txt if applicable).
    2. Change the target URL to: `https://www.datos.gov.co/resource/mcec-87by.json?$limit=1&$order=vigenciadesde DESC`.
    3. Query the URL using requests, parse the JSON payload array, and extract `valor` (as float) and `vigenciadesde` (formatted out safely as string YYYY-MM-DD).
  </action>
  <verify>
    Execute `python scraper.py` directly. It should print a valid JSON dictionary with `trm`, `date`, and `scraped_at`.
  </verify>
  <done>
    Scraper accurately retrieves official data via JSON API and BeautifulSoup is removed.
  </done>
</task>

<task type="auto">
  <name>FEATURE: Update message template</name>
  <files>main.py</files>
  <action>
    Update the text template generated in `main.py` to point to the correct source location.
    
    Steps:
    1. Identify the `message_text` construction logic in `main.py`.
    2. Change `Source www.dolar-colombia.com` to `Fuente: www.superfinanciera.gov.co`.
  </action>
  <verify>
    Confirm the output text string in `main.py` logs mentions the correct official URL.
  </verify>
  <done>
    Message template successfully reflects the new source URL.
  </done>
</task>

<task type="auto">
  <name>BUG-007: Fix delivery verification false negative</name>
  <files>broadcaster.py</files>
  <action>
    Update the empirical delivery verification to prevent false negatives.
    
    Steps:
    1. Improve the selector logic used in the `Verifying delivery` polling loop.
    2. Instead of polling `.last.is_visible(timeout=500)` rapidly, we can use `wait_for(state="attached")` and combine it with a robust check to see if the "Clock" (Outbox) icon has completely cleared.
  </action>
  <verify>
    Run a local dry-run broadcast to verify that a successful send correctly registers as `✅ SUCCESS` under load.
  </verify>
  <done>
    Delivery verification successfully detects checkmarks without throwing false negative timeouts.
  </done>
</task>

## Must-Haves
- [ ] Scraper fetches JSON directly from `datos.gov.co` (Socrata API).
- [ ] Message refers to `www.superfinanciera.gov.co`.
- [ ] Delivery verification wait logic is robust.

## Success Criteria
- [ ] All tasks verified passing locally.
- [ ] Changes pushed to VM and confirmed.
