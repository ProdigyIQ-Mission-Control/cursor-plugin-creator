---
name: plugin-creator
description: Create, scaffold, update, and validate native Cursor plugins with a required .cursor-plugin/plugin.json manifest, optional component folders, and repository marketplace entries. Use when creating a Cursor plugin, adding plugin components, preparing a plugin for local testing or marketplace submission, or updating an existing local Cursor plugin.
---

# Cursor Plugin Creator

Create native Cursor Plugins while preserving a safe scaffold-first workflow.

## Quick start

Run commands from this plugin's root (the directory containing `.cursor-plugin/plugin.json`).

```bash
python3 scripts/create_basic_plugin.py my-plugin
python3 scripts/validate_plugin.py ~/.cursor/plugins/local/my-plugin
```

Names are normalized to lowercase kebab-case, capped at 64 characters, and kept identical across the outer folder and manifest `name`. The default destination is `~/.cursor/plugins/local/<plugin-name>`, Cursor's local development plugin directory.

After creating or changing a local plugin, tell the user to restart Cursor or run `Developer: Reload Window`. Then verify it in **Customize → Plugins** and verify its individual skills under **Customize → Skills**.

## Add components

Only create components the request needs:

```bash
python3 scripts/create_basic_plugin.py my-plugin \
  --with-skills --with-rules --with-agents --with-commands \
  --with-hooks --with-scripts --with-assets --with-mcp
```

Supported generated locations:

- `skills/<skill-name>/SKILL.md`
- `rules/*.mdc`
- `agents/*.md`
- `commands/*.md`
- `hooks/hooks.json`
- `scripts/`
- `assets/`
- `mcp.json`

The scaffold creates empty component directories where a meaningful component cannot be inferred. It creates valid empty JSON objects for hooks and MCP so no fake behavior or placeholder secrets are introduced.

## Repository marketplace entries

Local personal plugins do not need a marketplace file. Use this only when the user explicitly wants a multi-plugin repository or team marketplace source:

```bash
python3 scripts/create_basic_plugin.py my-plugin \
  --path <repo-root>/plugins \
  --with-marketplace \
  --marketplace-root <repo-root>
```

This creates or updates `<repo-root>/.cursor-plugin/marketplace.json` and uses `plugins/<plugin-name>` as the entry source. New entries append in order. Use `--force` only to intentionally replace an existing plugin directory, manifest, or marketplace entry.

Do not invent a local personal marketplace registry: Cursor loads development plugins directly from `~/.cursor/plugins/local` and manages installed marketplace plugins through Customize.

## Required behavior

- Always create `.cursor-plugin/plugin.json`.
- Keep the plugin directory name and manifest `name` identical.
- Never leave unfinished placeholder markers in generated files.
- Use strict semantic versions.
- Include only valid relative component paths; never use `..` or absolute paths in a manifest.
- Keep component fields out of the manifest unless the corresponding files/directories exist.
- Never place secrets in a plugin. Use declared Cursor `variables` and `${VAR}` references when configuration is required.
- Preserve existing marketplace entries and ordering; append by default.
- Preserve existing marketplace metadata when updating it.
- Use `--force` only when replacement is explicitly intended.
- Do not edit Cursor's cache directory under `~/.cursor/plugins/cache`.
- Do not install into `~/.cursor/skills-cursor`; it is reserved for Cursor-managed built-in skills.
- Before handoff, run `python3 scripts/validate_plugin.py <plugin-path>`.

## Update flow

For a plugin already copied into `~/.cursor/plugins/local`:

1. Edit the source plugin, not Cursor's marketplace cache.
2. Run the validator.
3. Restart Cursor or run `Developer: Reload Window`.
4. Check **Customize → Plugins** and invoke a bundled skill as `/<skill-name>` in a new Agent chat.

Cursor does not require Codex-style cachebuster versions or personal `marketplace.json` edits for local development plugins.

Cursor 3.15.19 rejects a local-plugin symlink whose resolved target is outside `~/.cursor/plugins/local`. If the runtime log reports that rejection, install a real copy inside the trusted directory.

## Validation and handoff

Report:

- source files created or changed;
- installation path or symlink target;
- validation result;
- invocation (`/<skill-name>` or a natural-language request matching the skill description);
- any components that require user configuration or marketplace review.

For marketplace publication, the plugin must be hosted in a public Git repository and submitted through Cursor's marketplace publishing flow. Local discovery alone does not publish it.

See `references/cursor-plugin-format.md` for the component map and installation distinctions.
