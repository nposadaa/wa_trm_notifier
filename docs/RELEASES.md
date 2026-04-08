# Release Management Guide

This document explains how to create versioned releases for the WhatsApp TRM Notifier.

## 1. Prepare Release
1. Update the `VERSION` file to the new version number (e.g., `1.1.0`).
2. Update `CHANGELOG.md` with all new features and bug fixes under a new heading.
3. Commit everything to the `master` branch and push to GitHub.

## 2. Tag the Release
We use Git tags to "freeze" the codebase at specific versions. Run these commands in your terminal:

```bash
# Optional: Ensure you have latest code locally
git pull origin master

# Create the tag locally (use annotated tag with -a and -m)
git tag -a v1.0.0-beta -m "Release v1.0.0-beta"

# Push the newly created tag to GitHub
git push origin v1.0.0-beta
```

## 3. Publish on GitHub
1. Navigate to your repository page on GitHub.
2. Click on **Releases** on the right side of the main page.
3. Click **Draft a new release**.
4. In the "Choose a tag" dropdown, select the tag you just pushed (`v1.0.0-beta`).
5. Title the release (e.g., `v1.0.0-beta: Cloud Stabilization`).
6. For the description, click **Generate release notes** to automatically list all commits, or copy-paste the specific section from your `CHANGELOG.md`.
7. You do not need to attach any binaries; GitHub automatically attaches `<branch>.zip` source code.
8. Click **Publish release**.
