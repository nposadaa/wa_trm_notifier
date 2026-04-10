---
description: Update GSD from Nick's custom fork
---

# /update_nicks Workflow

<objective>
Update GSD for Antigravity from Nick's "NicksDev" fork, bringing in consolidated improvements and original GSD updates.
</objective>

<process>

## 1. Check Current Version

**PowerShell:**
```powershell
if (Test-Path "CHANGELOG.md") {
    $version = Select-String -Path "CHANGELOG.md" -Pattern "## \[(\d+\.\d+\.\d+)\]" | 
        Select-Object -First 1
    Write-Output "Current version: $($version.Matches.Groups[1].Value)"
}
```

---

## 2. Fetch Latest from Nick's Fork

```bash
# Clone latest to temp directory
git clone --depth 1 --recurse-submodules https://github.com/nposadaa/get-shit-done-for-antigravity_NicksDev .gsd-update-temp
```

---

## 3. Compare and Show Changes

The agent will extract the latest changes from the remote `CHANGELOG.md` and show them to the user.

---

## 4. Apply Consolidated Updates

This step brings in Nick's "golden master" code. Since improvements are already merged in the fork, we can safely overwrite.

**PowerShell:**
```powershell
# Backup sensitive areas
Copy-Item -Recurse ".agent" ".agent.backup"
Copy-Item -Recurse ".agents" ".agents.backup"

# Update workflows
Copy-Item -Recurse -Force ".gsd-update-temp/.agent/*" ".agent/"

# Update skills
Copy-Item -Recurse -Force ".gsd-update-temp/.agents/*" ".agents/"

# Update core files (The "Golden Master" rules)
Copy-Item -Force ".gsd-update-temp/PROJECT_RULES.md" "./"
Copy-Item -Force ".gsd-update-temp/GSD-STYLE.md" "./"
Copy-Item -Force ".gsd-update-temp/CHANGELOG.md" "./"
Copy-Item -Force ".gsd-update-temp/VERSION" "./"

# Update templates
if (Test-Path ".gsd-update-temp/.gsd/templates") {
    Copy-Item -Recurse -Force ".gsd-update-temp/.gsd/templates/*" ".gsd/templates/"
}
```

---

## 5. Cleanup

**PowerShell:**
```powershell
Remove-Item -Recurse -Force ".gsd-update-temp"
Remove-Item -Recurse -Force ".agent.backup"
Remove-Item -Recurse -Force ".agents.backup"
```

</process>

<preserved_files>
The following project-specific files are NEVER overwritten by /update_nicks:
- .gsd/SPEC.md
- .gsd/ROADMAP.md
- .gsd/STATE.md
- .gsd/ARCHITECTURE.md
- .gsd/STACK.md
- .gsd/DECISIONS.md
- .gsd/JOURNAL.md
- .gsd/TODO.md
- .gsd/phases/*
- .gemini/GEMINI.md
</preserved_files>
