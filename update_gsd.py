import json
from datetime import datetime

# Rewrite STATE.md completely
state_content = """# STATE.md - Project Memory

> **Current Milestone**: v1.1.0 — Financial Intelligence
> **Current Phase**: Phase 5 — Live Support & Stability (Hotfixes)
> **Status**: Paused at 2026-05-08T14:50:00-05:00

## Current Position
- **Milestone**: v1.1.0 — Financial Intelligence
- **Phase**: 3 (Next Up)
- **Task**: between tasks
- **Status**: Paused

## Last Session Summary
Diagnosed and fixed a critical delivery failure where messages were sent to the wrong chat. The broadcaster's text fallback search logic was removed because it was clicking previous messages instead of the group chat. Increased exact match timeouts. Deployed `v1.1.3`.

## In-Progress Work
- None

## Blockers
- None.

## Context Dump
### Decisions Made
- **(DEC-042) Strict Chat Matching**: Removed `get_by_text` fallback search. It's too dangerous because it can match past messages and send broadcasts to the wrong recipients. Increased exact match timeout to 8s instead.

### Files of Interest
- `broadcaster.py`: Search timeout and fallback logic.

## Next Steps
1. /plan 3 — Weekly Intelligence
"""

with open(".gsd/STATE.md", "w", encoding="utf-8") as f:
    f.write(state_content)

# Append to JOURNAL.md
journal_entry = """
---

## Session: 2026-05-08 14:00

### Objective
Diagnose and fix silent failure of messages not arriving in the WhatsApp group.

### Accomplished
- ✅ Analyzed `vm_run.log` and discovered message was sent to wrong chat due to Text Fallback search matching a previous message.
- ✅ Removed dangerous Text Fallback search logic in `broadcaster.py`.
- ✅ Increased exact match timeout to 8 seconds.
- ✅ Released `v1.1.3` and updated documentation.

### Verification
- [x] Tested search logic locally and pushed to VM.
- [x] VM successfully ran the fix and updated packages.

### Paused Because
Hotfix completed and deployed. Ready for next phase.

### Handoff Notes
Next up is Phase 3: Weekly Intelligence.
"""

with open(".gsd/JOURNAL.md", "a", encoding="utf-8") as f:
    f.write(journal_entry)

print("State and Journal updated.")
