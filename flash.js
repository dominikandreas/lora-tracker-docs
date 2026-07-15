(() => {
  const repository = 'dominikandreas/lora-tracker';
  const targets = [...document.querySelectorAll('.flash-target')];
  const installer = document.querySelector('#install-button');
  const activate = installer?.querySelector('[slot="activate"]');
  const selectedName = document.querySelector('#selected-name');
  const releaseStatus = document.querySelector('#release-status');
  let release = null;
  let manifestUrl = null;

  function select(targetButton) {
    targets.forEach((button) => {
      button.classList.toggle('selected', button === targetButton);
      button.setAttribute('aria-checked', button === targetButton ? 'true' : 'false');
    });
    selectedName.textContent = targetButton.querySelector('strong').textContent;
    if (!release) return;
    const target = targetButton.dataset.target;
    const asset = release.assets.find((item) =>
      item.name.startsWith(`lora-tracker-${target}-`) && item.name.endsWith('.factory.bin'));
    if (!asset) {
      releaseStatus.textContent = `Release ${release.tag_name} has no image for this target.`;
      activate.disabled = true;
      return;
    }
    if (manifestUrl) URL.revokeObjectURL(manifestUrl);
    const manifest = {
      name: `LoRa Tracker ${target}`,
      version: release.tag_name.replace(/^v/, ''),
      new_install_prompt_erase: true,
      new_install_improv_wait_time: 0,
      builds: [{ chipFamily: targetButton.dataset.chip, improv: false,
        parts: [{ path: asset.browser_download_url, offset: 0 }] }]
    };
    manifestUrl = URL.createObjectURL(new Blob([JSON.stringify(manifest)], { type: 'application/json' }));
    installer.manifest = manifestUrl;
    releaseStatus.textContent = `${release.tag_name} · ${targetButton.dataset.chip} · ${Math.ceil(asset.size / 1024)} KiB`;
    activate.disabled = false;
  }

  targets.forEach((button) => {
    button.setAttribute('role', 'radio');
    button.addEventListener('click', () => select(button));
  });
  fetch(`https://api.github.com/repos/${repository}/releases/latest`, {
    headers: { Accept: 'application/vnd.github+json' }
  }).then((response) => {
    if (!response.ok) throw new Error(`GitHub returned ${response.status}`);
    return response.json();
  }).then((latest) => {
    release = latest;
    select(document.querySelector('.flash-target.selected'));
  }).catch((error) => {
    releaseStatus.innerHTML = `No published firmware release is available yet. <a href="https://github.com/${repository}/actions/workflows/release.yml">View release builds</a>.`;
    activate.disabled = true;
    console.error(error);
  });
})();
