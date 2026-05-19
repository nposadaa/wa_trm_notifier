# Sprint 1 — Bugfix: Deep Clean Destroys IndexedDB

> **Duration**: 2026-05-19 to 2026-05-20
> **Status**: Todo

## Goal
Fix the self-healing deep clean logic so it preserves the modern WhatsApp Web encryption keys stored in `IndexedDB`, and restore the broken VM session via the Zip & Ship method.

## Analysis
The fallback 10:00 AM COT CRON job ran successfully but invalidated the WhatsApp session. 
- **Cause**: The `deep_clean_profile()` function deletes `IndexedDB` and `Service Worker` caches. Modern versions of WhatsApp Web have moved critical encryption key components into `IndexedDB` (not just `LocalStorage`).
- **Effect**: Deleting `IndexedDB` destroys the session, resulting in a fatal `Session Invalidated! (QR Required)` error.

## Scope

### Included
- Update `browser_config.py` to remove `IndexedDB` from the `deep_clean_profile()` deletion paths.
- Safely clear `.gsd/needs_maintenance` flag from the VM.
- Re-authenticate locally and transfer the session using the Zip & Ship method.

### Explicitly Excluded
- Refactoring the broader broadcaster logic.
- Phase 3 (Weekly Intelligence) features.

## Tasks

| Task | Assignee | Status | Est. Hours |
|------|----------|--------|------------|
| Update `browser_config.py` to preserve IndexedDB | Claude | ✅ Done | 0.5 |
| Clear `.gsd/needs_maintenance` flag on VM | User | ⬜ Todo | 0.1 |
| Re-authenticate and perform Zip & Ship | User / Claude | ⬜ Todo | 0.5 |

## Daily Log

### 2026-05-19
- Sprint created to address the May 19 broadcast failure. Log analysis confirmed `deep_clean_profile()` is destructive to modern WhatsApp sessions.
