# Cursor plugin format

## Manifest and discovery

A native Cursor Plugin has `.cursor-plugin/plugin.json` at its root. Cursor discovers conventional component locations automatically:

| Component | Default location |
|---|---|
| Skills | `skills/*/SKILL.md` |
| Rules | `rules/*.{md,mdc,markdown}` |
| Agents | `agents/*.{md,mdc,markdown}` |
| Commands | `commands/*.{md,mdc,markdown,txt}` |
| Hooks | `hooks/hooks.json` |
| MCP | `mcp.json` |

Manifest paths override default discovery for that component, so declare them only when useful and ensure the target exists.

## Local development

Place a plugin directory at:

```text
~/.cursor/plugins/local/<plugin-name>
```

Restart Cursor or run `Developer: Reload Window`, then inspect **Customize → Plugins**. Skills can be invoked manually with `/<skill-name>` from Agent chat.

Some Cursor builds permit development symlinks. Cursor 3.15.19 rejects a symlink when its resolved target is outside `~/.cursor/plugins/local`; use a real copy if the plugin log reports that trust-boundary rejection.

## Repository marketplace

A multi-plugin repository may contain `.cursor-plugin/marketplace.json` at the repository root. Each entry's `source` is relative to that root. This file is for repository/team distribution, not required for a personal local plugin.

## Publication limitation

Local installation is suitable for development and personal use. Public marketplace publication requires a public repository and Cursor review. Team marketplaces depend on the user's Cursor plan and organization controls.
