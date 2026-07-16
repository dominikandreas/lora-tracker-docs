#!/usr/bin/env python3
"""Render the reader-facing Markdown from lora-tracker into Pages HTML."""

from __future__ import annotations

import argparse
import re
from html import escape
from pathlib import Path

import markdown


PAGES = {
    "docs/ARCHITECTURE.md": ("Architecture", "reference/architecture.html"),
    "docs/BUILD_AND_DEPLOY.md": ("Build and deployment", "reference/build-and-deploy.html"),
    "docs/CONFIGURATION_REFERENCE.md": ("Configuration reference", "reference/configuration.html"),
    "docs/FLASHING.md": ("Flashing and recovery", "reference/flashing.html"),
    "docs/HARDWARE.md": ("Hardware", "reference/hardware.html"),
    "docs/ONBOARDING.md": ("Onboarding", "reference/onboarding.html"),
    "docs/OPERATIONS.md": ("Operations", "reference/operations.html"),
    "docs/PRODUCTION_READINESS.md": ("Production readiness", "reference/production-readiness.html"),
    "docs/REPEATERS.md": ("Repeaters", "reference/repeaters.html"),
    "docs/SIMULATION_COVERAGE.md": ("Simulation coverage", "reference/simulation-coverage.html"),
    "docs/protocols/CONFIGURATION.md": ("Configuration protocol", "reference/protocols/configuration.html"),
    "docs/protocols/LORA_PROTOCOL.md": ("LoRa protocol", "reference/protocols/lora-protocol.html"),
    "docs/protocols/MQTT_API.md": ("MQTT API", "reference/protocols/mqtt-api.html"),
    "docs/protocols/ONBOARDING_API.md": ("Onboarding API", "reference/protocols/onboarding-api.html"),
    "ROADMAP.md": ("Roadmap", "reference/roadmap.html"),
    "SECURITY.md": ("Security", "reference/security.html"),
}


def navigation(prefix: str) -> str:
    return f'''<header class="nav-wrap"><nav class="nav container" aria-label="Primary navigation">
  <a class="brand" href="{prefix}index.html"><span class="brand-mark">LT</span> LoRa Tracker</a>
  <button class="menu-button" aria-expanded="false" aria-controls="nav-links">Menu</button>
  <div id="nav-links" class="nav-links">
    <a href="{prefix}getting-started.html">Get started</a><a href="{prefix}hardware.html">Hardware</a>
    <a href="{prefix}repeater.html">Repeaters</a>
    <a href="{prefix}flash.html">Flash</a><a href="{prefix}simulator.html">Simulator</a>
    <a class="active" href="{prefix}protocols.html">Reference</a>
    <a class="source-link" href="https://github.com/dominikandreas/lora-tracker">Source ↗</a>
  </div></nav></header>'''


def relative_href(output: Path, target: str) -> str:
    relative = Path(target).relative_to("reference")
    return "../" * (len(output.parts) - 2) + str(relative)


def rewrite_links(html: str, source_file: Path, source_root: Path, output: Path) -> str:
    def replace(match: re.Match[str]) -> str:
        href = match.group(1)
        if not href.lower().endswith(".md") and ".md#" not in href.lower():
            return match.group(0)
        path_part, fragment = (href.split("#", 1) + [""])[:2]
        target = (source_file.parent / path_part).resolve()
        try:
            key = target.relative_to(source_root).as_posix()
        except ValueError:
            return match.group(0)
        if key not in PAGES:
            return match.group(0)
        rendered = relative_href(output, PAGES[key][1])
        return f'href="{rendered}{("#" + fragment) if fragment else ""}"'

    return re.sub(r'href="([^"]+)"', replace, html)


def render(source_root: Path, output_root: Path) -> None:
    for relative_source, (title, relative_output) in PAGES.items():
        source_file = source_root / relative_source
        if not source_file.is_file():
            raise SystemExit(f"missing source document: {source_file}")
        output = output_root / relative_output
        output.parent.mkdir(parents=True, exist_ok=True)
        body = markdown.markdown(
            source_file.read_text(encoding="utf-8"),
            extensions=["fenced_code", "tables", "toc", "sane_lists"],
            output_format="html5",
        )
        body = rewrite_links(body, source_file, source_root, Path(relative_output))
        prefix = "../" * (len(Path(relative_output).parts) - 1)
        output.write_text(
            f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{escape(title)} — LoRa Tracker documentation.">
<title>{escape(title)} — LoRa Tracker</title>
<link rel="stylesheet" href="{prefix}styles.css"><link rel="stylesheet" href="{prefix}extra.css"></head><body>
{navigation(prefix)}
<main class="docs container"><aside><p>REFERENCE</p><a href="{prefix}protocols.html">Reference overview</a><a href="{prefix}getting-started.html">Get started</a><a href="{prefix}production.html">Readiness</a></aside>
<article class="prose generated-doc"><p class="eyebrow">Source documentation</p>{body}</article></main>
<footer><div class="container"><span>LoRa Tracker documentation</span><a href="https://github.com/dominikandreas/lora-tracker">Source repository</a></div></footer>
<script src="{prefix}site.js"></script></body></html>''',
            encoding="utf-8",
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    render(args.source.resolve(), args.output.resolve())


if __name__ == "__main__":
    main()
