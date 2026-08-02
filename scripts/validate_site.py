#!/usr/bin/env python3
"""Fail deployment when the two browser applications are not integrated."""

from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


class AssetReferenceParser(HTMLParser):
    """Collect scripts, stylesheets, manifests, and module preloads from HTML."""

    def __init__(self) -> None:
        super().__init__()
        self.references: list[str] = []
        self.links: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attributes = dict(attrs)
        if tag == "a" and attributes.get("href"):
            self.links.append(attributes["href"])
        elif tag == "script" and attributes.get("src"):
            self.references.append(attributes["src"])
        elif tag == "link" and attributes.get("rel") in {
            "manifest",
            "modulepreload",
            "stylesheet",
        }:
            if attributes.get("href"):
                self.references.append(attributes["href"])


root = Path(sys.argv[1])
required = [
    "index.html",
    "simulator.html",
    "app/index.html",
    "app/sw.js",
    "app/manifest.webmanifest",
    "app/lab/index.html",
    "app/lab/firmware-core.wasm",
    "simulator/index.html",
    "simulator/firmware-core.wasm",
    "simulator/simulation-engine.js",
]
missing = [relative for relative in required if not (root / relative).is_file()]
if missing:
    raise SystemExit(f"missing deployed site files: {', '.join(missing)}")

for page in root.glob("*.html"):
    if page.name == "404.html":
        continue
    if 'href="app/"' not in page.read_text(encoding="utf-8"):
        raise SystemExit(f"{page.name} has no Tracker Console navigation link")

simulator_page = (root / "simulator.html").read_text(encoding="utf-8")
if 'src="simulator/"' not in simulator_page:
    raise SystemExit("simulator.html does not embed the Network Lab")

console_page = (root / "app/index.html").read_text(encoding="utf-8")
parser = AssetReferenceParser()
parser.feed(console_page)
if not any(
    urlsplit(reference).path.rstrip("/") in {"lab", "./lab"}
    for reference in parser.links
):
    raise SystemExit("Tracker Console does not link to its bundled Network Lab")

local_assets = []
for reference in parser.references:
    parsed = urlsplit(reference)
    if parsed.scheme or parsed.netloc or parsed.path.startswith("/"):
        continue
    asset = (root / "app" / parsed.path).resolve()
    try:
        asset.relative_to(root.resolve())
    except ValueError:
        raise SystemExit(f"Tracker Console asset escapes the site root: {reference}")
    local_assets.append((reference, asset))

if not any(asset.suffix == ".js" for _, asset in local_assets):
    raise SystemExit("Tracker Console has no bundled JavaScript entry point")
if not any(asset.suffix == ".css" for _, asset in local_assets):
    raise SystemExit("Tracker Console has no bundled stylesheet")

missing_assets = [reference for reference, asset in local_assets if not asset.is_file()]
if missing_assets:
    raise SystemExit(
        "Tracker Console references missing build assets: " + ", ".join(missing_assets)
    )

print("Documentation site contains the integrated console and Network Lab")
