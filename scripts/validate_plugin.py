#!/usr/bin/env python3
"""Validate a native Cursor plugin scaffold without third-party dependencies."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any


SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
NAME = re.compile(r"^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")
TODO = "[TODO:"
PATH_FIELDS = ("skills", "rules", "agents", "commands", "hooks", "mcpServers")


def load_object(path: Path, errors: list[str]) -> dict[str, Any] | None:
    if not path.is_file():
        errors.append(f"missing {path.name}: {path}")
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid JSON at {path}: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{path} must contain a JSON object")
        return None
    return value


def has_todo(value: Any) -> bool:
    if isinstance(value, str):
        return TODO in value
    if isinstance(value, list):
        return any(has_todo(item) for item in value)
    if isinstance(value, dict):
        return any(has_todo(item) for item in value.values())
    return False


def valid_relative_path(raw: str) -> bool:
    if not raw or Path(raw).is_absolute():
        return False
    path = PurePosixPath(raw.removeprefix("./"))
    return ".." not in path.parts and str(path) not in ("", ".")


def targets(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return value
    return []


def read_frontmatter(path: Path, errors: list[str]) -> dict[str, str] | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append(f"{path} is missing YAML frontmatter")
        return None
    closing = text.find("\n---", 4)
    if closing < 0:
        errors.append(f"{path} has unterminated YAML frontmatter")
        return None
    metadata: dict[str, str] = {}
    for line in text[4:closing].splitlines():
        if not line.strip() or line.startswith((" ", "\t")):
            continue
        key, separator, value = line.partition(":")
        if separator:
            metadata[key.strip()] = value.strip().strip("'\"")
    return metadata


def validate_skill(path: Path, errors: list[str]) -> None:
    metadata = read_frontmatter(path, errors)
    if metadata is None:
        return
    name = metadata.get("name", "")
    description = metadata.get("description", "")
    if not NAME.fullmatch(name):
        errors.append(f"{path}: invalid or missing skill name")
    if path.parent.name != name:
        errors.append(f"{path}: skill folder must match frontmatter name '{name}'")
    if not description:
        errors.append(f"{path}: missing skill description")
    if TODO in path.read_text(encoding="utf-8"):
        errors.append(f"{path}: contains a TODO placeholder")


def validate_plugin(root: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = root / ".cursor-plugin" / "plugin.json"
    manifest = load_object(manifest_path, errors)
    if manifest is None:
        return errors
    name = manifest.get("name")
    if not isinstance(name, str) or not NAME.fullmatch(name) or len(name) > 64:
        errors.append("manifest name must be lowercase kebab-case/dot-case and at most 64 characters")
    elif root.name != name:
        errors.append(f"plugin folder '{root.name}' must match manifest name '{name}'")
    version = manifest.get("version")
    if version is not None and (not isinstance(version, str) or not SEMVER.fullmatch(version)):
        errors.append("manifest version must use strict semantic versioning")
    if has_todo(manifest):
        errors.append("manifest contains a [TODO: ...] placeholder")
    for field in PATH_FIELDS:
        if field not in manifest:
            continue
        raw_targets = targets(manifest[field])
        if not raw_targets:
            errors.append(f"manifest field '{field}' must be a path or array of paths")
            continue
        for raw in raw_targets:
            if not valid_relative_path(raw):
                errors.append(f"manifest field '{field}' has unsafe path: {raw}")
                continue
            resolved = root / raw.removeprefix("./")
            if not resolved.exists():
                errors.append(f"manifest field '{field}' points to missing path: {raw}")
    for skill in sorted((root / "skills").glob("*/SKILL.md")) if (root / "skills").is_dir() else []:
        validate_skill(skill, errors)
    hooks = root / "hooks" / "hooks.json"
    if hooks.exists():
        payload = load_object(hooks, errors)
        if payload is not None and not isinstance(payload.get("hooks"), dict):
            errors.append("hooks/hooks.json must contain a 'hooks' object")
    mcp = root / "mcp.json"
    if mcp.exists():
        payload = load_object(mcp, errors)
        if payload is not None and not isinstance(payload.get("mcpServers"), dict):
            errors.append("mcp.json must contain an 'mcpServers' object")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plugin_path")
    return parser.parse_args()


def main() -> None:
    root = Path(parse_args().plugin_path).expanduser().resolve()
    errors = validate_plugin(root)
    if errors:
        print("Cursor plugin validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print(f"Cursor plugin validation passed: {root}")


if __name__ == "__main__":
    main()
