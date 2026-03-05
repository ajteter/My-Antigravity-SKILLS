---
name: skills-upgrade
description: "Batch-upgrade all installed Antigravity skills to their latest versions from the claude-plugins.dev registry. Use this skill whenever the user mentions upgrading skills, updating skills, refreshing skills, syncing skills to latest versions, checking for skill updates, or keeping skills up to date. Even if the user just says something like 'are my skills current?' or 'update everything', this skill is the right one to reach for."
---

# Skills Upgrade

Batch-upgrade all globally installed Antigravity skills by looking up each one in the [claude-plugins.dev](https://claude-plugins.dev) registry and reinstalling the latest version via `npx skills-installer`.

## When to Use

This skill is designed for a single, common scenario: the user wants to make sure all their installed skills are up to date. The upgrade script handles the entire flow — scanning, API lookup, and reinstallation — so there's no manual work involved.

## How to Use

Run the bundled script directly:

```bash
python <path-to-this-skill>/scripts/upgrade_skills.py
```

For example, if this skill is located at `/Users/you/projects/skills-upgrade`:

```bash
python /Users/you/projects/skills-upgrade/scripts/upgrade_skills.py
```

The script requires no additional dependencies beyond Python 3's standard library and `npx` (Node.js).

## What Happens Under the Hood

1. **Scan** — The script reads `~/.gemini/antigravity/skills/` and discovers all installed skill directories (ignoring hidden folders like `.DS_Store`).

2. **Lookup** — For each skill, it queries the `claude-plugins.dev` API to find the matching registry namespace. It converts hyphens to spaces for better search accuracy, prefers exact name matches, and falls back to partial matches ranked by star count.

3. **Reinstall** — Once a namespace is found, the script runs `npx -y skills-installer install <namespace> --client antigravity` to pull the latest version.

4. **Report** — Each skill gets a status line:
   - `[*] Found namespace: ...` — match found, upgrading
   - `[+] Upgrade complete` — success
   - `[!] Could not find matching registry entry` — no match, skipped
   - `[X] Failed to upgrade` — installer error, output shown

## Configuration

The default skills directory is `~/.gemini/antigravity/skills`. If your skills live elsewhere, edit the `SKILLS_DIR` constant at the top of `scripts/upgrade_skills.py`.

### Ignored Skills

The script maintains an `IGNORED_SKILLS` list (by default, it includes `skills-discovery` because it has heavily customized logic within the project). Skills in this list will be completely bypassed during the upgrade process to prevent their customizations from being overwritten by upstream versions.

## Troubleshooting

| Problem | Likely Cause | Fix |
|---|---|---|
| "Skills directory not found" | The default path doesn't exist | Create the directory or update `SKILLS_DIR` in the script |
| "Error checking API" | No network or SSL issue | Check your internet connection; the script disables strict SSL verification as a workaround |
| "Could not find matching registry entry" | Skill isn't published on claude-plugins.dev | This is expected for custom/private skills — they'll be skipped |
| "Failed to upgrade" | `npx` not installed or installer error | Make sure Node.js and npm are installed (`node -v`, `npm -v`) |
