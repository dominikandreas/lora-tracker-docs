#!/usr/bin/env python3
"""Fail deployment when the two browser applications are not integrated."""

from __future__ import annotations

import sys
from pathlib import Path


root = Path(sys.argv[1])
required = [
    "index.html",
    "simulator.html",
    "app/index.html",
    "app/sw.js",
    "app/vendor/leaflet/leaflet.js",
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
if "lora-tracker-docs/simulator/" not in console_page:
    raise SystemExit("Tracker Console does not link back to the Network Lab")

print("Documentation site contains the integrated console and Network Lab")
