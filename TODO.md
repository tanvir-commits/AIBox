# Local AI Box — backlog

## Friend / beta testing (now)

- [ ] **Plain-language README block** — “What you need before you start” (no jargon: Docker = separate install, what `start.sh` does, what friends do on Mac vs Windows vs Linux).
- [ ] **Share pack for friends** — short message template + link to repo + `check_env.sh` + default login + “first upload then chat” steps; note change password if exposed beyond LAN.
- [x] **Prebuilt container images** — GHCR `ghcr.io/tanvir-commits/aibox-backend` + `aibox-web` (workflow `publish-images.yml`); default compose pulls; `--build` uses `docker-compose.dev.yml`.
- [ ] **Ship `PrivateAIBox.exe` on GitHub Releases** — attach to tagged release so friends skip installing Go.

## Packaging & distribution (easier than “install Docker yourself”)

- [ ] **Prerequisite checker** — done: `scripts/check_env.sh` (extend if needed).
- [ ] **Ubuntu server installer** (`scripts/install_ubuntu.sh`) — on an existing Ubuntu machine: install Docker, app, secrets, systemd; good for a friend who has a spare Linux box.
- [x] **Windows launcher** — `PrivateAIBox.exe` + `scripts/start-windows.bat` (Docker check, compose up, open browser); build via `scripts/build-windows-launcher.sh`.
- [ ] **Ship `PrivateAIBox.exe` on GitHub Releases** — attach to tagged release so friends skip installing Go.
- [ ] **VM appliance (often easier than USB)** — export a VirtualBox/VMware disk (`.ova` / `.vmdk`) with Ubuntu + Docker + stack preinstalled; friend downloads one file, opens in VirtualBox, no BIOS changes.
- [ ] **Bootable USB / live image** — see below (larger effort).
- [ ] **Release artifacts** — git tag, GitHub Release with checksums and one-page instructions.

### Bootable USB idea (download → flash on Windows → boot)

Goal: friend uses **Rufus** or **balenaEtcher** on Windows to flash a `.iso` or `.img`, boots PC from USB, PrivateAI Box is already there.

- [ ] **Decide USB model** — (A) *Live USB* (runs from stick, may be slow; persistence optional) vs (B) *installed system on USB* (persistent, behaves like a portable PC) vs (C) *installer ISO* that installs to internal disk (not what you want for “try only”).
- [ ] **Base image** — Ubuntu 24.04 LTS minimal + Docker + Compose + clone or bake app into image at build time.
- [ ] **First-boot wizard** — set admin password, show LAN URL (http://this-machine:3000), optional Wi‑Fi (hard on servers).
- [ ] **Build pipeline** — script to produce bootable `.iso` / raw `.img` (e.g. `scripts/build_usb_image.sh`); test in QEMU.
- [ ] **Flash instructions** — Windows: Rufus; Mac: balenaEtcher; warn about **Secure Boot**, **backup disk**, **8GB+ USB**, **16GB+ RAM** recommended.
- [ ] **Do not embed secrets** — generate JWT/admin password on first boot (per spec).
- [ ] **Docs: limitations** — Wi‑Fi drivers, laptop GPU, “will not run inside Windows at the same time without a VM”; reboot removes live session unless persistent partition.

## Post-MVP (product)

- [ ] **Multi-file upload** — `multiple` + optional folder pick; per-file progress/errors; avoid blocking the whole batch on one failure.
- [ ] **Async document ingest** — return after save; background parse/embed/index; live status in Documents table.
- [ ] Phase 5 remainder — Ollama model pull UI; optional Ollama embeddings; change default model without env-only workflow.
- [ ] Phase 6 — watched folders (scan, hash skip, reindex).

## MVP scope (current release)

Single-org, **Docker required**, `./scripts/start.sh --build` → sign in → upload → chat. See README **Share with friends**.
