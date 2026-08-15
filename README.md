# Plugin Creator for Cursor

A native Cursor Plugin that scaffolds and validates other Cursor plugins. It adapts the Codex `plugin-creator` workflow to Cursor's manifest, component discovery, local installation, and repository marketplace conventions.

Maintained by ProdigyIQ Mission Control.

## Use

In Cursor Agent chat, enter:

```text
/plugin-creator Create a plugin named release-helper with a skill and scripts folder.
```

Cursor may also select the skill automatically when asked to create or update a Cursor plugin.

## Local installation

Copy this directory to `~/.cursor/plugins/local/plugin-creator`, then restart Cursor or run `Developer: Reload Window`.

Cursor 3.15.19 rejects local-plugin symlinks whose targets resolve outside `~/.cursor/plugins/local`, even though the general Cursor documentation describes symlinks as a development option. Use a real copy when that trust-boundary check is active.

## Included tools

- `scripts/create_basic_plugin.py`: scaffold local or repository-hosted Cursor plugins
- `scripts/validate_plugin.py`: validate manifest, paths, component files, and marketplace linkage
