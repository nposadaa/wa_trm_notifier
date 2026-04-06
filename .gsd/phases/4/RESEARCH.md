# Phase 4 Research: Cloud Deployment (Revised)

## Key Insight: headless=True May Work in Production

DEC-007 stated headless=False required. But that was for initial testing.
Research shows: **after session is established** with QR scan, `headless=True` + `playwright-stealth` can work for subsequent automated runs.

## Strategy: Try headless=True First

### Step 1: Local Test
- Change `headless=True` in broadcaster.py
- Run `py main.py` locally
- If message sends → headless works → GitHub Actions viable
- If blocked → fall back to Xvfb on VPS

### Why This Matters

| If headless=True works | If headless=True fails |
|----------------------|----------------------|
| GitHub Actions viable | Need VPS + Xvfb |
| Free (2000 min/mo) | Oracle Cloud (free) |
| Zero maintenance | Server maintenance |
| Session via GitHub Secret | Session on disk |

## Option A: GitHub Actions (if headless=True works)

Architecture:
```
GitHub Actions (cron 12:00 UTC = 7AM COT)
  |
  +-- Restore storageState from GitHub Secret
  +-- pip install + playwright install
  +-- python main.py (headless=True)
  +-- Save updated storageState back to artifact/secret
```

### Session Persistence Strategy
- Save `browserContext.storageState()` as JSON after each run
- Store as GitHub Actions artifact or encrypted secret
- Restore at start of each run
- Note: `launchPersistentContext` directory too large for secrets
  → Use `storageState` (cookies + localStorage only) instead

### Risks
- Different IP each run → WhatsApp may re-request QR
- Runner fingerprint differs from local → detection possible
- Session expiry unknown

## Option B: Oracle Cloud VPS (fallback)

Same as previous research — Xvfb + cron on Always Free VM.
Only needed if headless=True fails.

## Option C: Oracle Cloud VPS + headless=True (hybrid)

- VPS gives persistent filesystem + consistent IP
- headless=True means no Xvfb needed
- Simplest cloud option if headless works

## Recommendation

1. **Test headless=True locally first** (5 min)
2. If works → try **Option C** (VPS + headless, no Xvfb)
3. If fails → use **Option B** (VPS + Xvfb)
4. Option A (GitHub Actions) too risky due to IP rotation + ephemeral env
