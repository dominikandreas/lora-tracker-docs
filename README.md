# LoRa Tracker documentation

Static documentation site for [LoRa Tracker](https://github.com/dominikandreas/lora-tracker).

The site has no build-time dependencies. Open `index.html` locally or serve the
directory with any static HTTP server:

```bash
python3 -m http.server 8080
```

GitHub Actions publishes the `main` branch to GitHub Pages.

Pages cover getting started and secure provisioning, hardware selection,
browser-based ESP flashing, the Germany airtime/ERP profile, simulator/build
coverage, strict protocol contracts and current production readiness blockers. The detailed reference pages are
rendered from the authoritative Markdown in `dominikandreas/lora-tracker`; the
Pages workflow refreshes them on each deployment and every six hours.
