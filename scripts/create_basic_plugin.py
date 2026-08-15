#!/usr/bin/env python3
"""Scaffold a native Cursor plugin and optionally a repository marketplace entry."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


MAX_NAME_LENGTH = 64
DEFAULT_PARENT = Path.home() / ".cursor" / "plugins" / "local"


def normalize_name(raw: str) -> str:
    name = re.sub(r"[^a-z0-9]+", "-", raw.strip().lower())
    return re.sub(r"-{2,}", "-", name).strip("-")


def validate_name(name: str) -> None:
    if not name:
        raise ValueError("Plugin name must contain at least one letter or digit.")
    if len(name) > MAX_NAME_LENGTH:
        raise ValueError(f"Plugin name exceeds {MAX_NAME_LENGTH} characters: {name}")
    if re.fullmatch(r"[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?", name) is None:
        raise ValueError(f"Invalid Cursor plugin name: {name}")


def display_name(name: str) -> str:
    return " ".join(part.capitalize() for part in re.split(r"[-.]", name))


def write_json(path: Path, payload: dict[str, Any], *, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"{path} already exists; use --force to replace it.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def ensure_empty_json(path: Path, payload: dict[str, Any], *, force: bool) -> None:
    if path.exists() and not force:
        return
    write_json(path, payload, force=force)


def build_manifest(name: str, args: argparse.Namespace) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "name": name,
        "displayName": display_name(name),
        "version": "0.1.0",
        "description": f"{display_name(name)} Cursor plugin",
        "author": {"name": "Local developer"},
    }
    component_paths = {
        "skills": (args.with_skills, "./skills/"),
        "rules": (args.with_rules, "./rules/"),
        "agents": (args.with_agents, "./agents/"),
        "commands": (args.with_commands, "./commands/"),
        "hooks": (args.with_hooks, "./hooks/hooks.json"),
        "mcpServers": (args.with_mcp, "./mcp.json"),
    }
    for key, (enabled, path) in component_paths.items():
        if enabled:
            manifest[key] = path
    return manifest


def update_marketplace(root: Path, plugin_name: str, plugin_root: Path, force: bool) -> Path:
    marketplace_path = root / ".cursor-plugin" / "marketplace.json"
    try:
        source = plugin_root.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError("Plugin path must be inside --marketplace-root.") from exc
    if not source or source == ".":
        raise ValueError("A marketplace plugin must be in a subdirectory of its marketplace root.")

    if marketplace_path.exists():
        payload = json.loads(marketplace_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError(f"{marketplace_path} must contain a JSON object.")
    else:
        payload = {
            "name": normalize_name(root.name) or "local-plugins",
            "owner": {"name": "Local developer"},
            "metadata": {"description": "Cursor plugin collection"},
            "plugins": [],
        }

    plugins = payload.setdefault("plugins", [])
    if not isinstance(plugins, list):
        raise ValueError("Marketplace field 'plugins' must be an array.")
    entry = {
        "name": plugin_name,
        "source": source,
        "description": f"{display_name(plugin_name)} Cursor plugin",
        "version": "0.1.0",
    }
    for index, existing in enumerate(plugins):
        if isinstance(existing, dict) and existing.get("name") == plugin_name:
            if not force:
                raise FileExistsError(
                    f"Marketplace entry '{plugin_name}' exists; use --force to replace it."
                )
            plugins[index] = entry
            break
    else:
        plugins.append(entry)
    write_json(marketplace_path, payload, force=True)
    return marketplace_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plugin_name")
    parser.add_argument(
        "--path",
        default=str(DEFAULT_PARENT),
        help="Parent directory; defaults to ~/.cursor/plugins/local",
    )
    parser.add_argument("--with-skills", action="store_true")
    parser.add_argument("--with-rules", action="store_true")
    parser.add_argument("--with-agents", action="store_true")
    parser.add_argument("--with-commands", action="store_true")
    parser.add_argument("--with-hooks", action="store_true")
    parser.add_argument("--with-scripts", action="store_true")
    parser.add_argument("--with-assets", action="store_true")
    parser.add_argument("--with-mcp", action="store_true")
    parser.add_argument(
        "--with-marketplace",
        action="store_true",
        help="Update <marketplace-root>/.cursor-plugin/marketplace.json",
    )
    parser.add_argument(
        "--marketplace-root",
        help="Repository root for --with-marketplace (required with that option)",
    )
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    name = normalize_name(args.plugin_name)
    if name != args.plugin_name:
        print(f"Normalized plugin name: {args.plugin_name!r} -> {name!r}")
    validate_name(name)
    if args.with_marketplace and not args.marketplace_root:
        raise ValueError("--with-marketplace requires --marketplace-root.")

    plugin_root = Path(args.path).expanduser().resolve() / name
    plugin_root.mkdir(parents=True, exist_ok=True)
    write_json(
        plugin_root / ".cursor-plugin" / "plugin.json",
        build_manifest(name, args),
        force=args.force,
    )

    directories = {
        "skills": args.with_skills,
        "rules": args.with_rules,
        "agents": args.with_agents,
        "commands": args.with_commands,
        "scripts": args.with_scripts,
        "assets": args.with_assets,
    }
    for directory, enabled in directories.items():
        if enabled:
            (plugin_root / directory).mkdir(parents=True, exist_ok=True)
    if args.with_hooks:
        ensure_empty_json(plugin_root / "hooks" / "hooks.json", {"hooks": {}}, force=args.force)
    if args.with_mcp:
        ensure_empty_json(plugin_root / "mcp.json", {"mcpServers": {}}, force=args.force)

    print(f"Created Cursor plugin: {plugin_root}")
    if args.with_marketplace:
        marketplace = update_marketplace(
            Path(args.marketplace_root).expanduser().resolve(), name, plugin_root, args.force
        )
        print(f"Updated Cursor marketplace: {marketplace}")


if __name__ == "__main__":
    main()
