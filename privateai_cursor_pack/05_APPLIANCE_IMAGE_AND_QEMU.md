# PrivateAI Box — Appliance Image and QEMU Plan

## 1. Goal

Build a bootable Ubuntu appliance image that can run PrivateAI Box on a PC.

Output:

```text
images/privateai-box.img
```

User can flash this to:

- USB SSD
- SATA SSD
- NVMe SSD
- internal drive

Then boot a PC and access:

```text
http://privateai.local
```

---

## 2. Important Terminology

Do not call this a custom distro.

Call it:

```text
PrivateAI Box Appliance Image
```

It is:

```text
Ubuntu Server LTS
+ PrivateAI services
+ first-boot setup wizard
+ appliance defaults
```

---

## 3. Image Contents

The image should include:

- Ubuntu Server LTS
- Docker
- Docker Compose
- NVIDIA Container Toolkit install logic
- nginx
- PrivateAI backend
- PrivateAI web
- Qdrant
- PostgreSQL
- Ollama config
- systemd service wrapper
- first-boot setup wizard
- backup/restore scripts
- factory reset script
- firewall defaults
- mDNS/hostname support for `privateai.local`

The image should NOT include:

- customer documents
- passwords
- private keys
- license secrets
- API keys

---

## 4. First-Boot Behavior

On first boot:

1. Generate secrets
2. Start minimal setup service
3. Start nginx
4. Expose setup wizard
5. Wait for admin setup
6. Save configuration
7. Start full PrivateAI stack

Setup URL:

```text
http://privateai.local/setup
```

Fallback:

```text
http://<box-ip>/setup
```

---

## 5. Build Approach

Preferred initial approach:

- scripted image build
- QEMU-compatible raw image
- cloud-init or firstboot service
- Docker images pulled during build or first boot

Script:

```bash
scripts/build_appliance_image.sh
```

Output:

```text
images/privateai-box.img
```

The build script should support:

```bash
./scripts/build_appliance_image.sh --dev
./scripts/build_appliance_image.sh --release
```

Dev mode:

- smaller image
- mock LLM
- no giant model downloads
- QEMU-friendly

Release mode:

- production defaults
- optional model pre-pull
- appliance branding

---

## 6. QEMU Boot Script

Create:

```bash
scripts/qemu_boot_image.sh
```

Example behavior:

```bash
./scripts/qemu_boot_image.sh images/privateai-box.img
```

Internally uses:

```bash
qemu-system-x86_64 \
  -m 8192 \
  -smp 4 \
  -drive file=images/privateai-box.img,format=raw \
  -net nic \
  -net user,hostfwd=tcp::8080-:80 \
  -nographic
```

Then user can open:

```text
http://localhost:8080
```

---

## 7. QEMU Test Script

Create:

```bash
scripts/qemu_test_image.sh
```

It should:

1. Launch image
2. Wait for boot
3. Poll `http://localhost:8080/health`
4. Run setup wizard using API or Playwright
5. Upload fixture document
6. Ask fixture question
7. Verify citation
8. Reboot VM
9. Verify data persisted
10. Shut down VM

---

## 8. Testing USB SSD Images

Eventually support testing a physical USB SSD from QEMU.

Warning:
Be very careful. Physical disk writes can destroy data.

The script must require explicit confirmation and disk path.

Example:

```bash
sudo ./scripts/flash_image_to_disk.sh images/privateai-box.img /dev/sdX
```

Before writing, print:

```text
WARNING: This will erase /dev/sdX completely.
Type ERASE /dev/sdX to continue:
```

Do not auto-detect and erase disks.

---

## 9. Real Hardware Validation

QEMU validates appliance behavior.

Real hardware validates:

- NVIDIA driver
- CUDA
- Docker GPU passthrough
- Ollama GPU
- thermals
- LAN discovery
- USB SSD boot quirks
- BIOS/UEFI behavior

Manual test:

```bash
nvidia-smi
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
curl http://localhost:11434/api/tags
```

---

## 10. Cursor Implementation Rules

Cursor should:

- create scripts with dry-run support
- make QEMU tests CPU-only
- avoid requiring GPU in image tests
- keep build scripts readable
- document every command
- fail loudly with useful errors
- never erase physical disks without explicit confirmation

---

## 11. Acceptance Criteria

Appliance image phase is complete when:

- image builds
- image boots in QEMU
- setup wizard appears
- services start
- health endpoint works
- data persists after reboot
- Playwright smoke test passes
- image can be flashed manually to USB SSD
- real PC boots image
